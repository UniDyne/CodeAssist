# CodeAssist

CodeAssist is a tool that allows you to ask questions about your codebase and get answers from an LLM (Large Language Model) running locally via Ollama. It can also generate code changes based on your queries, which can be applied directly to your project files.

This is not designed to be a massive kitchen-sink type enterprise-grade assistant. This is for casual use and iterative improvement of small projects. That said, more features will be added over time.

## Features

- **Local LLM Usage**: Uses Ollama to run LLMs locally for privacy and performance.
- **Codebase Indexing**: Automatically indexes source files in your project, respecting `.gitignore`-like patterns.
- **Interactive Querying**: Ask questions about your codebase and get precise answers.
- **Code Generation**: Generate new code or modify existing files based on your queries.
- **Safe File Editing**: Optionally save changes to your project files with backup support.

## Limitations

- Up to 200 source files
- Up to 20K chars per file
- Otherwise limited by context size
- Does not use ChromaDB or any other RAG store.
- Full project source is loaded to prompt.


## Requirements

- Python 3.7+
- Ollama (https://ollama.com/)
- Required Python packages (install with `pip install -r requirements.txt`)

## Installation

1. Clone or download this repository.
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure Ollama is installed and running:
   ```bash
   ollama pull deepseek-coder-v2  # or another model of your choice
   ```

## Usage

Run the tool from the command line:

```bash
python -m codeassist
```

### Command Line Options

- `--project PATH`: Path to the project directory (default: current directory)
- `--model MODEL_NAME`: Ollama model name (default: `deepseek-coder-v2`)
- `--temperature FLOAT`: Model temperature (default: `0.2`)
- `--num-ctx INT`: Context window size (default: `8192`)
- `--enable-save`: Allow saving changes to project files (WARNING: This modifies your files)

### Example

```bash
python -m codeassist --project /path/to/my/project --model qwen2.5-coder --enable-save
```

### How It Works

1. The tool indexes all source files in the project directory, excluding common binary files and directories (like `.git`, `venv`, etc.).
2. You can ask questions about the codebase.
3. The LLM responds with answers and, if applicable, code changes in a specific format:
   ```
   === FILE: path/to/file ===
   ```language
   [full file content]
   ```
4. If `--enable-save` is used, the tool will apply the changes to your project files, creating a backup (`.orig`) of each modified file.

### Configuration Files

You can customize the behavior of CodeAssist using the following files in your project root:

- `.ai_ignore`: List of patterns to ignore when indexing files (similar to `.gitignore`)
- `.codeassist/preprompt.md`: Custom preprompt for the LLM
- `.codeassist/languages.json`: Custom language mappings for file extensions

Example `.ai_ignore`:
```
*.log
.env
build/
dist/
```

Example `.codeassist/languages.json`:
```json
{
  ".rs": "rust",
  ".go": "go"
}
```

## Security

- CodeAssist runs locally and does not send your code to any external servers.
- When using `--enable-save`, always review the changes before applying them. It's a good idea to use `git commit` before allowing AI-driven changes. That way, you can diff the source and rollback as needed.
- The tool creates backups of modified files (`.orig` extension).

## License

MIT
