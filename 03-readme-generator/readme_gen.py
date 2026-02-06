#!/usr/bin/env python3
"""
README Generator - Project 03

A CLI tool that analyzes a project directory and generates a README.md.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()

# Terminal formatting
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Directories to skip when scanning
SKIP_DIRS = {
    '.git', 'node_modules', 'venv', '.venv', '__pycache__',
    '.pytest_cache', '.mypy_cache', 'dist', 'build', '.eggs',
    'egg-info', '.tox', 'htmlcov', '.coverage'
}

# File extensions to include
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java',
    '.rb', '.php', '.c', '.cpp', '.h', '.hpp', '.cs', '.swift'
}

CONFIG_FILES = {
    'pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt',
    'package.json', 'package-lock.json', 'tsconfig.json',
    'go.mod', 'go.sum', 'Cargo.toml', 'Cargo.lock',
    'Makefile', 'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
    '.env.example', '.env.sample', 'config.yaml', 'config.yml',
    'README.md', 'README.rst', 'README.txt', 'LICENSE', 'CHANGELOG.md'
}

# Priority files to read first (most informative)
PRIORITY_FILES = [
    'README.md', 'pyproject.toml', 'package.json', 'Cargo.toml', 'go.mod',
    'setup.py', 'requirements.txt', 'main.py', 'app.py', 'index.js',
    'index.ts', 'main.go', 'lib.rs', 'main.rs', 'Dockerfile'
]


def get_project_files(directory: str) -> list[Path]:
    """
    Scan directory for relevant project files.

    Skips common non-essential directories like node_modules, .git, etc.
    Returns only files that are likely to be informative.
    """
    root = Path(directory).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not root.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    files = []

    for path in root.rglob('*'):
        # Skip excluded directories
        if any(skip_dir in path.parts for skip_dir in SKIP_DIRS):
            continue

        if not path.is_file():
            continue

        # Include config files by name
        if path.name in CONFIG_FILES:
            files.append(path)
            continue

        # Include code files by extension
        if path.suffix.lower() in CODE_EXTENSIONS:
            files.append(path)
            continue

    return files


def detect_project_type(files: list[Path]) -> str:
    """Detect the primary language/framework of the project."""
    filenames = {f.name for f in files}
    extensions = {f.suffix.lower() for f in files}

    # Check by config files first (most reliable)
    if 'pyproject.toml' in filenames or 'setup.py' in filenames or 'requirements.txt' in filenames:
        return 'Python'
    elif 'package.json' in filenames:
        if any(f.suffix in {'.ts', '.tsx'} for f in files):
            return 'TypeScript/Node.js'
        return 'JavaScript/Node.js'
    elif 'go.mod' in filenames:
        return 'Go'
    elif 'Cargo.toml' in filenames:
        return 'Rust'
    elif 'pom.xml' in filenames or 'build.gradle' in filenames:
        return 'Java'

    # Fallback to extension counting
    ext_counts = {}
    for f in files:
        ext = f.suffix.lower()
        if ext in CODE_EXTENSIONS:
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

    if ext_counts:
        dominant = max(ext_counts, key=ext_counts.get)
        ext_to_lang = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.go': 'Go', '.rs': 'Rust', '.java': 'Java', '.rb': 'Ruby',
            '.php': 'PHP', '.c': 'C', '.cpp': 'C++', '.cs': 'C#'
        }
        return ext_to_lang.get(dominant, 'Unknown')

    return 'Unknown'


def collect_file_content(files: list[Path], root: Path, max_chars: int = 80000) -> str:
    """
    Collect content from files, prioritizing important ones.

    Respects a character budget to avoid context overflow.
    """
    # Sort by priority
    def priority_key(f: Path) -> int:
        if f.name in PRIORITY_FILES:
            return PRIORITY_FILES.index(f.name)
        return 1000

    sorted_files = sorted(files, key=priority_key)

    content_parts = []
    total_chars = 0
    files_included = 0

    for file_path in sorted_files:
        try:
            text = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, PermissionError):
            continue  # Skip binary or unreadable files

        # Calculate relative path for display
        try:
            relative = file_path.relative_to(root)
        except ValueError:
            relative = file_path.name

        file_content = f"### {relative}\n```\n{text}\n```"

        if total_chars + len(file_content) > max_chars:
            # If we haven't included any files yet, truncate this one
            if files_included == 0:
                remaining = max_chars - total_chars - 100
                truncated = text[:remaining] + "\n[TRUNCATED]"
                file_content = f"### {relative}\n```\n{truncated}\n```"
                content_parts.append(file_content)
                files_included += 1
            break

        content_parts.append(file_content)
        total_chars += len(file_content)
        files_included += 1

    return "\n\n".join(content_parts)


def generate_readme(project_path: str, files: list[Path], project_type: str, content: str) -> str:
    """Generate README using Claude."""
    client = anthropic.Anthropic()

    project_name = Path(project_path).name
    file_list = "\n".join(f"- {f.name}" for f in files[:30])
    if len(files) > 30:
        file_list += f"\n- ... and {len(files) - 30} more files"

    prompt = f"""Analyze this project and generate a professional README.md file.

