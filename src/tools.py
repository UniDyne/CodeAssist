import os
import shutil
from typing import Any

from .utils import *

class Tool:
    """Tools for agent use. Must describe tool and how to call it."""
    def __init__(self, name: str, description: str, parameters: dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters
    
    def execute(self, **kwargs) -> str:
        """Base class - no implementation."""
        raise NotImplementedError
    
    def to_dict(self) -> dict[str, Any]:
        """Dictionary to hand off to LLM."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class ListDirectory(Tool):
    def __init__(self, config):
        super().__init__(
            name="list_dir",
            description="List contents of a directory.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to directory to list. Defaults to project base directory."
                    }
                },
                "required": []
            }
        )
        self.basepath = config['project']
    
    def execute(self, path: str) -> str:
        try:
            full_path = os.path.join(self.basepath, path)
            if not os.path.exists(full_path):
                return f"Error: Path not found: {path}"
            if not os.path.isdir(full_path):
                return f"Error: Path is not a directory: {path}"
            
            items = []
            with os.scandir(full_path) as it:
                for entry in it:
                    if not entry.name.startswith('.'):
                        if entry.is_file():
                            items.append(f"FILE: {entry.name}")
                        elif entry.is_dir():
                            items.append(f"DIR: {entry.name}")
            return "\n".join(items) if items else "Directory is empty."
        except Exception as e:
            return f"Error listing directory: {e}"


class FileReader(Tool):
    def __init__(self, config):
        super().__init__(
            name="read_file",
            description="Read complete contents of file.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file to read."
                    }
                },
                "required": ["path"]
            }
        )
        self.basepath = config['project']
    
    def execute(self, path: str) -> str:
        full_path = os.path.join(self.basepath, path)
        if not os.path.exists(full_path):
            return f"Error: File not found: {path}"
        return load_text(full_path)

class FileWriter(Tool):
    def __init__(self, config):
        super().__init__(
            name="write_file",
            description="Write complete contents of file.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of file to write."
                    },
                    "content": {
                        "type": "string",
                        "description": "The complete contents of the file to write."
                    }
                },
                "required": ["path", "content"]
            }
        )
        self.basepath = config['project']
    
    def execute(self, path: str, content: str) -> str:
        full_path = os.path.join(self.basepath, path)

        # create backup
        if os.path.exists(full_path):
            shutil.copy(full_path, full_path + ".orig")
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Success: File written: {rel_path}"

def get_tools(config) -> list[Tool]:
    return [
        FileReader(config),
        FileWriter(config),
        ListDirectory(config)
    ]

def execute_tool(tool: Tool, arguments: dict[str, Any]) -> str:
    try:
        return tool.execute(**arguments)
    except TypeError as e:
        return f"Error: Invalid arguments for tool {tool.name}: {e}"
    except Exception as e:
        return f"Error: Unable to execute tool {tool.name}: {e}"

