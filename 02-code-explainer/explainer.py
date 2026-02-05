#!/usr/bin/env python3
"""
Code Explainer CLI - Project 02

A CLI tool that explains code files using structured LLM output.
"""

import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()

# Terminal formatting
BOLD = "\033[1m"
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def read_file(filepath: str) -> str:
    """
    Read a file and return its contents.

    Uses pathlib for modern file handling.
    Validates the file exists and is readable.
    """
    path = Path(filepath)

    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Check if it's a file (not a directory)
    if not path.is_file():
        raise ValueError(f"Not a file: {filepath}")

    # Read with explicit encoding
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise ValueError(f"Cannot read file (binary or unknown encoding): {filepath}")


def analyze_code(code: str, filename: str) -> dict:
    """
    Send code to Claude and get structured analysis.

    Uses a carefully crafted prompt to get JSON output
    with specific fields we need for display.
    """
    client = anthropic.Anthropic()

    # The prompt requests specific JSON structure
    prompt = f"""Analyze this code file and respond with ONLY valid JSON (no other text).

Use exactly this structure:
{{
  "summary": "1-2 sentence overview of what this code does",
  "functions": [
    {{
      "name": "function_name",
      "signature": "function_name(arg1: type, arg2: type) -> return_type",
      "description": "What the function does",
      "key_points": ["point 1", "point 2"]
    }}
  ],
  "classes": [
    {{
      "name": "ClassName",
      "description": "What the class represents",
      "methods": ["method1", "method2"]
    }}
  ],
  "dependencies": [
    {{
      "name": "module_name",
      "purpose": "What it's used for in this code"
    }}
  ],
  "complexity": "simple | medium | complex"
}}

Rules:
- If there are no functions, use empty array: "functions": []
- If there are no classes, use empty array: "classes": []
- Only include actual imports in dependencies
- Complexity: simple (<50 lines, straightforward), medium (50-200 lines or some complexity), complex (>200 lines or advanced patterns)

Filename: {filename}

Code:
```
{code}
```

Respond with ONLY the JSON object. No markdown, no explanation."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()

    # Try to extract JSON if model added extra text
    if not response_text.startswith("{"):
        # Look for JSON block
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start != -1 and end > start:
            response_text = response_text[start:end]

    return json.loads(response_text)


def print_header(filename: str, line_count: int):
    """Print the file header."""
    print(f"\n{BOLD}📄 {filename}{RESET} ({line_count} lines)\n")


def print_summary(summary: str):
    """Print the summary section."""
    print(f"{BOLD}## Summary{RESET}")
    print(summary)
    print()


def print_box(title: str, content: list[str], width: int = 62):
    """Print content in a unicode box."""
    # Top border
    print("┌" + "─" * width + "┐")

    # Title line
    title_display = title[:width-2] if len(title) > width-2 else title
    print("│ " + f"{CYAN}{title_display}{RESET}".ljust(width + len(CYAN) + len(RESET) - 1) + "│")

    # Separator
    print("├" + "─" * width + "┤")

    # Content lines
    for line in content:
        # Handle lines longer than box width
        display_line = line[:width-2] if len(line) > width-2 else line
        print("│ " + display_line.ljust(width - 1) + "│")

    # Bottom border
    print("└" + "─" * width + "┘")


def print_functions(functions: list):
    """Print functions in formatted boxes."""
    for func in functions:
        name = func.get("name", "unknown")
        signature = func.get("signature", name)
        description = func.get("description", "No description")
        key_points = func.get("key_points", [])

        content = [description]
        for point in key_points:
            content.append(f"• {point}")

        print_box(signature, content)
        print()


def print_classes(classes: list):
    """Print classes in formatted boxes."""
    for cls in classes:
        name = cls.get("name", "unknown")
        description = cls.get("description", "No description")
        methods = cls.get("methods", [])

        content = [description]
        if methods:
            content.append("")
            content.append("Methods:")
            for method in methods:
                content.append(f"  • {method}")

        print_box(f"class {name}", content)
        print()


def print_dependencies(dependencies: list):
    """Print the dependencies section."""
    if not dependencies:
        return

    print(f"{BOLD}## Dependencies{RESET}")
    for dep in dependencies:
        name = dep.get("name", "unknown")
        purpose = dep.get("purpose", "")
        print(f"• {CYAN}{name}{RESET}: {purpose}")
    print()


def print_complexity(complexity: str):
    """Print the complexity rating with color."""
    colors = {
        "simple": GREEN,
        "medium": YELLOW,
        "complex": RED
    }
    color = colors.get(complexity.lower(), RESET)
    print(f"{BOLD}## Complexity:{RESET} {color}{complexity.title()}{RESET}\n")


def main():
    """Main entry point - orchestrates the flow."""

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print(f"{RED}Error: ANTHROPIC_API_KEY not set.{RESET}")
        print("Set it in your .env file or environment.")
        sys.exit(1)

    # Check command line arguments
    if len(sys.argv) < 2:
        print(f"{BOLD}Code Explainer{RESET} - Explain any code file\n")
        print("Usage: python explainer.py <file>")
        print("Example: python explainer.py main.py")
        sys.exit(1)

    filepath = sys.argv[1]

    # Read the file
    try:
        code = read_file(filepath)
    except FileNotFoundError as e:
        print(f"{RED}Error: {e}{RESET}")
        sys.exit(1)
    except ValueError as e:
        print(f"{RED}Error: {e}{RESET}")
        sys.exit(1)

    # Check for empty file
    if not code.strip():
        print(f"{YELLOW}Warning: File is empty.{RESET}")
        sys.exit(0)

    # Get the analysis
    print("Analyzing code...")
    try:
        analysis = analyze_code(code, Path(filepath).name)
    except anthropic.APIError as e:
        print(f"{RED}API Error: {e}{RESET}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"{RED}Failed to parse response as JSON: {e}{RESET}")
        print("The model may not have returned valid JSON.")
        sys.exit(1)

    # Display the results
    print_header(Path(filepath).name, len(code.splitlines()))
    print_summary(analysis.get("summary", "No summary available."))

    functions = analysis.get("functions", [])
    if functions:
        print(f"{BOLD}## Functions{RESET}\n")
        print_functions(functions)

    classes = analysis.get("classes", [])
    if classes:
        print(f"{BOLD}## Classes{RESET}\n")
        print_classes(classes)

    print_dependencies(analysis.get("dependencies", []))
    print_complexity(analysis.get("complexity", "unknown"))


if __name__ == "__main__":
    main()
