import os
import re
import shutil
import sys

import ollama

from src.constants import *
from src.configuration import get_configuration


def should_ignore(rel_path: str, ignore_patterns):
    parts = rel_path.split(os.sep)
    if any(part.startswith(".") and part != "." for part in parts):
        return True
    if any(part in IGNORE_DIRS for part in parts):
        return True
    if any(rel_path.endswith(ext) for ext in IGNORE_EXTS):
        return True

    # Apply .ai_ignore patterns (simple fnmatch-style)
    for pattern in ignore_patterns:
        if pattern in rel_path or rel_path.startswith(pattern):
            return True
    return False


def collect_source_files(project_path, ignore_patterns):
    files = []

    for root, dirs, filenames in os.walk(project_path):
        # Prune ignored dirs in-place
        dirs[:] = [d for d in dirs if not should_ignore(os.path.relpath(os.path.join(root, d), project_path), ignore_patterns)]

        for fname in filenames:
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, project_path)

            if should_ignore(rel_path, ignore_patterns):
                continue

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if content.strip():
                    files.append((rel_path, content[:MAX_CHARS_PER_FILE]))
                    if len(files) >= MAX_FILES:
                        break
            except Exception:
                pass  # Skip binary or unreadable files

        if len(files) >= MAX_FILES:
            break

    return files[:MAX_FILES]


def build_preprompt(preprompt, files, langmap):
    preprompt += "\n\n# Project Files:\n\n"

    for rel_path, content in files:
        # Detect extension → fallback to text
        ext = os.path.splitext(rel_path)[1]
        lang = langmap.get(ext, "text")
        
        preprompt += f"\n## File: `{rel_path}`\n\n```{lang}\n{content}\n```\n"

    return preprompt



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


def save_files(new_files):
    for rel_path, content in new_files:
        full_path = os.path.join(PROJECT_DIR, rel_path)

        # Create backup
        if os.path.exists(full_path):
            shutil.copy(full_path, full_path + ".orig")

        # Ensure parent dirs exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   Updated: {rel_path}")


def call_ollama(prompt, config):
    response = ollama.chat(
        model=config['model'],
        messages=[
            {"role": "user", "content": prompt}
        ],
        options={
            "temperature": config['temperature'],
            "num_ctx": config['num_ctx']
        }
    )
    
    return response["message"]["content"]


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

    while True:
        preprompt = build_preprompt(config['preprompt'], files, config['langmap'])
        try:
            query = input("\nAsk about the code (or 'quit' to exit): ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() in ["quit", "exit", "q"]:
            break

        full_prompt = preprompt + "\n\nUser question: " + query + "\n\nAnswer precisely. For code changes, use:\n=== FILE: relative/path/to/file ===\n```language\n[full file content]\n```"

        print(f"\nCalling Ollama...")
        response = call_ollama(full_prompt, config)
        
        if not response:
            print("!!! Failed to get LLM response.")
            continue

        print("\nLLM response:\n" + response)

        # Try parsing file replacements
        new_files = parse_llm_response(response)
        if new_files:
            print(f"Detected {len(new_files)} file changes from LLM:")
        
            for path, _ in new_files:
                print(f"  - {path}")
            if config['enable_save']:
                save_files(new_files)
                print("\nChanges saved.")
                # need to update files collection

    print("\nGoodbye!")


if __name__ == "__main__":
    main()
