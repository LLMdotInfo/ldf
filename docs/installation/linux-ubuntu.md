# Installing LDF on Linux (Ubuntu/Debian)

> **For**: Complete beginners and experienced users
> **Time**: 30-45 minutes
> **What you'll install**: Python 3.10+, pip, VS Code, Git, LDF
> **Distributions**: Ubuntu 20.04+, Debian 11+, Linux Mint 20+, Pop!_OS 20.04+

---

## What You'll Need

Before starting:
- Ubuntu 20.04 or later, OR Debian 11 or later
- sudo access (administrator privileges)
- Internet connection
- About 2 GB of free disk space

---

## Step 1: Install Python 3.10 or Later

### Check if Python is Already Installed

Open **Terminal** (Ctrl+Alt+T), then type:
```bash
python3 --version
```

**If you see** `Python 3.10.0` or higher (like `3.11.5`, `3.12.1`):
- ✅ **Python is already installed!** Skip to "Install pip" below.

**If you see** `Python 3.9.x` or lower, OR "command not found":
- Continue below to install Python.

---

### Install Python 3.10+

**Ubuntu 22.04+ / Debian 12+** (Python 3.10+ included):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

**Ubuntu 20.04 / Debian 11** (Need to add PPA for Python 3.10+):
```bash
# Add deadsnakes PPA (for newer Python versions)
sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-distutils -y

# Install pip for Python 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11
```

---

### Verify Installation

```bash
python3 --version
```

Expected output:
```
Python 3.11.5
```

---

### Install pip (if not already installed)

```bash
# Ubuntu 22.04+ / Debian 12+
sudo apt install python3-pip -y

# Ubuntu 20.04 / Debian 11 (if using python3.11 from PPA)
# pip was installed in the previous step
```

Verify pip:
```bash
pip3 --version
```

Expected output:
```
pip 23.0.1 from /usr/lib/python3/dist-packages/pip (python 3.11)
```

---

## Step 2: Install Visual Studio Code (Optional but Recommended)

**What is VS Code?** A free code editor from Microsoft. Not required, but makes editing LDF specs much easier.

### Option A: Install via APT Repository (Recommended)

1. **Add Microsoft GPG key and repository**:
   ```bash
   # Install prerequisites
   sudo apt install wget gpg apt-transport-https -y

   # Download and install Microsoft GPG key
   wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
   sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg

   # Add VS Code repository
   sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'

   # Clean up
   rm -f packages.microsoft.gpg
   ```

2. **Install VS Code**:
   ```bash
   sudo apt update
   sudo apt install code -y
   ```

3. **Verify**:
   ```bash
   code --version
   ```

   Expected output:
   ```
   1.85.0
   5c3e652f63e798a5ac2f31ffd0d863669328dc4c
   x64
   ```

### Option B: Install via Snap (Simpler, but slower startup)

```bash
sudo snap install code --classic
```

---

## Step 3: Install Git

**What is Git?** Version control software. Required if you want to clone LDF examples or track changes to your code.

### Check if Git is Already Installed

```bash
git --version
```

**If you see** `git version 2.x.x`:
- ✅ **Git is already installed!** Skip to Step 4.

**If you see** "command not found":
- Continue below.

---

### Install Git

```bash
sudo apt update
sudo apt install git -y
```

Verify:
```bash
git --version
```

Expected output:
```
git version 2.34.1
```

---

## Step 4: Install LDF

Now that Python and pip are installed, installing LDF is simple.

### Basic Installation

```bash
pip3 install ldf
```

**What's happening?**
- `pip3` is Python's package manager
- `install ldf` downloads and installs the LDF CLI tool
- This takes about 30 seconds

**Expected output:**
```
Collecting ldf
  Downloading ldf-1.0.0-py3-none-any.whl (150 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 150.0/150.0 kB 2.5 MB/s eta 0:00:00
Collecting click>=8.0.0
  Using cached click-8.1.7-py3-none-any.whl (97 kB)
[... more packages ...]
Installing collected packages: click, pyyaml, rich, jinja2, questionary, ldf
Successfully installed click-8.1.7 jinja2-3.1.2 ldf-1.0.0 pyyaml-6.0.1 questionary-2.0.1 rich-13.7.0
```

---

### Add LDF to PATH (if needed)

If you installed with `pip3 install --user ldf`, you may need to add `~/.local/bin` to your PATH:

