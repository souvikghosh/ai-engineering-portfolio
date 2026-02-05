# Project 01: Commit Message Generator

**Difficulty:** Beginner | **Time:** 2-4 hours

## What You'll Build

A CLI tool that generates commit messages from your staged git changes using an LLM.

```bash
$ git add .
$ python commit_gen.py
Generated commit message:

  Add user authentication with JWT tokens

  - Implement login/logout endpoints
  - Add JWT token generation and validation
  - Create auth middleware for protected routes

Accept? [y/n/edit]:
```

## Why This Project?

- **Practical:** You'll actually use this daily
- **Portfolio gold:** Shows you can build developer tools
- **Foundation:** Teaches the core pattern for all LLM apps

## Learning Objectives

By completing this project, you'll understand:

1. **API Basics** - Making requests to an LLM API (Claude/OpenAI)
2. **Prompt Engineering** - Crafting prompts that get good results
3. **CLI Development** - Building usable command-line tools
4. **Git Integration** - Working with git programmatically

## Requirements

Build a CLI that:

- [ ] Reads staged git changes (`git diff --cached`)
- [ ] Sends diff to an LLM with a good prompt
- [ ] Displays the generated commit message
- [ ] Lets user accept, reject, or edit the message
- [ ] Commits with the final message

### Stretch Goals

- [ ] Support different commit styles (conventional commits, etc.)
- [ ] Add `--amend` flag for amending commits
- [ ] Cache API responses for identical diffs
- [ ] Add `--model` flag to switch between models

## Getting Started

```bash
# Navigate to project folder
cd 01-commit-msg-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY or OPENAI_API_KEY
```

## Hints (Only if stuck!)

<details>
<summary>Hint 1: Getting git diff</summary>

```python
import subprocess

def get_staged_diff():
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True
    )
    return result.stdout
```
</details>

<details>
<summary>Hint 2: Basic prompt structure</summary>

```
You are a commit message generator. Given a git diff, write a clear commit message.

Rules:
- First line: concise summary (50 chars max)
- Blank line
- Bullet points explaining what changed

Git diff:
{diff}
```
</details>

<details>
<summary>Hint 3: Making API call (Anthropic)</summary>

```python
import anthropic

client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)

print(message.content[0].text)
```
</details>

## Testing Your Solution

```bash
# Stage some changes
git add some_file.py

# Run your tool
python commit_gen.py

# Should output a reasonable commit message!
```

## Done?

When complete:
1. Make sure your code is clean and documented
2. Update CURRICULUM.md - mark this project as done
3. Commit your solution
4. Move to Project 02!
