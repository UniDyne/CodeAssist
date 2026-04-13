import ollama

from .tools import execute_tool

class Agent:
    def __init__(self, config):
        self.client = ollama.Client()
        self.messages = []
        self.model = config['model']
        self.temperature = config['temperature']
        self.num_ctx = config['num_ctx']

        if 'tools' in config.keys():
            self.tools = {tool.name: tool for tool in config['tools']}
        else:
            self.tools = {}
        
        if 'sysprompt' in config.keys():
            self.messages.append({"role":"system", "content": config['sysprompt']})
    
    def add_message(self, role, content):
        self.messages.append({"role":role, "content": content})

    def chat(self, prompt):
        self.messages.append({"role":"user", "content":prompt})

        # Loop in order to catch tool calls
        while(True):
            response = self.client.chat(
                model=self.model,
                messages=self.messages,
                tools=[tool.to_dict() for tool in self.tools.values()],
                options={
                    'temperature': self.temperature,
                    'num_ctx': self.num_ctx
                }
            )

            print(response)

            message = response.get('message',{})
            self.messages.append(message)

            content = message.get('content', '')
            if content:
                print(content)
                # old file replacement code would go here
            
            # The content might be pure JSON for a tool call...
            # need to add a fix here for qwen2.5-coder (json tool call)
            # and for qwen3-coder (xml tool call)

            tool_calls = message.get('tool_calls', [])
            if not tool_calls:
                break
            for tool_call in tool_calls:
                
                function = tool_call.get('function',{})
                tool_name = funciton.get('name', '')
                arguments = function.get('arguments', {})

                print(f"Calling tool {tool_name}...")

                if tool_name in self.tools:
                    tool = self.tools[tool_name]
                    result = execute_tool(tool, arguments)
                    self.messages.append({"role":"tool", "content": result})
                else:
                    self.messages.append({"role":"tool", "content": f"Unknown tool {tool_name}"})


    def clear(self):
        self.messages = []


"""
    OLD CODE BELOW
"""

def parse_llm_response(response_text: str):
    # Extract files from various formats:
    # 1. === FILE: path/to/file ===
    # 2. ## File: path/to/file
    # 3. File: path/to/file
    # 4. With or without backticks around the path
    # 5. With various whitespace and formatting
    
    # Pattern 1: === FILE: ... === blocks
    pattern1 = r"===\s*FILE:\s*(.+?)\s*===\s*\n+```(?:\w+)?\s*\n(.*?)\n*```\s*"
    
    # Pattern 2: ## File: ... blocks (more flexible)
    pattern2 = r"##\s*File:\s*`?([^`\n]+)`?\s*\n+```(?:\w+)?\s*\n(.*?)\n*```\s*"
    
    # Pattern 3: File: ... blocks (generic)
    pattern3 = r"(?<!#)\bFile:\s*`?([^`\n]+)`?\s*\n+```(?:\w+)?\s*\n(.*?)\n*```\s*"
    
    matches = []
    
    # Try pattern 1 first (most specific)
    for match in re.finditer(pattern1, response_text, re.DOTALL | re.MULTILINE):
        path = match.group(1).strip()
        # Remove backticks from path if present
        path = path.strip("`").strip()
        content = match.group(2)
        matches.append((path, content))
    
    # Try pattern 2 (## File: format)
    for match in re.finditer(pattern2, response_text, re.DOTALL | re.MULTILINE):
        path = match.group(1).strip()
        # Remove backticks from path if present
        path = path.strip("`").strip()
        content = match.group(2)
        # Avoid duplicates
        if not any(m[0] == path for m in matches):
            matches.append((path, content))
    
    # Try pattern 3 (generic File: format)
    for match in re.finditer(pattern3, response_text, re.DOTALL | re.MULTILINE):
        path = match.group(1).strip()
        # Remove backticks from path if present
        path = path.strip("`").strip()
        content = match.group(2)
        # Avoid duplicates
        if not any(m[0] == path for m in matches):
            matches.append((path, content))
    
    return matches

def call_ollama(prompt, config):
    # !!TODO
    # tools should probably get added to the config...
    # and then turned on/off based on settings...
    # getting tools here for now
    if 'tools' in config.keys():
        tools = [tool.to_dict() for tool in config['tools']]
    else:
        tools = None

    messages = []
    if 'sysprompt' in config.keys():
        messages.append({"role":"system", "content": config['sysprompt']})
    messages.append({"role":"user", "content": prompt})

    response = ollama.chat(
        model=config['model'],
        messages=messages,
        tools=tools,
        options={
            "temperature": config['temperature'],
            "num_ctx": config['num_ctx']
        }
    )
    
    return response["message"]["content"]