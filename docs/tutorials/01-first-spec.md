# Tutorial: Your First LDF Spec

> **For**: Beginners who just installed LDF
> **Time**: 20 minutes
> **Prerequisites**: [LDF installed](../installation/) on your system
> **What you'll learn**: Create a simple spec, understand the three phases, validate it

---

## What We're Building

A simple **GET /hello** API endpoint that returns `{"message": "Hello, World!"}`.

This is the simplest possible LDF project - perfect for learning the workflow.

---

## Before You Start

Make sure you have:
- ✅ LDF installed (`ldf --version` works)
- ✅ A terminal/command prompt open
- ✅ VS Code or any text editor (optional but helpful)

**Terminal basics you'll need**:
- `cd` - Change directory (move between folders)
- `ls` (Mac/Linux) or `dir` (Windows) - List files in current folder
- `mkdir` - Make a new directory

---

## Step 1: Create a Project Directory

Let's create a folder for your first LDF project.

**On Mac/Linux:**
```bash
cd ~                          # Go to your home directory
mkdir my-first-ldf-project    # Create a new folder
cd my-first-ldf-project       # Enter the folder
```

**On Windows:**
```cmd
cd %USERPROFILE%              # Go to your home directory
mkdir my-first-ldf-project    # Create a new folder
cd my-first-ldf-project       # Enter the folder
```

**What just happened?**
- You created a new empty folder called `my-first-ldf-project`
- You're now "inside" that folder (your terminal's current location)

**Verify**: Run `pwd` (Mac/Linux) or `cd` (Windows) to see your current location:
```bash
# Mac/Linux
pwd
# Output: /Users/yourname/my-first-ldf-project

# Windows
cd
# Output: C:\Users\yourname\my-first-ldf-project
```

---

## Step 2: Initialize LDF

Now let's set up LDF in this project.

```bash
ldf init -y
```

**What's happening?**
- `ldf init` - Initialize LDF in the current folder
- `-y` - Skip the interactive prompts and use defaults (for simplicity)

**Expected output:**
```
Initializing LDF in /Users/yourname/my-first-ldf-project

Using defaults:
  Preset: custom (8 core guardrails)
  Question packs: security, testing, api-design, data-model
  MCP servers: Not enabled

✓ Created .ldf/ directory structure
✓ Created .ldf/config.yaml
✓ Created .ldf/guardrails.yaml
✓ Initialized templates
✓ Created AGENT.md

LDF initialization complete!
```

**What got created?**

Let's look at the folder structure now:

```bash
# Mac/Linux
ls -la

# Windows
dir
```

You'll see:
```
.ldf/                  # LDF configuration and specs go here
  ├── config.yaml      # Project settings
  ├── guardrails.yaml  # The 8 core quality rules
  ├── specs/           # Your feature specs will go here (empty for now)
  ├── templates/       # Spec templates
  ├── macros/          # Enforcement rules
  └── question-packs/  # Domain question templates

.agent/
  └── commands/        # Commands for AI assistants (if you use Claude Code, etc.)

AGENT.md               # Instructions for AI coding assistants
```

**The most important folder**: `.ldf/specs/` - This is where all your feature specifications will live.

---

## Step 3: Create Your First Spec

Now let's create a spec for our "hello world" endpoint.

```bash
ldf create-spec hello-world
```

**What's happening?**
- `create-spec` - Creates a new feature specification
- `hello-world` - The name of your spec (use lowercase with hyphens)

**Expected output:**
```
Creating spec: hello-world

✓ Created .ldf/specs/hello-world/
✓ Created requirements.md template

Next steps:
1. Edit .ldf/specs/hello-world/requirements.md
2. Answer question-packs (optional for this simple example)
3. Validate with: ldf lint hello-world
```

**What got created?**

```bash
# Look inside the new spec folder
ls .ldf/specs/hello-world/
```

You'll see:
```
requirements.md        # Template for Phase 1 (Requirements)
```

---

## Step 4: Write the Requirements

Let's edit the requirements file. Open it in your text editor:

**Using VS Code:**
```bash
code .ldf/specs/hello-world/requirements.md
```

