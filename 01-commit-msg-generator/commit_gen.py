#!/usr/bin/env python3
"""
Commit Message Generator - Project 01

A CLI tool that generates commit messages from staged git changes.

Your task: Implement the functions below to complete the tool.
"""

import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_staged_diff() -> str:
    """
    Get the diff of staged changes.

    Returns:
        The git diff output as a string, or empty string if no changes.

    TODO: Implement this function
    - Use subprocess to run: git diff --cached
    - Return the stdout
    """
    pass


def generate_commit_message(diff: str) -> str:
    """
    Generate a commit message using an LLM.

    Args:
        diff: The git diff to analyze

    Returns:
        A generated commit message

    TODO: Implement this function
    - Create an Anthropic client (or OpenAI)
    - Write a good prompt that explains what you want
    - Send the diff to the API
    - Return the generated message
    """
    pass


def prompt_user(message: str) -> str:
    """
    Show the message and ask user what to do.

    Args:
        message: The generated commit message

    Returns:
        'y' to accept, 'n' to reject, or the edited message

    TODO: Implement this function
    - Print the generated message
    - Ask user: [y]es / [n]o / [e]dit
    - Handle each option appropriately
    """
    pass


def create_commit(message: str) -> bool:
    """
    Create a git commit with the given message.

    Args:
        message: The commit message to use

    Returns:
        True if commit succeeded, False otherwise

    TODO: Implement this function
    - Use subprocess to run: git commit -m "message"
    - Return True if successful
    """
    pass


def main():
    """Main entry point."""
    # Step 1: Get staged changes
    diff = get_staged_diff()

    if not diff:
        print("No staged changes found. Stage some changes with 'git add' first.")
        sys.exit(1)

    # Step 2: Generate commit message
    print("Generating commit message...")
    message = generate_commit_message(diff)

    if not message:
        print("Failed to generate commit message.")
        sys.exit(1)

    # Step 3: Get user confirmation
    result = prompt_user(message)

    if result == 'n':
        print("Commit cancelled.")
        sys.exit(0)

    final_message = message if result == 'y' else result

    # Step 4: Create commit
    if create_commit(final_message):
        print("Commit created successfully!")
    else:
        print("Failed to create commit.")
        sys.exit(1)


if __name__ == "__main__":
    main()