```bash
# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

### Verify LDF Installation

```bash
ldf --version
```

**Expected output:**
```
ldf version 1.0.0
```

✅ **Success!** LDF is installed and ready to use.

---

### Optional: Install LDF Extras

**Install MCP Servers** (for AI assistant integration):
```bash
pip3 install ldf[mcp]
```

**Install Automation Features** (for ChatGPT/Gemini API audits):
```bash
pip3 install ldf[automation]
```

**Install S3 Support** (for AWS S3 coverage uploads):
```bash
pip3 install ldf[s3]
```

**Install All Extras**:
```bash
pip3 install ldf[mcp,automation,s3]
```

---

## Step 5: Verify Everything Works

```bash
ldf doctor
```

**Expected output:**
```
LDF Installation Health Check
=============================

Python version: 3.11.5 ✓
pip version: 23.0.1 ✓
LDF version: 1.0.0 ✓

Optional components:
  MCP servers: Not installed
  Automation: Not installed
  S3 support: Not installed

All core components are working correctly!
```

---

## Troubleshooting

### Issue: "pip3: command not found"

**Cause:** pip wasn't installed.

**Solution:**
```bash
sudo apt update
sudo apt install python3-pip -y
```

If using Python 3.11 from PPA:
```bash
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11
```

---

### Issue: "ldf: command not found" after installation

**Cause:** `~/.local/bin` not in PATH.

**Solution:**

1. Add to PATH:
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

2. Verify:
   ```bash
   ldf --version
   ```

---

### Issue: Permission denied when running pip3 install

**Cause:** Trying to install system-wide without sudo.

**Solution 1** - Install for current user only (recommended):
```bash
pip3 install --user ldf
```

**Solution 2** - Install system-wide (not recommended):
```bash
sudo pip3 install ldf
```

Note: Using `--user` is safer and doesn't require sudo.

---

### Issue: Python version too old (Python 3.9 or earlier)

**Cause:** Ubuntu 20.04/Debian 11 ships with older Python.

**Solution:** Follow the "Ubuntu 20.04 / Debian 11" instructions in Step 1 to install Python 3.11 from the deadsnakes PPA.

---

### Issue: "externally-managed-environment" error

**Error message:**
```
error: externally-managed-environment
```

**Cause:** Debian/Ubuntu prevents pip from installing packages system-wide to avoid conflicts with apt.

**Solution 1** - Use virtual environment (recommended for projects):
```bash
python3 -m venv ~/.venv/ldf
source ~/.venv/ldf/bin/activate
pip install llm-ldf
```

**Solution 2** - Install with --user flag:
```bash
pip3 install --user ldf
```

Then ensure `~/.local/bin` is in your PATH (see "ldf: command not found" solution above).

---

### Issue: VS Code won't start

**Cause:** Missing dependencies or permissions.

**Solution:**

1. Check for errors:
   ```bash
   code --verbose
   ```

2. Install missing dependencies:
   ```bash
   sudo apt install libgbm1 libasound2 -y
   ```

3. If using Wayland, try with X11:
   ```bash
   code --disable-gpu
   ```

---

## Next Steps

Now that LDF is installed:

1. **Complete Beginners**: Continue to [Your First LDF Spec](../tutorials/01-first-spec.md)
2. **Experienced Users**: Jump to [5-Minute Quickstart](../quickstart.md)
3. **Need Help?**: See [Troubleshooting Guide](../reference/troubleshooting.md)

---

## Summary of What You Installed

| Tool | Purpose | Required? |
|------|---------|-----------|
| Python 3.10+ | Run LDF and Python-based tools | ✅ Required |
| pip | Install Python packages | ✅ Required |
| VS Code | Edit LDF spec files | ⭐ Recommended |
| Git | Version control, clone examples | ⭐ Recommended |
| LDF | The LDF framework itself | ✅ Required |

**Total disk space used:** ~1.5 GB

---

## Platform-Specific Notes

### Ubuntu 24.04 LTS
- Python 3.12 included by default
- All commands above work without modifications

### Ubuntu 22.04 LTS
- Python 3.10 included by default
- All commands above work without modifications

### Ubuntu 20.04 LTS
- Python 3.8 by default - use deadsnakes PPA for 3.11+
- Follow "Ubuntu 20.04 / Debian 11" instructions in Step 1

### Debian 12 (Bookworm)
- Python 3.11 included
- All commands work with `apt` instead of `apt-get`

### Debian 11 (Bullseye)
- Python 3.9 by default - use backports or compile Python 3.11+
- Follow "Ubuntu 20.04 / Debian 11" instructions

### Linux Mint / Pop!_OS
- Based on Ubuntu, same instructions apply
- Check your base Ubuntu version: `cat /etc/upstream-release/lsb-release`
