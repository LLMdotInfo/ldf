# Installing LDF on Windows

> **For**: Complete beginners and experienced users
> **Time**: 30-45 minutes
> **What you'll install**: Python 3.10+, pip, VS Code, Git, LDF

---

## What You'll Need

Before starting:
- A PC running Windows 10 or Windows 11
- Administrator access (ability to install software)
- Internet connection
- About 2 GB of free disk space

---

## Step 1: Install Python 3.10 or Later

### Check if Python is Already Installed

Open **Command Prompt** or **PowerShell**:

**Method 1 (Windows 10/11):**
1. Press `Windows key + R`
2. Type `cmd` and press Enter

**Method 2:**
1. Click the Start menu
2. Type "cmd" or "PowerShell"
3. Click on **Command Prompt** or **Windows PowerShell**

In the command window, type:
```cmd
python --version
```

**If you see** `Python 3.10.0` or higher (like `3.11.5`, `3.12.1`):
- ✅ **Python is already installed!** Skip to Step 2.

**If you see** `Python 3.9.x` or lower, OR "'python' is not recognized":
- Continue below to install Python.

---

### Install Python from python.org

1. **Download Python**:
   - Visit: https://www.python.org/downloads/
   - Click the yellow **"Download Python 3.12.x"** button
   - Save the installer (about 25 MB)

2. **Run the Installer**:
   - Double-click the downloaded file (e.g., `python-3.12.1-amd64.exe`)

   **⚠️ IMPORTANT - Before clicking "Install Now":**
   - ✅ **Check the box**: "Add python.exe to PATH"
   - ✅ **Check the box**: "Add Python to environment variables"

   - Click **"Install Now"**
   - Click **"Yes"** when Windows asks for admin permission
   - Wait for installation (2-3 minutes)
   - Click **"Close"** when finished

3. **Verify Installation**:
   **Close and reopen** Command Prompt/PowerShell (important!), then run:
   ```cmd
   python --version
   ```

   Expected output:
   ```
   Python 3.12.1
   ```

4. **Verify pip**:
   ```cmd
   pip --version
   ```

   Expected output:
   ```
   pip 23.3.1 from C:\Users\YourName\AppData\Local\Programs\Python\Python312\Lib\site-packages\pip (python 3.12)
   ```

---

## Step 2: Install Visual Studio Code (Optional but Recommended)

**What is VS Code?** A free code editor from Microsoft. Not required, but makes editing LDF specs much easier.

### Download and Install

1. **Download VS Code**:
   - Visit: https://code.visualstudio.com/
   - Click **Download for Windows**
   - Save the installer (about 90 MB)

2. **Run the Installer**:
   - Double-click the downloaded `.exe` file
   - Click **"I accept the agreement"**
   - Click **Next** to use default installation folder
   - Click **Next** for Start Menu folder
   - **✅ Important - Check these boxes:**
     - ✅ "Add to PATH (requires shell restart)"
     - ✅ "Create a desktop icon" (optional, but helpful)
     - ✅ "Register Code as an editor for supported file types"
   - Click **Next**, then **Install**
   - Wait for installation (2-3 minutes)
   - Click **Finish**

3. **First Launch**:
   - Double-click the VS Code icon on your desktop or Start menu
   - VS Code will open and may show a Welcome tab

4. **Verify**:
   Close and reopen Command Prompt/PowerShell, then run:
   ```cmd
   code --version
   ```

   Expected output:
   ```
   1.85.0
   5c3e652f63e798a5ac2f31ffd0d863669328dc4c
   x64
   ```

---

## Step 3: Install Git (Optional but Recommended)

**What is Git?** Version control software. Required if you want to clone LDF examples or track changes to your code.

### Check if Git is Already Installed

```cmd
git --version
```

**If you see** `git version 2.x.x`:
- ✅ **Git is already installed!** Skip to Step 4.

**If you see** "'git' is not recognized":
- Continue below.

---

### Install Git for Windows

1. **Download Git**:
   - Visit: https://git-scm.com/download/win
   - The download should start automatically
   - Save the installer (about 50 MB)

2. **Run the Installer**:
   - Double-click the downloaded `.exe` file
   - Click **Next** through the license agreement
   - Click **Next** to accept default installation folder

   **Important Options** (use these settings):
   - **"Select Components"**: Keep defaults, click **Next**
   - **"Choose default editor"**: Select **"Use Visual Studio Code as Git's default editor"** (if you installed VS Code), click **Next**
   - **"Adjusting PATH"**: Select **"Git from the command line and also from 3rd-party software"**, click **Next**
   - **"HTTPS transport backend"**: Keep default, click **Next**
   - **"Line ending conversions"**: Keep default ("Checkout Windows-style, commit Unix-style"), click **Next**
   - **"Terminal emulator"**: Keep default ("Use MinTTY"), click **Next**
   - **All remaining screens**: Keep defaults, click **Next**
   - Click **Install**
   - Wait for installation (3-5 minutes)
   - Click **Finish**