Project name: {project_name}
Project type: {project_type}
Total files: {len(files)}

Key files:
{file_list}

File contents:
{content}

Generate a README.md with these sections (skip any that don't apply):

1. **Title and Description** - Project name as H1, one-paragraph description
2. **Features** - Bullet list of main features/capabilities
3. **Installation** - How to install/set up (based on project type)
4. **Usage** - Basic usage examples with code blocks
5. **Configuration** - Environment variables or config options if any
6. **API Reference** - If it's a library/API, document main functions
7. **Contributing** - Brief contribution guidelines
8. **License** - If detectable from files

Rules:
- Be accurate - only include what's evident from the code
- Use proper markdown formatting
- Include realistic code examples based on actual code
- Don't make up features that aren't in the code
- Keep it concise but complete

Output ONLY the README content in markdown format. No commentary."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def print_summary(files: list[Path], project_type: str):
    """Print a summary of what was found."""
    # Count by type
    code_files = [f for f in files if f.suffix in CODE_EXTENSIONS]
    config_files = [f for f in files if f.name in CONFIG_FILES]

    print(f"\n{BOLD}Project Analysis{RESET}")
    print(f"├── Type: {CYAN}{project_type}{RESET}")
    print(f"├── Code files: {len(code_files)}")
    print(f"├── Config files: {len(config_files)}")
    print(f"└── Total files: {len(files)}")
    print()


def main():
    """Main entry point."""

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print(f"{YELLOW}Error: ANTHROPIC_API_KEY not set.{RESET}")
        sys.exit(1)

    # Check arguments
    if len(sys.argv) < 2:
        print(f"{BOLD}README Generator{RESET} - Generate README.md for any project\n")
        print("Usage: python readme_gen.py <directory>")
        print("Example: python readme_gen.py /path/to/my/project")
        sys.exit(1)

    project_path = sys.argv[1]

    # Scan project
    print(f"Scanning {CYAN}{project_path}{RESET}...")
    try:
        files = get_project_files(project_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"{YELLOW}Error: {e}{RESET}")
        sys.exit(1)

    if not files:
        print(f"{YELLOW}No relevant files found in directory.{RESET}")
        sys.exit(1)

    # Detect project type
    project_type = detect_project_type(files)
    print_summary(files, project_type)

    # Collect content
    print("Reading files...")
    root = Path(project_path).resolve()
    content = collect_file_content(files, root)

    # Generate README
    print("Generating README...")
    try:
        readme = generate_readme(project_path, files, project_type, content)
    except anthropic.APIError as e:
        print(f"{YELLOW}API Error: {e}{RESET}")
        sys.exit(1)

    # Display result
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{GREEN}Generated README.md:{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")
    print(readme)
    print(f"\n{BOLD}{'='*60}{RESET}\n")

    # Ask to save
    readme_path = Path(project_path) / "README.md"
    existing = " (will overwrite existing)" if readme_path.exists() else ""

    save = input(f"Save to {readme_path}{existing}? [y/n]: ").lower().strip()

    if save == 'y':
        readme_path.write_text(readme, encoding='utf-8')
        print(f"{GREEN}Saved to {readme_path}{RESET}")
    else:
        print("Not saved.")


if __name__ == "__main__":
    main()
