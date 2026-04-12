import os
import json

def load_json(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except(json.JSONDecodeError, IOError) as e:
        print(f"!! Failed to load {path}: {e}.")
        return None


def load_list(path):
    listing = set()
    if not os.path.isfile(path):
        return listing
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    listing.add(line)
    except IOError as e:
        print(f"!! Failed to load {path}: {e}.")
    
    return listing

def load_text(path):
    if not os.path.isfile(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except (UnicodeDecodeError, IOError) as e:
        print(f"!! Failed to load {path}: {e}.")
        return ""
