# Project 03: README Generator

**Difficulty:** Beginner+ | **Time:** 3-5 hours

## What You'll Build

A CLI tool that analyzes a project directory and generates a professional README.md.

```bash
$ python readme_gen.py /path/to/project

Analyzing project...
Found: 12 Python files, 3 config files, 1 existing README

Generated README.md:

# MyProject

A FastAPI-based REST API for managing user authentication and sessions.

## Features
- JWT-based authentication
- Session management with Redis
- Rate limiting middleware
...

Save to /path/to/project/README.md? [y/n]:
```

## Why This Project?

- **Multi-file analysis:** Process entire directories, not just single files
- **Template generation:** Create structured markdown from code
- **Real utility:** Every project needs a README - this saves hours
- **Portfolio gold:** Shows you can build practical developer tools

## Learning Objectives

1. **Directory traversal** - Walk through project files with pathlib
2. **File filtering** - Skip binaries, node_modules, .git, etc.
3. **Context aggregation** - Combine info from multiple files
4. **Markdown generation** - Output well-formatted documentation
5. **Template patterns** - Structure complex outputs

## Requirements

Build a CLI that:

- [ ] Takes a directory path as argument
- [ ] Scans for relevant files (code, configs, existing docs)
- [ ] Identifies project type (Python, Node, Go, etc.)
- [ ] Extracts key information:
  - Project name and description
  - Main features/functionality
  - Installation steps
  - Usage examples
  - Dependencies
- [ ] Generates well-structured README.md
- [ ] Optionally saves to file

### What to Detect

| File | Information |
|------|-------------|
| `pyproject.toml` / `package.json` | Name, description, dependencies |
| `requirements.txt` | Python dependencies |
| `*.py` / `*.js` / `*.go` | Main functionality, exports |
| `Dockerfile` | Containerization info |
| `.env.example` | Required environment variables |
| Existing `README.md` | Current documentation to enhance |

### Stretch Goals

- [ ] Multiple output formats: `--format markdown|rst|html`
- [ ] Update mode: enhance existing README instead of replacing
- [ ] Badge generation (build status, version, license)
- [ ] Auto-detect license type
- [ ] Generate from git history (recent changes section)

## Getting Started

```bash
cd 03-readme-generator
source ../01-commit-msg-generator/venv/bin/activate
pip install -r requirements.txt
```

## Hints

<details>
<summary>Hint 1: Walking a directory</summary>

```python
from pathlib import Path

def get_project_files(directory: str) -> list[Path]:
    root = Path(directory)
    files = []

    # Directories to skip
    skip_dirs = {'.git', 'node_modules', 'venv', '__pycache__', '.venv'}

    for path in root.rglob('*'):
        # Skip if in excluded directory
        if any(skip in path.parts for skip in skip_dirs):
            continue
        if path.is_file():
            files.append(path)

    return files
```
</details>

<details>
<summary>Hint 2: Detecting project type</summary>

```python
def detect_project_type(files: list[Path]) -> str:
    filenames = {f.name for f in files}

    if 'pyproject.toml' in filenames or 'setup.py' in filenames:
        return 'python'
    elif 'package.json' in filenames:
        return 'node'
    elif 'go.mod' in filenames:
        return 'go'
    elif 'Cargo.toml' in filenames:
        return 'rust'
    else:
        return 'unknown'
```
</details>

<details>
<summary>Hint 3: Chunking large contexts</summary>

```python
# If project is too large for one API call, prioritize key files
PRIORITY_FILES = [
    'README.md', 'pyproject.toml', 'package.json',
    'main.py', 'app.py', 'index.js', 'main.go'
]

def get_priority_content(files: list[Path], max_chars: int = 50000) -> str:
    content = []
    total = 0

    # Sort by priority
    sorted_files = sorted(files, key=lambda f:
        PRIORITY_FILES.index(f.name) if f.name in PRIORITY_FILES else 999
    )

    for f in sorted_files:
        text = f.read_text()
        if total + len(text) > max_chars:
            break
        content.append(f"## {f.name}\n```\n{text}\n```")
        total += len(text)

    return "\n\n".join(content)
```
</details>

## Testing Your Solution

```bash
# Test on this portfolio
python readme_gen.py /home/claudeuser/ai-engineering-portfolio

# Test on a real project
python readme_gen.py /path/to/any/project
```

## Done?

1. Test on multiple project types
2. Update CURRICULUM.md
3. Commit and push
4. Move to Project 04!