3. **Verify**:
   Close and reopen Command Prompt/PowerShell, then run:
   ```cmd
   git --version
   ```

   Expected output:
   ```
   git version 2.43.0.windows.1
   ```

---

## Step 4: Install LDF

Now that Python and pip are installed, installing LDF is simple.

### Basic Installation

```cmd
pip install llm-ldf
```

**What's happening?**
- `pip` is Python's package manager
- `install ldf` downloads and installs the LDF CLI tool
- This takes about 30 seconds

**Expected output:**
```
Collecting ldf
  Downloading ldf-1.0.0-py3-none-any.whl (150 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 150.0/150.0 KB 2.5 MB/s eta 0:00:00
Collecting click>=8.0.0
  Using cached click-8.1.7-py3-none-any.whl (97 kB)
[... more packages ...]
Installing collected packages: click, pyyaml, rich, jinja2, questionary, ldf
Successfully installed click-8.1.7 jinja2-3.1.2 ldf-1.0.0 pyyaml-6.0.1 questionary-2.0.1 rich-13.7.0
```

---

### Verify LDF Installation

```cmd
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
```cmd
pip install llm-ldf[mcp]
```

**Install Automation Features** (for ChatGPT/Gemini API audits):
```cmd
pip install llm-ldf[automation]
```

**Install S3 Support** (for AWS S3 coverage uploads):
```cmd
pip install llm-ldf[s3]
```

**Install All Extras**:
```cmd
pip install llm-ldf[mcp,automation,s3]
```

---

## Step 5: Verify Everything Works

```cmd
ldf doctor
```

**Expected output:**
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

### Issue: "'python' is not recognized as an internal or external command"

**Cause:** Python isn't in your system PATH.

**Solution 1** - Reinstall Python and check "Add to PATH":
- Uninstall Python (Settings → Apps → Python → Uninstall)
- Download and reinstall, **making sure to check "Add python.exe to PATH"**

**Solution 2** - Manually add to PATH:
1. Press `Windows key + R`
2. Type `sysdm.cpl` and press Enter
3. Click **Advanced** tab
4. Click **Environment Variables**
5. Under "User variables", select **Path** and click **Edit**
6. Click **New** and add:
   ```
   C:\Users\YourUsername\AppData\Local\Programs\Python\Python312
   C:\Users\YourUsername\AppData\Local\Programs\Python\Python312\Scripts
   ```
   (Replace `YourUsername` with your actual username)
7. Click **OK** on all windows
8. Close and reopen Command Prompt

---

### Issue: "'ldf' is not recognized as an internal or external command"

**Cause:** LDF installed but Scripts directory not in PATH.

**Solution:**

1. Find where pip installed LDF:
   ```cmd
   pip show ldf
   ```

   Look for "Location:", for example:
   ```
   Location: C:\Users\YourName\AppData\Local\Programs\Python\Python312\Lib\site-packages
   ```

2. The `ldf.exe` is in the `Scripts` folder one level up. Add to PATH:
   - Press `Windows key + R`
   - Type `sysdm.cpl` and press Enter
   - Click **Advanced** → **Environment Variables**
   - Edit **Path** under User variables
   - Click **New** and add:
     ```
     C:\Users\YourName\AppData\Local\Programs\Python\Python312\Scripts
     ```
   - Click **OK** on all windows
   - Close and reopen Command Prompt

3. Verify:
   ```cmd
   ldf --version
   ```

---

### Issue: Permission errors during pip install

**Error message:**
```
ERROR: Could not install packages due to an OSError: [WinError 5] Access is denied
```

**Solution 1** - Install for current user only:
```cmd
pip install --user ldf
```

**Solution 2** - Run as administrator:
- Right-click Command Prompt
- Select "Run as administrator"
- Run `pip install llm-ldf` again

---

### Issue: Python version too old

**Cause:** Windows came with an older Python or you have multiple versions.

**Solution:**

1. Check which Python you're using:
   ```cmd
   where python
   ```

   This shows all Python installations.

2. Uninstall old versions:
   - Settings → Apps → Search "Python"
   - Uninstall older versions (keep 3.10+)

3. Install Python 3.12 using instructions above

4. Verify:
   ```cmd
   python --version
   ```

---

### Issue: VS Code Terminal can't find python/ldf

**Cause:** VS Code cached old PATH before you installed tools.

**Solution:**
1. Close VS Code completely
2. Reopen VS Code
3. Open new Terminal (Terminal → New Terminal)
4. Try command again

If still not working, verify VS Code is using the correct shell:
- Open VS Code settings (File → Preferences → Settings)
- Search for "terminal integrated shell windows"
- Ensure it's using `cmd.exe` or `powershell.exe`

---

### Issue: PowerShell execution policy blocks scripts

**Error message:**
```
ldf : File C:\Users\...\ldf.ps1 cannot be loaded because running scripts is disabled
```

**Solution:**

Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then close and reopen PowerShell normally.

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
