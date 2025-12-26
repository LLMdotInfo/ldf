# Installing LDF

Complete installation guides for all supported platforms.

---

## Quick Platform Selection

Choose your operating system:

### 🍎 **macOS** (10.15+ Catalina or later)
**[Complete macOS Installation Guide →](macos.md)**
- Intel and Apple Silicon (M1/M2/M3) supported
- Includes Homebrew and python.org installation methods
- **Time**: 30-45 minutes

### 🪟 **Windows** (10 or 11)
**[Complete Windows Installation Guide →](windows.md)**
- Comprehensive PATH configuration help
- PowerShell and CMD support
- **Time**: 30-45 minutes

### 🐧 **Linux - Ubuntu/Debian**
**[Ubuntu/Debian Installation Guide →](linux-ubuntu.md)**
- Ubuntu 20.04+, Debian 11+
- Linux Mint, Pop!_OS also supported
- **Time**: 30-45 minutes

### 🐧 **Linux - Fedora/RHEL**
**[Fedora/RHEL Installation Guide →](linux-fedora.md)**
- Fedora 36+, RHEL 9+, CentOS Stream 9+
- Rocky Linux, AlmaLinux also supported
- **Time**: 30-45 minutes

---

## What You'll Install

All platforms install the same core components:

| Component | Purpose | Required? |
|-----------|---------|-----------|
| **Python 3.10+** | Run LDF and execute Python code | ✅ Required |
| **pip** | Python package manager | ✅ Required (bundled with Python) |
| **LDF CLI** | The LDF framework command-line tool | ✅ Required |
| **VS Code** | Code/spec editor with LDF extension support | ⭐ Recommended |
| **Git** | Version control, clone examples | ⭐ Recommended |

**Total disk space**: ~1.5-2 GB

---

## Installation Overview

Each platform guide follows the same structure:

1. **Check existing installations** - See if you already have Python/Git
2. **Install Python 3.10+** - Core requirement for LDF
3. **Install VS Code** (optional) - Best editor for LDF specs
4. **Install Git** (optional) - For version control and examples
5. **Install LDF** - The framework itself
6. **Verify installation** - Run `ldf doctor` to check everything works
7. **Troubleshooting** - Platform-specific solutions to common issues

---

## Not Sure Which Guide to Follow?

### How to Check Your Operating System

**On macOS:**
- Click the Apple icon → About This Mac
- Look at "macOS" version (e.g., "macOS Sonoma 14.2")

**On Windows:**
- Press `Windows key + R`
- Type `winver` and press Enter
- Look at "Version" (e.g., "Windows 11")

**On Linux:**
```bash
cat /etc/os-release
```
Look for `NAME` and `VERSION_ID` lines.

---

## Quick Install (Experienced Users Only)

If you're comfortable with the command line and already have Python 3.10+ and pip installed:

```bash
# Install LDF
pip install llm-ldf

# Or with all optional features
pip install llm-ldf[mcp,automation,s3]

# Verify
ldf --version
ldf doctor
```

**Note for beginners**: Follow the full platform-specific guide above for step-by-step instructions!

---

## After Installation

Once LDF is installed successfully:

### Next Steps for Beginners
1. **[Your First LDF Spec Tutorial →](../tutorials/01-first-spec.md)**
   - 20-minute hands-on tutorial
   - Create a complete spec from scratch
   - Learn the three-phase workflow

### Next Steps for Experienced Users
1. **[5-Minute Quickstart →](../quickstart.md)**
   - Fast track to your first LDF project
   - Assumes familiarity with Python and terminal

---

## Optional Features

After basic installation, you can install optional LDF features:

### MCP Servers (AI Assistant Integration)
Enables 90% token savings when using Claude Code and other AI assistants.

```bash
pip install llm-ldf[mcp]
```

**Learn more**: [MCP Setup Tutorial](../tutorials/05-mcp-setup.md)

### Automation (ChatGPT/Gemini API Audits)
API-based multi-agent review of your specifications.

```bash
pip install llm-ldf[automation]
```

**Learn more**: [Multi-Agent Workflow](../multi-agent-workflow.md)

### S3 Support (Coverage Upload)
Upload test coverage reports to AWS S3.

```bash
pip install llm-ldf[s3]
```

**Install All Optional Features:**
```bash
pip install llm-ldf[mcp,automation,s3]
```

---

## Common Installation Issues

### "python: command not found"
- **Solution**: Install Python using your platform's guide above
- Python 3.10 or later is required

### "ldf: command not found" after installation
- **macOS/Linux**: Add `~/.local/bin` to PATH
- **Windows**: Add Python Scripts folder to PATH
- See platform-specific troubleshooting in guides above

### "Permission denied" errors
- **Solution**: Use `pip install --user ldf` instead of `sudo pip install`
- Installing with `--user` is safer and recommended

### Need More Help?
- Check platform-specific troubleshooting sections
- Run `ldf doctor` for diagnostics
- See [Troubleshooting Guide](../reference/troubleshooting.md)
- Report issues: [GitHub Issues](https://github.com/LLMdotInfo/ldf/issues)

---

## Upgrading LDF

To upgrade to the latest version:

```bash
pip install --upgrade ldf
```

Check your version:
```bash
ldf --version
```

---

## Uninstalling LDF

If you need to uninstall:

```bash
pip uninstall ldf
```

This removes LDF but keeps Python, VS Code, and Git installed.

---

## Platform Comparison

| Feature | macOS | Windows | Ubuntu/Debian | Fedora/RHEL |
|---------|-------|---------|---------------|-------------|
| Python pre-installed | ⚠️ Old version | ❌ No | ⚠️ May be old | ⚠️ May be old |
| Package manager | Homebrew (optional) | None (manual) | apt | dnf/yum |
| PATH setup | Automatic | Manual | Automatic | Automatic |
| VS Code install | Download .zip | Download .exe | APT repo | DNF repo |
| Git install | Xcode CLI Tools | Download .exe | apt | dnf |
| Typical issues | PATH, old Python | PATH setup | Old Python version | SELinux, Python modules |

---

## Need Platform-Specific Help?

Select your platform above and follow the complete guide. Each guide includes:
- ✅ Step-by-step instructions with screenshots
- ✅ Command explanations for beginners
- ✅ Expected output for each step
- ✅ Comprehensive troubleshooting section
- ✅ Platform-specific notes and gotchas

**Ready to start?** Click your platform link at the top of this page!
