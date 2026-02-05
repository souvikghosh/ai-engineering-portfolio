#!/usr/bin/env python3
"""
Commit Message Generator - Project 01

A CLI tool that generates commit messages from staged git changes.
"""

import subprocess
import sys
import os
from dotenv import load_dotenv
import anthropic

# Load environment variables from .env file
load_dotenv()


def get_staged_diff() -> str:
    """
    Get the diff of staged changes.

    Uses subprocess to run 'git diff --cached' which shows
    only the changes that have been staged with 'git add'.
    """
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True
    )
    return result.stdout


def generate_commit_message(diff: str) -> str:
    """
    Generate a commit message using Claude.

    Sends the diff to the API with a carefully crafted prompt
    that instructs the model on how to write good commit messages.
    """
    # Create the Anthropic client (uses ANTHROPIC_API_KEY env var automatically)
    client = anthropic.Anthropic()

    # The prompt is crucial - it tells the model exactly what we want
    prompt = f"""You are a commit message generator. Analyze the following git diff and write a clear, professional commit message.

Rules:
1. First line: imperative mood, max 50 characters (e.g., "Add user authentication")
2. Leave a blank line after the first line
3. Then add bullet points explaining the key changes
4. Focus on WHAT changed and WHY, not HOW
5. Be concise but informative

Git diff:
```
{diff}
```

Write only the commit message, nothing else."""

    # Make the API call
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the text from the response
    return message.content[0].text


def prompt_user(message: str) -> str:
    """
    Show the generated message and get user's decision.

    Returns:
        'y' to accept as-is
        'n' to reject/cancel
        The edited message if user chooses to edit
    """
    print("\n" + "=" * 50)
    print("Generated commit message:")
    print("=" * 50)
    print(message)
    print("=" * 50 + "\n")

    while True:
        choice = input("[y]es to accept / [n]o to cancel / [e]dit: ").lower().strip()

        if choice == 'y':
            return 'y'
        elif choice == 'n':
            return 'n'
        elif choice == 'e':
            print("\nEnter your edited message (type END on a new line when done):")
            lines = []
            while True:
                line = input()
                if line == "END":
                    break
                lines.append(line)
            return "\n".join(lines)
        else:
            print("Invalid choice. Please enter 'y', 'n', or 'e'.")


def create_commit(message: str) -> bool:
    """
    Create a git commit with the given message.

    Uses subprocess to run 'git commit' with the message.
    Returns True if the commit succeeded (exit code 0).
    """
    result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True,
        text=True
    )

    # Print any output from git
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    # Return True if exit code is 0 (success)
    return result.returncode == 0


def main():
    """Main entry point - orchestrates the whole flow."""

    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set.")
        print("Copy .env.example to .env and add your API key.")
        sys.exit(1)

    # Step 1: Get staged changes
    diff = get_staged_diff()

    if not diff:
        print("No staged changes found. Stage some changes with 'git add' first.")
        sys.exit(1)

    print(f"Found {len(diff.splitlines())} lines of diff...")

    # Step 2: Generate commit message
    print("Generating commit message...")
    try:
        message = generate_commit_message(diff)
    except anthropic.APIError as e:
        print(f"API error: {e}")
        sys.exit(1)

    if not message:
        print("Failed to generate commit message.")
        sys.exit(1)

    # Step 3: Get user confirmation
    result = prompt_user(message)

    if result == 'n':
        print("Commit cancelled.")
        sys.exit(0)

    # Use original message if 'y', or the edited version
    final_message = message if result == 'y' else result

    # Step 4: Create commit
    if create_commit(final_message):
        print("Commit created successfully!")
    else:
        print("Failed to create commit.")
        sys.exit(1)


if __name__ == "__main__":
    main()
