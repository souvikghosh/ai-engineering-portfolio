# Key Concepts - Project 02

## 1. Structured Outputs from LLMs

LLMs naturally output free-form text. But often you need **structured data** you can parse.

### The Problem
```python
response = "Here's the analysis:\n\nThis code has 3 functions..."
# How do you extract the function names programmatically? Messy regex? 😬
```

### The Solution: Ask for JSON
```python
prompt = """Analyze this code. Respond with ONLY this JSON structure:
{
  "summary": "string",
  "functions": [
    {"name": "string", "description": "string"}
  ]
}

Code:
```python
{code}
```"""
```

### Parsing the Response
```python
import json

response_text = message.content[0].text
data = json.loads(response_text)  # Convert JSON string to Python dict

print(data["summary"])  # Access like a dictionary
for func in data["functions"]:
    print(func["name"])
```

### What Can Go Wrong
1. Model adds extra text: "Here's the JSON:\n{...}"
2. Model uses wrong format: single quotes instead of double
3. Model hallucinates fields

**Tip:** Be explicit: "Respond with ONLY valid JSON. No other text."

## 2. File I/O with pathlib

Python's `pathlib` is the modern way to handle files:

```python
from pathlib import Path

# Create a Path object
file = Path("src/main.py")

# Check existence
file.exists()      # True/False
file.is_file()     # True if it's a file (not directory)
file.is_dir()      # True if it's a directory

# Read content
content = file.read_text(encoding="utf-8")

# Get info
file.name          # "main.py"
file.suffix        # ".py"
file.stem          # "main"
file.parent        # Path("src")

# Combine paths
folder = Path("src")
new_file = folder / "utils.py"  # Path("src/utils.py")
```

### Why `encoding="utf-8"`?

```python
# Without encoding, Python uses system default (might not be UTF-8)
content = file.read_text()  # Might fail on special characters

# Always specify UTF-8 for code files
content = file.read_text(encoding="utf-8")  # Safe
```

## 3. Command-Line Arguments

Get the filename from command line:

```python
import sys

# sys.argv is a list: ["script.py", "arg1", "arg2", ...]
if len(sys.argv) < 2:
    print("Usage: python explainer.py <file>")
    sys.exit(1)

filepath = sys.argv[1]
```

### For More Complex Args, Use argparse

```python
import argparse

parser = argparse.ArgumentParser(description="Explain code files")
parser.add_argument("file", help="Path to the code file")
parser.add_argument("--format", choices=["text", "json"], default="text")
parser.add_argument("--depth", choices=["shallow", "deep"], default="shallow")

args = parser.parse_args()

print(args.file)    # The file path
print(args.format)  # "text" or "json"
```

## 4. Error Handling Best Practices

```python
def read_file(filepath: str) -> str:
    path = Path(filepath)

    # Check before trying (LBYL - Look Before You Leap)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Or handle when it fails (EAFP - Easier to Ask Forgiveness)
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise ValueError(f"Cannot read file (not text?): {filepath}")
```

**Which to use?**
- File existence → Check first (LBYL)
- Encoding issues → Try/except (EAFP)
- Network/API calls → Always try/except (EAFP)

## 5. Terminal Formatting

Make output pretty without external libraries:

```python
# Colors (ANSI escape codes)
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

print(f"{GREEN}Success!{RESET}")
print(f"{BOLD}Title{RESET}")

# Box drawing characters
print("┌────────────┐")
print("│  Content   │")
print("└────────────┘")
```

## Resources

- [Anthropic: Structured Outputs](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Python pathlib docs](https://docs.python.org/3/library/pathlib.html)
- [Python argparse tutorial](https://docs.python.org/3/howto/argparse.html)
