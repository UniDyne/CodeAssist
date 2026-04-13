import os
import re
import shutil
import sys

from src.constants import *
from src.configuration import get_configuration
from src.sourcefiles import collect_source_files, save_files

from src.agent import Agent
from src.tools import Tool, get_tools


def build_preprompt(preprompt, files, langmap):
    preprompt += "\n\n# Project Files:\n\n"

    for rel_path, content in files:
        # Detect extension → fallback to text
        ext = os.path.splitext(rel_path)[1]
        lang = langmap.get(ext, "text")
        
        preprompt += f"\n## File: `{rel_path}`\n\n```{lang}\n{content}\n```\n"

    return preprompt





def main():
    
    # config from command line supercedes everything
    config = get_configuration()

    # get project-specific settings and merge


    print("Indexing project files...")
    files = collect_source_files(config['project'], config['ignore_patterns'])

    if not files:
        print("!!! No source files found (or all ignored).")
        return

    print(f"Loaded {len(files)} files")

    if config['enable_tools']:
        tools = get_tools(config)
        config['tools'] = tools

    agent = Agent(config)
    preprompt = build_preprompt(config['preprompt'], files, config['langmap'])
    agent.add_message('user', preprompt)

    while True:
        try:
            query = input("\nAsk about the code (or 'quit' to exit): ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() in ["clear", "reset"]:
            agent.clear()
            # add necessary messages back
            agent.add_message('system', config['sysprompt'])
            agent.add_message('user', preprompt)
            continue
        if query.lower() in ["quit", "exit", "q"]:
            break

        #full_prompt = preprompt + "\n\nUser question: " + query + "\n\nAnswer precisely. For code changes, use:\n=== FILE: relative/path/to/file ===\n```language\n[full file content]\n```"

        print(f"\nCalling Ollama...")
        agent.chat(query)
        
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
