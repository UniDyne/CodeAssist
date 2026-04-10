
#
# Models and Ollama
# These are defaults - can be changed from command line
# Other models to try:
# - qwen2.5-coder
# - qwen3-coder
# - qwen3-coder-next (very large...)
#
# For some reason, gpt-oss:20b does not work.
#
DEFAULT_MODEL = "deepseek-coder-v2"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_NUM_CTX = 8192


#
# CodeAssist Settings
#

IGNORE_DIRS = {".git", "venv", "node_modules", "__pycache__", ".idea", ".vscode", ".codeassist"}
IGNORE_EXTS = {".pyc", ".so", ".o", ".a", ".exe", ".dll", ".dylib", ".bin", ".dat"}

# Project-specific settings files
AI_IGNORE_FILE = ".ai_ignore"
OPTIONS_FILE = ".codeassist/options.json"
LANGUAGES_FILE = ".codeassist/languages.json"
PREPROMPT_FILE = ".codeassist/preprompt.md"


#
# Limitations
# These are hard-limits and are not configurable
#

MAX_FILES = 200  # Prevent huge prompts
MAX_CHARS_PER_FILE = 20_000  # Truncate long files


#
# Various flags
# These flags may be changed from command line
#

# by default, allow saving
ENABLE_SAVE = False
