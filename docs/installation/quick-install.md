# LDF Quick Installation Guide

A condensed guide for getting LDF up and running quickly.

## Prerequisites

- **Python 3.10+** - Check with `python3 --version`
- **Git** - Check with `git --version`
- **pip** - Usually included with Python

## Quick Install (5 minutes)

### Step 1: Clone the Repository

```bash
git clone https://github.com/LLMdotInfo/ldf.git
cd ldf
```

### Step 2: Create a Virtual Environment

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install LDF

```bash
# Basic installation
pip install -e .

# With all features (MCP, AI automation, S3)
pip install -e ".[mcp,automation,s3]"
```

### Step 4: Verify Installation

```bash
ldf --version
ldf doctor
```

You should see the version number and a diagnostic report.

## VS Code Extension Setup

1. Install the **LDF** extension from the VS Code marketplace
2. Open a project folder in VS Code
3. The extension will auto-detect `ldf` if it's in:
   - Your system PATH
   - `.venv/bin/ldf` (or similar virtualenv locations)
4. If not auto-detected, configure manually:
   - Open Settings (`Cmd+,` or `Ctrl+,`)
   - Search for `ldf.executablePath`
   - Set the full path: `/path/to/ldf/.venv/bin/ldf`

## Initialize a New Project

```bash
# Interactive setup
ldf init

# Or specify a path
ldf init --path ./my-project
```

## Troubleshooting

### "command not found: ldf"

Your virtual environment isn't activated. Run:
```bash
source /path/to/ldf/.venv/bin/activate
```

### "No module named 'ldf'"

Reinstall in the active virtual environment:
```bash
pip install -e .
```

### VS Code can't find ldf

Set `ldf.executablePath` in VS Code settings to the full path:
```
/Users/yourname/ldf/.venv/bin/ldf
```

## Next Steps

- See [Getting Started](../getting-started.md) for a full tutorial
- Check platform-specific guides: [macOS](macos.md) | [Ubuntu](linux-ubuntu.md) | [Fedora](linux-fedora.md) | [Windows](windows.md)
- Learn about [VS Code Extension](https://github.com/LLMdotInfo/ldf-vscode) features