**Using another editor:**
- Navigate to `.ldf/specs/hello-world/requirements.md`
- Open it with your preferred text editor

---

### Understanding the Template

You'll see a template with sections like this:

```markdown
# hello-world - Requirements

## Overview
[Brief description of what this feature does and why it's needed]

## User Stories

### US-1: [Story Title]

**As a** [role]
**I want to** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] AC-1.1: [Specific, testable criterion]
- [ ] AC-1.2: [Another criterion]

...
```

---

### Fill in the Requirements

**Replace the template content** with this simple example:

```markdown
# hello-world - Requirements

## Overview

A simple GET /hello endpoint that returns a JSON message. This is a minimal example to learn the LDF workflow.

## User Stories

### US-1: Hello Endpoint

**As a** developer testing the API
**I want to** call GET /hello
**So that** I can verify the API is running and responding correctly

**Acceptance Criteria:**
- [ ] AC-1.1: GET /hello returns HTTP 200 OK
- [ ] AC-1.2: Response body is JSON: `{"message": "Hello, World!"}`
- [ ] AC-1.3: Endpoint responds in less than 100ms
- [ ] AC-1.4: Endpoint is accessible without authentication

## Question-Pack Answers

For this simple example, we'll answer the most critical questions:

### Security
- **Authentication required?** No - this is a public read-only endpoint
- **Authorization model?** None - public endpoint
- **Secrets handling?** Not applicable

### Testing
- **Coverage target:** 80% (standard for non-critical endpoints)
- **Test types:** Integration test for the endpoint, unit test for response formatting

### API Design
- **Base path:** `/api/v1`
- **Endpoint:** `GET /hello`
- **Response format:** JSON
- **Error handling:** Return 500 with JSON error if server error occurs

### Data Model
- **Database required?** No - this endpoint doesn't touch a database

## Guardrail Coverage Matrix

This table shows how we're addressing each of the 8 core guardrails:

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [US-1: 80% target, integration + unit tests] | TBD | TBD | Dev | TODO |
| 2. Security Basics | [Public endpoint, no auth required per US-1] | TBD | TBD | Dev | TODO |
| 3. Error Handling | [AC-1.3: Return 500 on server errors] | TBD | TBD | Dev | TODO |
| 4. Logging & Observability | [Log all requests with timestamp, path] | TBD | TBD | Dev | TODO |
| 5. API Design | [US-1: /api/v1/hello, JSON response] | TBD | TBD | Dev | TODO |
| 6. Data Validation | N/A - No input parameters for this endpoint | N/A | N/A | - | N/A |
| 7. Database Migrations | N/A - No database access | N/A | N/A | - | N/A |
| 8. Documentation | [US-1: OpenAPI/Swagger docs auto-generated] | TBD | TBD | Dev | TODO |

**Note on "TBD" vs "N/A":**
- **TBD** (To Be Determined) - We'll fill this in during the Design and Tasks phases
- **N/A** (Not Applicable) - This guardrail doesn't apply to this feature, with a reason why

## Outstanding Questions

None - this is a simple endpoint with clear requirements.

## References

- REST API best practices: https://restfulapi.net/
- JSON response format: RFC 8259
```

**Save the file** (Ctrl+S or Cmd+S in VS Code).

---

### What You Just Created

Let's break down the requirements file:

1. **Overview** - A one-paragraph summary of what you're building
2. **User Stories** - Written as "As a [role], I want to [action], so that [benefit]"
3. **Acceptance Criteria** - Specific, testable conditions (AC-1.1, AC-1.2, etc.)
4. **Question-Pack Answers** - Key decisions made upfront (security, testing, API design)
5. **Guardrail Coverage Matrix** - Shows how you're addressing all 8 quality constraints
6. **Outstanding Questions** - Anything still unclear (none in this simple example)

---

## Step 5: Validate Your Spec

Now let's check if your requirements file is valid.

```bash
ldf lint hello-world
```

**What's happening?**
- `ldf lint` - Validate a spec
- `hello-world` - The name of the spec to check

