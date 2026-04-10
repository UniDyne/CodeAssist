
import os
import argparse
import json
from pathlib import Path

from .constants import *


"""
Command Line Arguments:
    --project PATH
    --temperature FLOAT
    --num-ctx INT
    --model MODEL_NAME
"""

def get_configuration():
    parser = argparse.ArgumentParser(
        description="Coding Assistant",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--project", default=os.getcwd(), metavar="PATH", help="Path to project.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model name")
    parser.add_argument("--temperature", type=float,
                        default=float(os.getenv("OLLAMA_TEMPERATURE", DEFAULT_TEMPERATURE)),
                        help="Model temperature")
    parser.add_argument("--num-ctx", type=int,
                        default=int(os.getenv("OLLAMA_NUM_CTX", DEFAULT_NUM_CTX)),
                        help="Context window size")
    
    parser.add_argument("--enable-save", action="store_true", help="Allow saving changes to project files. (WARNING)")

    args = parser.parse_args()
    
    config = {
        'project': args.project,
        'model': args.model,
        'temperature': args.temperature,
        'num_ctx': args.num_ctx,
        'enable_save': hasattr(args, 'enable_save')
    }

    # merge non-command line params
    # from project-specific config
    config['ignore_patterns'] = load_ai_ignore(config['project'])
    config['langmap'] = load_langmap(config['project'])
    config['preprompt'] = load_preprompt_template(config['project'])

    return config


def load_ai_ignore(project_path):
    patterns = set()
    path = os.path.join(project_path, AI_IGNORE_FILE)
    if os.path.isfile(path):
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.add(line)

    return patterns


def load_preprompt_template(project_path):
    default = "You are a senior software engineer. Below is the full source code of a project.\n"
    default += "Answer questions about the code and, if suggesting changes, output complete updated files.\n\n"

    try:
        path = os.path.join(project_path, PREPROMPT_FILE)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception as e:
        print(f"!!! Could not load {PREPROMPT_FILE}: {e}")
    
    return default


def load_langmap(project_path):
    """ load language mappings"""
    default_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".h": "cpp",
        ".c": "c",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".sql": "sql",
        ".sh": "bash",
        ".yaml": "yaml",
        ".json": "json",
        ".md": "markdown",
    }

    path = os.path.join(project_path, LANGUAGES_FILE)
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded_map = json.load(f)
                # merge with defaults
                default_map.update(loaded_map)
        except (json.JSONDecodeError, IOError) as e:
            print(f"!! Failed to load {LANGUAGES_FILE}: {e}. Using defaults.")
    
    return default_map