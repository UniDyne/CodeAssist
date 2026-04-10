import os

from .constants import *
from .utils import load_text


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
            
            content = load_text(full_path)
            if content:
                files.append((rel_path, content[:MAX_CHARS_PER_FILE]))
                if len(files) >= MAX_FILES:
                    break

        if len(files) >= MAX_FILES:
            break

    return files[:MAX_FILES]


def save_files(project_path, new_files):
    for rel_path, content in new_files:
        full_path = os.path.join(project_path, rel_path)

        # Create backup
        if os.path.exists(full_path):
            shutil.copy(full_path, full_path + ".orig")

        # Ensure parent dirs exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   Updated: {rel_path}")