**Expected output:**
```
Linting spec: hello-world
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Checking: .ldf/specs/hello-world/requirements.md
  ✓ File exists
  ✓ Overview section found
  ✓ User stories found: 1
  ✓ Acceptance criteria found: 4
  ✓ Guardrail coverage matrix present
  ✓ All 8 core guardrails accounted for (6 covered, 2 N/A with reasons)
  ✓ No template markers ([TBD], [TODO]) found in answerpack references

Checking: .ldf/specs/hello-world/design.md
  ⚠ File not yet created (expected - create after requirements approval)

Checking: .ldf/specs/hello-world/tasks.md
  ⚠ File not yet created (expected - create after design approval)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary: 0 errors, 2 warnings

Status: ✅ READY FOR DESIGN PHASE

Next steps:
1. Get requirements approval (team review, or AI audit via: ldf audit --type spec-review)
2. Create design.md
3. Create tasks.md
```

---

### Understanding the Output

**✓ Green checkmarks** - Everything that's required for Phase 1 (Requirements) is present and valid

**⚠ Warnings** - These are expected:
- `design.md` doesn't exist yet (we'll create it in Phase 2)
- `tasks.md` doesn't exist yet (we'll create it in Phase 3)

**Status: ✅ READY FOR DESIGN PHASE** - Your requirements are complete and valid!

---

## Step 6: Check Project Status

Let's see an overview of your entire LDF project:

```bash
ldf status
```

**Expected output:**
```
LDF Project Status
══════════════════════════════════════════════════════════════════════════════

Project: my-first-ldf-project
Preset: custom (8 core guardrails)
Specs: 1 total

Specs Overview:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Spec Name     Phase          Status    Guardrails  Tasks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
hello-world   requirements   valid     6/8 (2 N/A) 0/0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommendations:
  • hello-world: Ready for design phase - create design.md
```

---

## 🎉 Congratulations!

You've created your first valid LDF spec! Here's what you accomplished:

✅ Created an LDF project
✅ Initialized LDF configuration
✅ Created a feature spec
✅ Wrote requirements following the LDF format
✅ Filled out a guardrail coverage matrix
✅ Validated your spec with the linter

---

## Understanding the Three Phases

You've just completed **Phase 1: Requirements**. Here's the full LDF workflow:

```
┌─────────────────────────────────────────────┐
│ PHASE 1: REQUIREMENTS (✅ You are here!)    │
│                                             │
│ What to build:                              │
│ • User stories                              │
│ • Acceptance criteria                       │
│ • Question-pack answers                     │
│ • Guardrail coverage matrix                 │
│                                             │
│ Output: requirements.md                     │
│ Gate: ✋ Get approval before proceeding     │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ PHASE 2: DESIGN (Next step)                │
│                                             │
│ How to build it:                            │
│ • Architecture diagram                      │
│ • Component definitions                     │
│ • Data models                               │
│ • API contracts                             │
│                                             │
│ Output: design.md                           │
│ Gate: ✋ Get approval before proceeding     │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ PHASE 3: TASKS (Final step)                │
│                                             │
│ Implementation steps:                       │
│ • Numbered task list                        │
│ • Dependencies                              │
│ • Guardrail checklist per task              │
│                                             │
│ Output: tasks.md                            │
│ Status: ✅ READY TO IMPLEMENT               │
└─────────────────────────────────────────────┘
```

---

## What's Next?

You have several options:

### Option 1: Continue the Three-Phase Workflow (Recommended)

Complete the remaining two phases for your hello-world spec:

1. **Create design.md** - Define how to build the endpoint
   - API framework choice (FastAPI, Flask, Express, etc.)
   - Route definition
   - Response format
   - Error handling strategy
   - Logging approach

2. **Create tasks.md** - Break it into implementation steps
   - Task 1.1: Set up project structure
   - Task 1.2: Create /hello route
   - Task 2.1: Add error handling middleware
   - Task 2.2: Add logging
   - Task 3.1: Write integration tests
   - Task 3.2: Write unit tests
   - Task 4.1: Add OpenAPI documentation

