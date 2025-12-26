# Installing LDF on macOS

> **For**: Complete beginners and experienced users
> **Time**: 30-45 minutes
> **What you'll install**: Python 3.10+, pip, VS Code, Git, LDF

---

## What You'll Need

Before starting, you'll need:
- A Mac running macOS 10.15 (Catalina) or later
- Administrator access (ability to install software)
- Internet connection
- About 2 GB of free disk space

---

## Step 1: Install Python 3.10 or Later

### Check if Python is Already Installed

Open **Terminal**:
1. Press `Cmd + Space` to open Spotlight
2. Type "Terminal" and press Enter
3. A window with a command prompt will open

Type this command and press Enter:
```bash
python3 --version
```

**If you see** `Python 3.10.0` or higher (like `3.11.5`, `3.12.1`):
- ✅ **Python is already installed!** Skip to Step 2.

**If you see** `Python 3.9.x` or lower, OR "command not found":
- Continue below to install Python.

---

### Option A: Install Python from python.org (Recommended for Beginners)

1. **Download Python**:
   - Visit: https://www.python.org/downloads/
   - Click the yellow **"Download Python 3.12.x"** button (latest version)
   - Save the `.pkg` file (about 25 MB)

2. **Run the Installer**:
   - Double-click the downloaded `.pkg` file
   - Click **Continue** through the introduction
   - Click **Continue** to accept the license
   - Click **Install** (you may need to enter your Mac password)
   - Wait for installation to complete (2-3 minutes)
   - Click **Close** when finished

3. **Verify Installation**:
   Open a **new Terminal window** (close and reopen Terminal), then run:
   ```bash
   python3 --version
   ```

   Expected output:
   ```
   Python 3.12.1
   ```

4. **Verify pip (Package Manager)**:
   ```bash
   pip3 --version
   ```

   Expected output:
   ```
   pip 23.3.1 from /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/pip (python 3.12)
   ```

---

### Option B: Install Python via Homebrew (For Advanced Users)

**What is Homebrew?** A package manager for macOS that makes installing developer tools easier.

1. **Install Homebrew** (if you don't have it):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

   Follow the on-screen instructions. This takes 5-10 minutes.

2. **Install Python**:
   ```bash
   brew install python@3.11
   ```

3. **Verify**:
   ```bash
   python3 --version
   pip3 --version
   ```

---

## Step 2: Install Visual Studio Code (Optional but Recommended)

**What is VS Code?** A free, beginner-friendly code editor from Microsoft. Not required, but makes editing LDF specs much easier.

### Download and Install

1. **Download VS Code**:
   - Visit: https://code.visualstudio.com/
   - Click **Download for macOS**
   - Save the `.zip` file (about 90 MB)

2. **Install**:
   - Double-click the `.zip` file to extract it
   - Drag **Visual Studio Code.app** to your **Applications** folder
   - Open **Applications** and double-click **Visual Studio Code**

3. **First Launch**:
   - macOS may show a security warning: "Visual Studio Code is an app downloaded from the Internet. Are you sure you want to open it?"
   - Click **Open**

4. **Install Terminal Integration** (Important):
   - In VS Code, press `Cmd + Shift + P` to open the Command Palette
   - Type: `shell command`
   - Select: **"Shell Command: Install 'code' command in PATH"**
   - You'll see: "Shell command 'code' successfully installed"

5. **Verify**:
   In Terminal, run:
   ```bash
   code --version
   ```

   Expected output:
   ```
   1.85.0
   5c3e652f63e798a5ac2f31ffd0d863669328dc4c
   arm64
   ```

---

## Step 3: Install Git (Optional but Recommended)

**What is Git?** Version control software that tracks changes to your code. Required if you want to clone LDF examples or use version control.

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

**Option A: Install via Xcode Command Line Tools (Recommended)**

1. **Trigger Installation**:
   ```bash
   git --version
   ```

   macOS will prompt: "The 'git' command requires the command line developer tools. Would you like to install the tools now?"

2. **Click "Install"**:
   - This downloads about 500 MB
   - Installation takes 5-10 minutes
   - Click **Agree** to the license

3. **Verify**:
   ```bash
   git --version
   ```

   Expected output:
   ```
   git version 2.39.2 (Apple Git-143)
   ```

**Option B: Install via Homebrew**

```bash
brew install git
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

LDF has optional features that require additional packages:

**Install MCP Servers** (for AI assistant integration with Claude, etc.):
```bash
pip3 install ldf[mcp]
```

**Install Automation Features** (for ChatGPT/Gemini API-based audits):
```bash
pip3 install ldf[automation]
```

**Install S3 Support** (for uploading coverage reports to AWS S3):
```bash
pip3 install ldf[s3]
```

**Install All Extras**:
```bash
pip3 install ldf[mcp,automation,s3]
```

---

## Step 5: Verify Everything Works

Run the LDF doctor command to check your installation:

```bash
ldf doctor
```

**Expected output (healthy system):**
```
LDF Installation Health Check
=============================

Python version: 3.12.1 ✓
pip version: 23.3.1 ✓
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

**Cause:** pip wasn't installed with Python, or PATH is incorrect.

**Solution 1** - Reinstall pip:
```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user
```

**Solution 2** - Add pip to PATH:
Add this line to `~/.zshrc` (or `~/.bash_profile` if using bash):
```bash
export PATH="$HOME/Library/Python/3.12/bin:$PATH"
```

Then reload your shell:
```bash
source ~/.zshrc
```

---

### Issue: "ldf: command not found" after installation

**Cause:** pip installed LDF to a directory not in your PATH.

**Solution:**

1. Find where pip installed LDF:
   ```bash
   pip3 show ldf
   ```

   Look for the "Location:" line, for example:
   ```
   Location: /Users/yourname/Library/Python/3.12/lib/python/site-packages
   ```

2. The `ldf` command is in the `bin` directory relative to this. Add to PATH:
   ```bash
   export PATH="$HOME/Library/Python/3.12/bin:$PATH"
   ```

3. Add this line to `~/.zshrc` (or `~/.bash_profile`) to make it permanent:
   ```bash
   echo 'export PATH="$HOME/Library/Python/3.12/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

4. Verify:
   ```bash
   ldf --version
   ```

---

### Issue: Permission denied when running pip3 install

**Cause:** Trying to install into system Python directories.

**Solution:** Install for your user only:
```bash
pip3 install --user ldf
```

---

### Issue: Python 3.9 or older is installed

**Cause:** Your Mac came with an older Python version.

**Solution:** Install Python 3.10+ using Option A or Option B above. The new version will coexist with the old one.

**After installation**, verify you're using the new version:
```bash
python3 --version  # Should show 3.10+
which python3      # Should show /Library/Frameworks/Python.framework/... or /opt/homebrew/bin/python3
```

---

### Issue: VS Code's Terminal shows "command not found" for commands that work in regular Terminal

**Cause:** VS Code is using a different shell or hasn't loaded your PATH updates.

**Solution:**
1. Quit VS Code completely (Cmd+Q)
2. Reopen VS Code
3. Open a new Terminal in VS Code (Terminal → New Terminal)
4. Try your command again

If still not working, verify your shell:
```bash
echo $SHELL
```

If it says `/bin/bash`, edit `~/.bash_profile` instead of `~/.zshrc`.
If it says `/bin/zsh`, edit `~/.zshrc`.

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
| pip | Install Python packages | ✅ Required (included with Python) |
| VS Code | Edit LDF spec files | ⭐ Recommended |
| Git | Version control, clone examples | ⭐ Recommended |
| LDF | The LDF framework itself | ✅ Required |

**Total disk space used:** ~1.5 GB
