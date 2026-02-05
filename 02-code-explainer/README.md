# Project 02: Code Explainer CLI

**Difficulty:** Beginner+ | **Time:** 3-5 hours

## What You'll Build

A CLI tool that explains code files in plain English, with structured output.

```bash
$ python explainer.py auth.py

📄 auth.py (47 lines)

## Summary
A JWT authentication module that handles user login and token validation.

## Functions

┌─────────────────────────────────────────────────────────────┐
│ create_token(user_id: str) -> str                           │
├─────────────────────────────────────────────────────────────┤
│ Creates a JWT token for the given user.                     │
│ • Takes a user ID string                                    │
│ • Returns a signed JWT valid for 24 hours                   │
│ • Uses HS256 algorithm with SECRET_KEY                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ verify_token(token: str) -> dict | None                     │
├─────────────────────────────────────────────────────────────┤
│ Validates a JWT token and returns the payload.              │
│ • Returns the decoded payload if valid                      │
│ • Returns None if expired or invalid                        │
└─────────────────────────────────────────────────────────────┘

## Dependencies
• jwt (PyJWT library)
• datetime (standard library)
```

## Why This Project?

- **Structured outputs:** Learn to get JSON from LLMs (not just free text)
- **File handling:** Read and process code files
- **Prompt complexity:** Parse code structure, not just summarize
- **Portfolio value:** Shows you can build developer productivity tools

## Learning Objectives

1. **Structured outputs** - Get JSON responses from LLMs
2. **File I/O** - Read files, handle encodings, validate paths
3. **Complex prompting** - Extract specific information (functions, classes, deps)
4. **Output formatting** - Present information clearly in terminal

## Requirements

Build a CLI that:

- [ ] Takes a file path as argument
- [ ] Reads the file content
- [ ] Sends to LLM with a prompt requesting structured analysis
- [ ] Parses the JSON response
- [ ] Displays formatted output in terminal

### What to Extract

For each file, identify:
- **Summary:** 1-2 sentence overview
- **Functions/Methods:** Name, signature, brief description
- **Classes:** Name, purpose, key methods
- **Dependencies:** Imports and what they're used for
- **Complexity:** Simple/Medium/Complex rating

### Stretch Goals

- [ ] Support multiple files: `explainer.py src/*.py`
- [ ] Add `--format json` flag for raw JSON output
- [ ] Add `--depth shallow|deep` for detail level
- [ ] Syntax highlighting in output
- [ ] Cache explanations for unchanged files

## Getting Started

```bash
cd 02-code-explainer
source ../01-commit-msg-generator/venv/bin/activate  # reuse venv
pip install -r requirements.txt
```

## Hints

<details>
<summary>Hint 1: Reading a file safely</summary>

```python
from pathlib import Path

def read_file(filepath: str) -> str:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if not path.is_file():
        raise ValueError(f"Not a file: {filepath}")
    return path.read_text(encoding="utf-8")
```
</details>

<details>
<summary>Hint 2: Getting JSON output from Claude</summary>

```python
# Option 1: Ask nicely in prompt + parse
prompt = """Analyze this code and respond with ONLY valid JSON:
{
  "summary": "...",
  "functions": [...]
}
"""
response = client.messages.create(...)
data = json.loads(response.content[0].text)

# Option 2: Use response_format (if available)
# Check Anthropic docs for structured output features
```
</details>

<details>
<summary>Hint 3: Formatting output with boxes</summary>

```python
def print_box(title: str, content: list[str], width: int = 60):
    print("┌" + "─" * width + "┐")
    print("│ " + title.ljust(width - 1) + "│")
    print("├" + "─" * width + "┤")
    for line in content:
        print("│ " + line.ljust(width - 1) + "│")
    print("└" + "─" * width + "┘")
```
</details>

## Testing Your Solution

```bash
# Test on Project 01's code
python explainer.py ../01-commit-msg-generator/commit_gen.py

# Test on itself
python explainer.py explainer.py
```

## Done?

1. Ensure it handles edge cases (empty files, binary files, missing files)
2. Update CURRICULUM.md
3. Commit and push
4. Move to Project 03!
