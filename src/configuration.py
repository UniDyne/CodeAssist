
import os
import argparse
from pathlib import Path

from .constants import *
from .utils import load_json, load_list, load_text


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

    # project options take precedence
    options = load_options(config['project'])
    config.update(options)

    # merge non-command line params
    # from project-specific config
    config['ignore_patterns'] = load_ai_ignore(config['project'])
    config['langmap'] = load_langmap(config['project'])
    config['preprompt'] = load_preprompt_template(config['project'])


    sysprompt = load_sysprompt(config['project'])
    if sysprompt:
        config['sysprompt'] = sysprompt

    print_config(config)
    return config


def print_config(config):
    print("Ollama Configuration:")
    print(f"\tModel: {config['model']}")
    print(f"\tTemperature: {config['temperature']}")
    print(f"\tContext Size: {config['num_ctx']}")
    print("\n")




def load_options(project_path):
    path = os.path.join(project_path, OPTIONS_FILE)
    
    options = load_json(path)
    if options is None:
        return {}
    return options


def load_ai_ignore(project_path):
    patterns = set()
    path = os.path.join(project_path, AI_IGNORE_FILE)
    patterns = load_list(path)
    return patterns


def load_sysprompt(project_path):
    path = os.path.join(project_path, SYSPROMPT_FILE)
    return load_text(path)
    

def load_preprompt_template(project_path):
    default = "You are a senior software engineer. Below is the full source code of a project.\n"
    default += "Answer questions about the code and, if suggesting changes, output complete updated files.\n\n"

    path = os.path.join(project_path, PREPROMPT_FILE)
    preprompt = load_text(path)
    if preprompt not in {None, ""}:
        return preprompt
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
    loaded_map = load_json(path)
    if loaded_map is not None:
        default_map.update(loaded_map)
    
    return default_map
