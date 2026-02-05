# Key Concepts - Project 01

## 1. LLM API Basics

An LLM API works like any web API:
- You send a request with your prompt
- You get back a response with generated text

```
Your Code → HTTP Request → API → LLM processes → Response → Your Code
```

**Key terms:**
- **API Key**: Your authentication credential (keep it secret!)
- **Model**: Which LLM to use (e.g., `claude-sonnet-4-20250514`)
- **Max tokens**: Limit on response length
- **Messages**: The conversation history you send

## 2. Prompt Engineering Basics

The prompt is *everything*. A good prompt:

1. **Sets the role**: "You are a commit message generator..."
2. **Gives clear instructions**: "Write a concise summary..."
3. **Provides format**: "First line under 50 chars, then bullets..."
4. **Includes examples** (optional): Shows what good output looks like

**Tip:** Iterate on your prompt! Try it, see results, improve.

## 3. Working with subprocess

Python's `subprocess` module runs shell commands:

```python
import subprocess

# Run a command and capture output
result = subprocess.run(
    ["git", "status"],      # Command as list
    capture_output=True,     # Capture stdout/stderr
    text=True                # Return strings, not bytes
)

print(result.stdout)         # The command's output
print(result.returncode)     # 0 = success
```

## 4. Environment Variables

Never hardcode API keys! Use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

api_key = os.getenv("ANTHROPIC_API_KEY")
```

The `.env` file (which you never commit):
```
ANTHROPIC_API_KEY=sk-ant-...
```

## Resources

- [Anthropic API Docs](https://docs.anthropic.com/en/api/getting-started)
- [Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)
- [Python subprocess docs](https://docs.python.org/3/library/subprocess.html)
