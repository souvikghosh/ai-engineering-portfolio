# Key Concepts - Project 03

## 1. Directory Traversal with pathlib

### Basic Iteration
```python
from pathlib import Path

root = Path("/my/project")

# List immediate children
for item in root.iterdir():
    print(item)  # /my/project/file.py, /my/project/src, etc.

# Recursive - all files in all subdirectories
for item in root.rglob("*"):
    print(item)  # Includes nested files
```

### Glob Patterns
```python
# All Python files
root.rglob("*.py")

# All files named 'main' with any extension
root.rglob("main.*")

# All files in 'src' directory
root.glob("src/*")
```

### Filtering
```python
# Only files (not directories)
files = [p for p in root.rglob("*") if p.is_file()]

# Only certain extensions
python_files = list(root.rglob("*.py"))

# Skip certain directories
skip = {'.git', 'node_modules', '__pycache__'}
files = [
    p for p in root.rglob("*")
    if p.is_file() and not any(s in p.parts for s in skip)
]
```

## 2. Working with Multiple Files

### The Challenge
LLMs have context limits. A large project might have hundreds of files totaling millions of characters. You can't send everything.

### Strategies

**1. Priority-based selection:**
```python
# Most important files first
priority = ['README.md', 'pyproject.toml', 'main.py', 'app.py']

sorted_files = sorted(files, key=lambda f:
    priority.index(f.name) if f.name in priority else 999
)
```

**2. Truncation with budget:**
```python
def collect_content(files, max_chars=50000):
    content = []
    total = 0

    for f in files:
        text = f.read_text()
        if total + len(text) > max_chars:
            # Could also truncate instead of skip
            continue
        content.append((f.name, text))
        total += len(text)

    return content
```

**3. Summarize first, detail later:**
- First pass: Get file names and sizes only
- Ask LLM which files are most relevant
- Second pass: Read only those files in detail

## 3. Project Type Detection

Different project types have different conventions:

| Type | Indicators | Key Files |
|------|------------|-----------|
| Python | pyproject.toml, setup.py, requirements.txt | main.py, app.py, __init__.py |
| Node.js | package.json, package-lock.json | index.js, server.js |
| Go | go.mod, go.sum | main.go |
| Rust | Cargo.toml | main.rs, lib.rs |
| Java | pom.xml, build.gradle | Main.java |

```python
def detect_type(filenames: set[str]) -> str:
    indicators = {
        'python': {'pyproject.toml', 'setup.py', 'requirements.txt'},
        'node': {'package.json'},
        'go': {'go.mod'},
        'rust': {'Cargo.toml'},
    }

    for project_type, files in indicators.items():
        if files & filenames:  # Set intersection
            return project_type

    return 'unknown'
```

## 4. Markdown Generation

### Structure
A good README follows a pattern:

```markdown
# Project Name

One-line description.

## Features
- Feature 1
- Feature 2

## Installation
```bash
pip install myproject
```

## Usage
```python
from myproject import main
main()
```

## Configuration
Environment variables...

## License
MIT
```

### In Python
```python
def generate_readme(data: dict) -> str:
    sections = []

    sections.append(f"# {data['name']}\n\n{data['description']}")

    if data.get('features'):
        features = "\n".join(f"- {f}" for f in data['features'])
        sections.append(f"## Features\n\n{features}")

    if data.get('installation'):
        sections.append(f"## Installation\n\n```bash\n{data['installation']}\n```")

    return "\n\n".join(sections)
```

## 5. Token/Character Limits

Claude's context window has limits. Be strategic:

| Model | Context Window |
|-------|---------------|
| claude-sonnet-4-20250514 | 200K tokens (~150K words) |
| claude-opus-4-5-20251101 | 200K tokens |

### Estimating Tokens
- Rough estimate: 1 token ≈ 4 characters
- 50,000 characters ≈ 12,500 tokens

```python
def estimate_tokens(text: str) -> int:
    return len(text) // 4  # Rough estimate
```

### Staying Under Limits
```python
MAX_CONTEXT_CHARS = 100000  # Leave room for prompt + response

def truncate_content(files_content: str) -> str:
    if len(files_content) > MAX_CONTEXT_CHARS:
        return files_content[:MAX_CONTEXT_CHARS] + "\n\n[TRUNCATED]"
    return files_content
```

## Resources

- [pathlib documentation](https://docs.python.org/3/library/pathlib.html)
- [Markdown Guide](https://www.markdownguide.org/)
- [Anthropic Token Counting](https://docs.anthropic.com/en/docs/build-with-claude/token-counting)
