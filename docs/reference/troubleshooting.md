# Troubleshooting Guide

Common issues and solutions for LDF users.

---

## Table of Contents

- [Installation Issues](#installation-issues)
- [Command Not Found Errors](#command-not-found-errors)
- [Linting Errors](#linting-errors)
- [Project Initialization Problems](#project-initialization-problems)
- [MCP Server Issues](#mcp-server-issues)
- [Coverage Problems](#coverage-problems)
- [Platform-Specific Issues](#platform-specific-issues)
- [FAQ](#faq)

---

## Installation Issues

### Python version too old

**Error:**
```
ERROR: ldf requires Python 3.10 or later
```

**Solution:**

**macOS:**
```bash
# Install Python 3.12
brew install python@3.12
# Or download from python.org
```

**Windows:**
- Download Python 3.12 from https://www.python.org/downloads/
- ⚠️ Check "Add python.exe to PATH" during installation

**Linux (Ubuntu/Debian):**
```bash
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install python3.11
```

---

### pip install fails with "No matching distribution"

**Error:**
```
ERROR: Could not find a version that satisfies the requirement ldf
```

**Causes:**
1. Python version too old (< 3.10)
2. pip not updated
3. Network/proxy issues

**Solutions:**

1. **Check Python version:**
```bash
python3 --version  # Must be 3.10+
```

2. **Update pip:**
```bash
python3 -m pip install --upgrade pip
```

3. **Try with --user:**
```bash
pip3 install --user ldf
```

4. **Behind proxy:**
```bash
pip3 install ldf --proxy http://proxy.company.com:8080
```

---

### Permission denied errors

**Error:**
```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**Solution: Install with `--user` flag**
```bash
pip3 install --user ldf
```

**Why:** Installs to your user directory, no sudo needed.

**Then add to PATH if needed:**
```bash
# macOS/Linux
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Windows
# Add %APPDATA%\Python\Python312\Scripts to PATH
```

---

## Command Not Found Errors

### "ldf: command not found" (macOS/Linux)

**Cause:** `~/.local/bin` not in PATH.

**Solution:**

1. **Add to PATH:**
```bash
export PATH="$HOME/.local/bin:$PATH"
```

2. **Make permanent:**
```bash
# For bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# For zsh (macOS default)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

3. **Verify:**
```bash
which ldf
# Should show: /Users/yourname/.local/bin/ldf
```

---

### "'ldf' is not recognized" (Windows)

**Cause:** Python Scripts folder not in PATH.

**Solution:**

1. **Find Python Scripts folder:**
```cmd
pip show ldf
```
Look for "Location:" line, e.g.:
```
Location: C:\Users\YourName\AppData\Local\Programs\Python\Python312\Lib\site-packages
```

The Scripts folder is:
```
C:\Users\YourName\AppData\Local\Programs\Python\Python312\Scripts
```

2. **Add to PATH:**
- Press `Windows key + R`
- Type `sysdm.cpl` and press Enter
- Click **Advanced** tab
- Click **Environment Variables**
- Edit **Path** under User variables
- Click **New** and add Scripts path
- Click **OK** on all windows

3. **Restart terminal and verify:**
```cmd
ldf --version
```

---

### "pip3: command not found"

**Cause:** pip not installed or not in PATH.

**Solution:**

**macOS/Linux:**
```bash
# Download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# Install pip
python3 get-pip.py --user

# Verify
pip3 --version
```

**Windows:**
Reinstall Python with "Install pip" option checked.

---

## Linting Errors

### "Guardrail matrix incomplete"

**Error:**
```
ERROR: Guardrail matrix incomplete - missing guardrails: 6, 7
```

**Cause:** Not all 8 core guardrails (+ preset guardrails) listed in matrix.

**Solution:**

Ensure table has all guardrails:

**Core 8:**
1. Testing Coverage
2. Security Basics
3. Error Handling
4. Logging & Observability
5. API Design
6. Data Validation
7. Database Migrations
8. Documentation

**Plus preset guardrails if using:**
- SaaS: +5 guardrails
- Fintech: +7 guardrails
- Healthcare: +6 guardrails
- API-only: +4 guardrails

**Example:**
```markdown
| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [US-1] | TBD | TBD | Dev | TODO |
| 2. Security Basics | [US-2] | TBD | TBD | Dev | TODO |
| 3. Error Handling | [US-1] | TBD | TBD | Dev | TODO |
| 4. Logging & Observability | [US-1] | TBD | TBD | Dev | TODO |
| 5. API Design | [US-1] | TBD | TBD | Dev | TODO |
| 6. Data Validation | [US-1] | TBD | TBD | Dev | TODO |
| 7. Database Migrations | [US-3] | TBD | TBD | DB | TODO |
| 8. Documentation | [US-1] | TBD | TBD | TechWriter | TODO |
```

---

### "Guardrail marked N/A without reason"

**Error:**
```
ERROR: Guardrail 6 marked N/A but no reason provided
```

**Cause:** Marked N/A in table but didn't explain why.

**Solution:**

**Bad:**
```markdown
| 6. Data Validation | N/A | N/A | N/A | - | N/A |
```

**Good:**
```markdown
| 6. Data Validation | N/A - No user input parameters | N/A | N/A | - | N/A |
```

---

### "Template markers found"

**Error:**
```
ERROR: Template markers [TBD] or [TODO] found in spec
```

**Cause:** Left placeholder text in requirements/design/tasks files.

**Solution:**

Replace all placeholders:
- `[TBD]` → Specific content or "N/A - reason"
- `[TODO]` → Actual content
- `[FILL THIS IN]` → Real values

**Find all placeholders:**
```bash
grep -r "\[TBD\]" .ldf/specs/
grep -r "\[TODO\]" .ldf/specs/
```

---

### "No user stories found"

**Error:**
```
ERROR: No user stories found in requirements.md
```

**Cause:** Missing user stories or incorrect formatting.

**Solution:**

Ensure you have at least one user story with this format:

```markdown
### US-1: Story Title

**As a** [role]
**I want to** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] AC-1.1: Specific criterion
- [ ] AC-1.2: Another criterion
```

**Required elements:**
- `### US-X:` heading
- `**As a**`, `**I want to**`, `**So that**` lines
- `**Acceptance Criteria:**` section
- At least one `- [ ] AC-X.Y:` item

---

### "Acceptance criteria not testable"

**Warning:**
```
WARNING: AC-1.2 may not be testable - too vague
```

**Cause:** Acceptance criteria like "works correctly" or "is fast".

**Solution:**

**Vague (bad):**
- `AC-1.1: Login works correctly`
- `AC-1.2: System is fast`

**Specific (good):**
- `AC-1.1: Login returns 200 OK with JWT token on valid credentials`
- `AC-1.2: Login endpoint responds in < 500ms at p95`

---

## Project Initialization Problems

### "Not in an LDF project"

**Error:**
```
ERROR: Not in an LDF project. Run 'ldf init' first.
```

**Cause:** Trying to run LDF commands outside an initialized directory.

**Solution:**

1. **Check for .ldf directory:**
```bash
ls -la .ldf  # Should exist
```

2. **If missing, initialize:**
```bash
ldf init
```

3. **Or navigate to correct directory:**
```bash
cd /path/to/my-ldf-project
```

---

### ".ldf directory already exists"

**Error:**
```
ERROR: .ldf directory already exists. Use --force to overwrite.
```

**Cause:** Trying to reinitialize an LDF project.

**Solutions:**

**Repair existing setup:**
```bash
ldf init --repair
```

**Start fresh (destructive):**
```bash
rm -rf .ldf AGENT.md .agent
ldf init
```

**Upgrade framework files only:**
```bash
ldf update
```

---

### "Invalid preset name"

**Error:**
```
ERROR: Unknown preset 'webapp'. Valid presets: saas, fintech, healthcare, api-only, custom
```

**Cause:** Typo in preset name.

**Solution:**

Use valid preset:
```bash
ldf init --preset saas       # ✓ Correct
ldf init --preset webapp     # ✗ Invalid
```

**List available presets:**
```bash
ldf list-presets
```

---

## MCP Server Issues

### "MCP servers not installed"

**Error:**
```
WARNING: MCP servers requested but 'mcp' package not installed
```

**Solution:**

```bash
pip install llm-ldf[mcp]
```

**Verify:**
```bash
ldf mcp-health
```

---

### "MCP server unhealthy"

**Error:**
```
ERROR: spec_inspector MCP server not responding
```

**Causes & Solutions:**

1. **MCP package not installed:**
```bash
pip install llm-ldf[mcp]
```

2. **Python version too old:**
```bash
python3 --version  # Must be 3.10+
```

3. **Corrupted installation:**
```bash
pip uninstall ldf
pip install llm-ldf[mcp]
```

4. **Check server status:**
```bash
ldf mcp-health --server spec_inspector
```

---

### "MCP config not found"

**Error:**
```
ERROR: .agent/mcp.json not found
```

**Solution:**

```bash
mkdir -p .agent
ldf mcp-config > .agent/mcp.json
```

---

## Coverage Problems

### "Coverage data not found"

**Error:**
```
ERROR: No coverage data found. Run tests with coverage first.
```

**Cause:** Haven't run tests with coverage tracking.

**Solution:**

**Python (pytest):**
```bash
pytest --cov=your_package --cov-report=json
```

**Then:**
```bash
ldf coverage
```

---

### "Coverage below threshold"

**Error:**
```
ERROR: Coverage 75% is below required 80%
```

**Cause:** Test coverage doesn't meet target.

**Solutions:**

1. **Write more tests**
2. **Lower threshold (not recommended):**
```bash
ldf coverage --fail-under 70
```
3. **Check which files need coverage:**
```bash
ldf coverage --verbose
```

---

## Platform-Specific Issues

### macOS: VS Code "command not found" in terminal

**Cause:** VS Code shell integration not installed or PATH not loaded.

**Solution:**

1. **Install shell integration:**
   - Open VS Code
   - Press `Cmd + Shift + P`
   - Type: `shell command`
   - Select: "Shell Command: Install 'code' command in PATH"

2. **Restart VS Code completely** (Cmd+Q, then reopen)

3. **Check shell:**
```bash
echo $SHELL
```

If `/bin/bash`, edit `~/.bash_profile`
If `/bin/zsh`, edit `~/.zshrc`

---

### Windows: PowerShell execution policy blocks scripts

**Error:**
```
ldf : File cannot be loaded because running scripts is disabled on this system
```

**Solution:**

Run PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Explanation:** Allows local scripts, still protects against remote scripts.

---

### Linux: "externally-managed-environment" error

**Error:**
```
error: externally-managed-environment
```

**Cause:** Debian/Ubuntu blocks system-wide pip installs.

**Solution 1 - Use --user (recommended):**
```bash
pip3 install --user ldf
```

**Solution 2 - Use virtual environment:**
```bash
python3 -m venv ~/.venv/ldf
source ~/.venv/ldf/bin/activate
pip install llm-ldf
```

---

### Linux: SELinux blocks operations (Fedora/RHEL)

**Error:**
```
Permission denied (SELinux)
```

**Solution:**

**Temporary (for testing):**
```bash
sudo setenforce 0
```

**Permanent (less secure):**
```bash
sudo setsebool -P allow_execmem 1
```

**Best (create policy):**
```bash
# Run command that fails, then:
sudo audit2allow -a -M ldf
sudo semodule -i ldf.pp
```

---

## FAQ

### Q: Do I need to use all three phases for every feature?

**A:** No. Use LDF for significant features only.

**Use LDF for:**
- ✅ New features
- ✅ Security-sensitive changes
- ✅ Public APIs
- ✅ Database schema changes
- ✅ >200 lines of code

**Skip LDF for:**
- ❌ Bug fixes (link to issue)
- ❌ Documentation updates
- ❌ Config changes
- ❌ Small refactorings

---

### Q: What if I don't know the answer to a question-pack question?

**A:** Mark it as "TBD - needs research" in the answerpack YAML file, and add to "Outstanding Questions" section in requirements.md.

**Don't proceed to design phase** until all critical questions are answered.

**Why:** These questions surface critical decisions early when they're cheap to make.

---

### Q: Can I change requirements after approval?

**A:** Yes, but update the spec file and re-lint.

**Best practice:**
1. Update requirements.md
2. Run `ldf lint <spec>`
3. If design/tasks exist, update those too
4. Commit changes to version control

**The spec should always match what you're building.**

---

### Q: Do I really need the guardrail coverage matrix?

**A:** Yes - it's the most important part of requirements.md.

**Why:**
- Forces thinking about quality constraints upfront
- Prevents bugs by ensuring nothing is forgotten
- Makes review easier (reviewers can scan matrix)
- Tracks who owns each quality concern

**Many production bugs are prevented by properly filling this out.**

---

### Q: How detailed should requirements.md be?

**A:** Enough to answer "what" but not "how".

**Include:**
- User stories (As a... I want... So that...)
- Acceptance criteria (testable, measurable)
- Question-pack answer summaries
- Complete guardrail coverage matrix

**Don't include:**
- Implementation details (save for design.md)
- Specific code (save for tasks.md)
- Technology choices (save for design.md)

**Example:**

**Good:** "AC-1.1: Login returns 401 for invalid credentials"

**Too vague:** "AC-1.1: Login works correctly"

**Too detailed:** "AC-1.1: FastAPI route /login with bcrypt cost 12 returns HTTPException(401)"

---

### Q: What's the difference between `ldf init` and `ldf create-spec`?

**A:**

- **`ldf init`** - Run once per project to set up LDF
- **`ldf create-spec`** - Run once per feature to create a spec

**Example workflow:**
```bash
# Once: Set up project
ldf init

# Many times: Create specs for features
ldf create-spec user-auth
ldf create-spec payment-processing
ldf create-spec admin-dashboard
```

---

### Q: Can I use LDF without AI assistants?

**A:** Yes! LDF is a methodology, not an AI tool.

**LDF works great:**
- ✅ With AI (recommended - faster spec creation)
- ✅ Without AI (manual spec writing)
- ✅ Mixed (AI for specs, manual for code)

**The specs and guardrails work regardless of who writes them.**

---

### Q: Why is my lint failing but I see no errors?

**A:** Check for warnings in `--strict` mode.

**Try:**
```bash
ldf lint <spec> --strict
```

This fails on warnings, not just errors.

**Common warnings:**
- Missing optional sections
- Vague acceptance criteria
- No references to question-packs

---

### Q: How do I upgrade LDF?

**A:**
```bash
pip install --upgrade ldf
```

**Then update framework files in project:**
```bash
ldf update
```

---

### Q: Can I customize guardrails?

**A:** Yes! See [Customization Guide](../customization.md).

**You can:**
- Add custom guardrails
- Modify existing guardrails
- Create domain-specific presets
- Add custom question-packs

---

### Q: What if `ldf doctor` shows warnings?

**A:** Warnings are informational, not blocking.

**Common warnings:**
- Optional features not installed (MCP, automation, S3)
- Old framework files (run `ldf update`)
- Specs in progress (not errors)

**Only fix if impacting your workflow.**

---

## Getting More Help

### Check diagnostics
```bash
ldf doctor
```

### Search existing issues
https://github.com/LLMdotInfo/ldf/issues

### Report a bug
Include:
- LDF version (`ldf --version`)
- Python version (`python3 --version`)
- Operating system
- Complete error message
- Steps to reproduce
- Output from `ldf doctor`

### Join discussions
https://github.com/LLMdotInfo/ldf/discussions

---

## Related Documentation

- **[Installation Guides](../installation/)** - Platform-specific setup
- **[Command Reference](commands.md)** - All CLI commands
- **[First Spec Tutorial](../tutorials/01-first-spec.md)** - Hands-on walkthrough
- **[Guardrail Examples](../visual-guides/guardrail-examples.md)** - Real coverage matrices

---

**Still stuck?** Create an issue with the `question` label:
https://github.com/LLMdotInfo/ldf/issues/new
