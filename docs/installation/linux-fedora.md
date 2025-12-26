# Installing LDF on Linux (Fedora/RHEL/CentOS)

> **For**: Complete beginners and experienced users
> **Time**: 30-45 minutes
> **What you'll install**: Python 3.10+, pip, VS Code, Git, LDF
> **Distributions**: Fedora 36+, RHEL 9+, CentOS Stream 9+, Rocky Linux 9+, AlmaLinux 9+

---

## What You'll Need

Before starting:
- Fedora 36 or later, OR RHEL/CentOS/Rocky/AlmaLinux 9 or later
- sudo access (administrator privileges)
- Internet connection
- About 2 GB of free disk space

---

## Step 1: Install Python 3.10 or Later

### Check if Python is Already Installed

Open **Terminal** (Ctrl+Alt+T or from Activities menu), then type:
```bash
python3 --version
```

**If you see** `Python 3.10.0` or higher (like `3.11.5`, `3.12.1`):
- ✅ **Python is already installed!** Skip to "Install pip" below.

**If you see** `Python 3.9.x` or lower, OR "command not found":
- Continue below to install Python.

---

### Install Python 3.10+

**Fedora 38+ / RHEL 9+** (Python 3.11+ included):
```bash
sudo dnf install python3 python3-pip python3-devel -y
```

**Fedora 36-37** (Python 3.10+ included):
```bash
sudo dnf install python3 python3-pip python3-devel -y
```

**RHEL 8 / CentOS 8** (Need Python 3.11 module):
```bash
# Enable Python 3.11 module
sudo dnf module enable python311 -y
sudo dnf install python3.11 python3.11-pip python3.11-devel -y

# Set as default python3
sudo alternatives --set python3 /usr/bin/python3.11
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
sudo dnf install python3-pip -y
```

Verify pip:
```bash
pip3 --version
```

Expected output:
```
pip 23.0.1 from /usr/lib/python3.11/site-packages/pip (python 3.11)
```

---

## Step 2: Install Visual Studio Code (Optional but Recommended)

**What is VS Code?** A free code editor from Microsoft. Not required, but makes editing LDF specs much easier.

### Option A: Install via RPM Repository (Recommended)

1. **Add Microsoft repository**:
   ```bash
   # Import Microsoft GPG key
   sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc

   # Add VS Code repository
   sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'
   ```

2. **Install VS Code**:
   ```bash
   # Update cache and install
   sudo dnf check-update
   sudo dnf install code -y
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

### Option B: Install via Flatpak (Alternative)

```bash
flatpak install flathub com.visualstudio.code -y
```

Note: Flatpak version runs in a sandbox and may have different file access permissions.

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
sudo dnf install git -y
```

Verify:
```bash
git --version
```

Expected output:
```
git version 2.39.1
```

---

## Step 4: Install LDF

Now that Python and pip are installed, installing LDF is simple.

### Basic Installation

```bash
pip3 install --user ldf
```

**What's happening?**
- `pip3` is Python's package manager
- `--user` installs for your user only (no sudo needed)
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

### Add LDF to PATH

After installing with `--user`, add `~/.local/bin` to your PATH:

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
pip3 install --user ldf[mcp]
```

**Install Automation Features** (for ChatGPT/Gemini API audits):
```bash
pip3 install --user ldf[automation]
```

**Install S3 Support** (for AWS S3 coverage uploads):
```bash
pip3 install --user ldf[s3]
```

**Install All Extras**:
```bash
pip3 install --user ldf[mcp,automation,s3]
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
sudo dnf install python3-pip -y
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

**Cause:** Trying to install system-wide without sudo or --user flag.

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

### Issue: Python version too old

**Cause:** Using RHEL 8 or older Fedora with Python 3.9 or earlier.

**Solution for RHEL 8:**
```bash
# Enable Python 3.11 module
sudo dnf module list python3*
sudo dnf module enable python311 -y
sudo dnf install python3.11 python3.11-pip -y

# Set as default
sudo alternatives --set python3 /usr/bin/python3.11
```

**Solution for older Fedora:**
Upgrade to Fedora 36+ which includes Python 3.10+.

---

### Issue: SELinux blocks VS Code or Git operations

**Error message:**
```
Permission denied (SELinux)
```

**Solution:**

1. Check SELinux status:
   ```bash
   getenforce
   ```

2. If Enforcing and causing issues, temporarily set to Permissive:
   ```bash
   sudo setenforce 0
   ```

3. For permanent fix, create proper SELinux policies or:
   ```bash
   sudo setsebool -P allow_execmem 1
   ```

Note: Disabling SELinux is not recommended for production systems.

---

### Issue: Firewall blocks package downloads

**Cause:** Firewall blocking HTTP/HTTPS connections.

**Solution:**

1. Check firewall status:
   ```bash
   sudo firewall-cmd --state
   ```

2. If active, ensure HTTP/HTTPS allowed:
   ```bash
   sudo firewall-cmd --permanent --add-service=http
   sudo firewall-cmd --permanent --add-service=https
   sudo firewall-cmd --reload
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

### Fedora Workstation 40
- Python 3.12 included by default
- GNOME desktop with Wayland
- All commands above work without modifications

### Fedora 39
- Python 3.12 included
- SELinux Enforcing by default

### Fedora 38
- Python 3.11 included
- Use `dnf` for all package operations

### RHEL 9 / CentOS Stream 9 / Rocky Linux 9 / AlmaLinux 9
- Python 3.9 by default, use module system for 3.11+
- SELinux Enforcing by default
- May need Red Hat subscription for some packages (RHEL only)

### RHEL 8 / CentOS 8 / Rocky Linux 8 / AlmaLinux 8
- Python 3.6 by default
- Must enable python311 module
- Use `dnf module enable python311`

### Package Manager Notes
- **dnf** is the modern package manager (Fedora 22+, RHEL 8+)
- **yum** is legacy but still works (RHEL 7, CentOS 7)
- Commands are mostly interchangeable: `dnf` ↔ `yum`