3. **Implement** - Actually write the code following your tasks

---

### Option 2: Try Multi-Agent Review

Get feedback on your spec from ChatGPT or Gemini:

```bash
ldf audit --type spec-review
```

This generates a prompt you can copy-paste into ChatGPT/Gemini to get an external review of your requirements.

See [Tutorial: Multi-Agent Review](04-multi-agent-review.md) for details.

---

### Option 3: Explore More Complex Examples

Look at real-world examples in the `/examples/` directory:

```bash
# If you cloned the LDF repo
cd /path/to/ldf/examples/

# Examples available:
# • python-fastapi/ - FastAPI microservice
# • python-flask/ - Flask web app
# • python-django/ - Django application
# • typescript-node/ - TypeScript/Express API
# • go-service/ - Go microservice
```

Each example has complete specs (requirements.md, design.md, tasks.md).

---

### Option 4: Learn More Concepts

Read the conceptual guides:

- [Understanding Guardrails](../concepts.md#guardrails) - What each of the 8 guardrails means
- [Question-Packs Deep Dive](../answerpacks.md) - How to use question-packs effectively
- [When to Use LDF](../concepts.md#when-to-use-ldf) - Is LDF right for your project?

---

## Quick Reference: Commands You Learned

| Command | What it does |
|---------|--------------|
| `ldf init` | Set up LDF in a project (one time) |
| `ldf create-spec <name>` | Create a new spec |
| `ldf lint <name>` | Validate a spec |
| `ldf status` | Show overview of all specs |
| `ldf doctor` | Check LDF installation health |

---

## Common Questions

### Q: Do I have to fill out all three phases for every feature?

**A:** For significant features, yes. For tiny changes (bug fixes, typos), no.

**Use full LDF workflow for:**
- New features
- Security-sensitive changes
- Public APIs
- Database schema changes
- Anything with >200 lines of code

**Skip LDF for:**
- Bug fixes (link to GitHub issue instead)
- Documentation updates
- Configuration changes
- Tiny refactorings

### Q: What if I don't know the answer to a question-pack question?

**A:** Mark it as "TBD - needs research" and add to "Outstanding Questions" section. **Don't proceed to design** until answered. The whole point is to surface critical decisions early.

### Q: Can I change requirements after approval?

**A:** Yes, but update the spec file and re-lint. The spec should always match what you're building. Version control (git) tracks the history of changes.

### Q: Do I really need the guardrail coverage matrix?

**A:** Yes - it's the most important part! It forces you to think about quality constraints upfront. Many production bugs are prevented by filling this out properly.

---

## Troubleshooting

### Issue: ldf lint fails with "Guardrail matrix incomplete"

**Cause:** Missing guardrails in the table or didn't explain N/A.

**Solution:**
- Ensure all 8 core guardrails are in the table
- For N/A guardrails, add a reason: `N/A - No database used`

---

### Issue: Can't find the .ldf folder

**Cause:** Hidden files not shown in file explorer.

**Solution:**

**Mac Finder:**
- Press `Cmd + Shift + .` to show hidden files

**Windows Explorer:**
- View tab → Check "Hidden items"

**Terminal/Command Prompt:**
```bash
# Mac/Linux - list all files including hidden
ls -la

# Windows
dir /a
```

---

### Issue: ldf create-spec says "Not in an LDF project"

**Cause:** You're not in a directory that has been initialized with `ldf init`.

**Solution:**
```bash
# Check if you're in the right folder
ls .ldf

# If you see "No such file or directory", you're in the wrong folder
# Navigate to your project folder
cd /path/to/my-first-ldf-project

# Or initialize LDF in the current folder
ldf init
```

---

## Next Tutorial

Ready for more? Continue to:

**[Tutorial 2: Understanding Guardrails](02-guardrails.md)** - Deep dive into the 8 core quality constraints

Or jump to:
- [Tutorial 3: Working with Question-Packs](03-question-packs.md)
- [Tutorial 4: Multi-Agent Review Workflow](04-multi-agent-review.md)
- [Tutorial 5: MCP Setup for AI Assistants](05-mcp-setup.md)
