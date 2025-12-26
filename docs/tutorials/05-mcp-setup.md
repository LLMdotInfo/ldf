# Tutorial: MCP Setup for AI Assistants

> **For**: Users who want AI assistants to query LDF specs efficiently
> **Time**: 20 minutes
> **Prerequisites**: LDF project initialized, AI assistant that supports MCP (Claude Code, etc.)
> **What you'll learn**: Set up MCP servers, query specs from AI, achieve 90% token reduction

---

## What is MCP?

**MCP (Model Context Protocol)** is a standard for AI assistants to access external data sources efficiently.

### The Problem MCP Solves

**Without MCP:**

```
You: "What's the status of the user-auth spec?"

Claude Code:
1. Reads .ldf/specs/user-auth/requirements.md (5,000 tokens)
2. Reads .ldf/specs/user-auth/design.md (8,000 tokens)
3. Reads .ldf/specs/user-auth/tasks.md (6,000 tokens)
4. Reads .ldf/answerpacks/user-auth/*.yaml (3,000 tokens)
5. Total: 22,000 tokens consumed

Response: "user-auth is in the design phase with 12 tasks."
```

**Cost:** 22,000 input tokens (~$0.66 with GPT-4)
**Latency:** 3-5 seconds to read all files

---

**With MCP:**

```
You: "What's the status of the user-auth spec?"

Claude Code:
1. Calls MCP tool: spec_inspector.get_status("user-auth")
2. Receives structured response: { phase: "design", tasks: 12, status: "valid" }
3. Total: ~500 tokens (just the tool call + response)

Response: "user-auth is in the design phase with 12 tasks."
```

**Cost:** ~500 tokens (~$0.015 with GPT-4)
**Latency:** <1 second

**Savings:** 97.7% fewer tokens, 5x faster

---

### How MCP Works

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Assistant (Claude Code)               │
│                                                             │
│  User asks: "What specs are ready for review?"             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ MCP Tool Call
                 │ Tool: spec_inspector.list_specs(status="ready")
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                 MCP Server (spec_inspector)                 │
│                                                             │
│  1. Query .ldf/specs/ directory                            │
│  2. Parse each spec's status                               │
│  3. Filter by status="ready"                               │
│  4. Return structured JSON                                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ JSON Response
                 │ { "specs": ["user-auth", "payment-flow"] }
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Assistant                             │
│                                                             │
│  Response: "2 specs are ready for review:                  │
│             • user-auth                                     │
│             • payment-flow"                                 │
└─────────────────────────────────────────────────────────────┘
```

**Key insight:** Instead of reading entire files, AI calls specialized tools that return only the needed information.

---

## LDF's MCP Servers

LDF includes 2 MCP servers:

| Server | Purpose | Tools Provided |
|--------|---------|----------------|
| **spec_inspector** | Query spec status, structure, guardrails | `list_specs`, `get_spec_status`, `get_guardrail_coverage`, `search_specs` |
| **coverage_reporter** | Query test coverage data | `get_coverage`, `get_spec_coverage`, `compare_coverage` |

---

## Prerequisites

### 1. LDF Installed

```bash
ldf --version
# Should show: ldf version 1.0.0 or higher
```

### 2. AI Assistant with MCP Support

Currently supported:
- **Claude Code** (Anthropic's CLI) ✅
- **VS Code + Claude Extension** ✅ (experimental)
- More coming soon

**Check Claude Code:**
```bash
# If you don't have Claude Code, install it:
# See: https://docs.anthropic.com/claude-code

claude --version
```

---

## Step 1: Install MCP Extras

LDF's MCP servers require additional Python packages.

```bash
pip install llm-ldf[mcp]
```

**What gets installed:**
- `mcp` - Model Context Protocol SDK
- `pydantic` - Data validation for tool responses
- `uvloop` - High-performance event loop (optional, for speed)

**Verify installation:**

```bash
ldf mcp-health
```

**Expected output:**
```
MCP Server Health Check
=======================

spec_inspector:     ✓ Healthy
coverage_reporter:  ✓ Healthy

All MCP servers operational.
```

---

## Step 2: Generate MCP Configuration

Create an MCP configuration file for your AI assistant.

```bash
mkdir -p .agent
ldf mcp-config > .agent/mcp.json
```

**What's created:** `.agent/mcp.json`

**Contents:**

```json
{
  "mcpServers": {
    "spec_inspector": {
      "command": "ldf",
      "args": ["mcp", "serve", "spec_inspector"],
      "env": {
        "LDF_PROJECT_ROOT": "/Users/yourname/my-ldf-project"
      }
    },
    "coverage_reporter": {
      "command": "ldf",
      "args": ["mcp", "serve", "coverage_reporter"],
      "env": {
        "LDF_PROJECT_ROOT": "/Users/yourname/my-ldf-project"
      }
    }
  }
}
```

**Key parts:**
- `command`: Executable to run (`ldf`)
- `args`: Arguments to start the MCP server
- `env.LDF_PROJECT_ROOT`: Absolute path to your LDF project (auto-detected)

---

## Step 3: Configure Claude Code

Tell Claude Code about your MCP servers.

### Option A: Project-Level Config (Recommended)

Claude Code automatically discovers `.agent/mcp.json` if it's in your project root.

**Verify:**
```bash
# In your project directory
ls .agent/mcp.json
# Should exist

# Start Claude Code
claude

# In Claude Code session, ask:
"What MCP tools do you have access to?"
```

Claude should respond with tools from spec_inspector and coverage_reporter.

---

### Option B: Global Config

To use LDF MCP servers in all projects:

**macOS/Linux:**
```bash
# Copy to Claude Code config directory
mkdir -p ~/.config/claude-code/mcp
cp .agent/mcp.json ~/.config/claude-code/mcp/ldf.json
```

**Windows:**
```cmd
mkdir %APPDATA%\claude-code\mcp
copy .agent\mcp.json %APPDATA%\claude-code\mcp\ldf.json
```

---

## Step 4: Test MCP Integration

Let's verify the MCP servers work.

### Start Claude Code

```bash
# Navigate to your LDF project
cd /path/to/my-ldf-project

# Start Claude Code
claude
```

---

### Query 1: List All Specs

**You:**
```
What LDF specs exist in this project?
```

**Claude Code (using spec_inspector.list_specs):**
```
I found 3 specs in this project:

1. **user-auth**
   - Phase: Requirements
   - Status: Valid
   - Guardrails: 8/8 covered

2. **payment-flow**
   - Phase: Design
   - Status: Valid
   - Guardrails: 13/13 covered (SaaS preset)

3. **admin-dashboard**
   - Phase: Tasks
   - Status: In progress
   - Tasks: 7/15 complete
```

**Behind the scenes:**
```json
// MCP Tool Call
{
  "tool": "spec_inspector.list_specs",
  "args": {}
}

// MCP Response
{
  "specs": [
    {
      "name": "user-auth",
      "phase": "requirements",
      "status": "valid",
      "guardrails_covered": 8,
      "guardrails_total": 8
    },
    // ... more specs
  ]
}
```

---

### Query 2: Get Spec Status

**You:**
```
What's the status of the user-auth spec?
```

**Claude Code (using spec_inspector.get_spec_status):**
```
Status of user-auth spec:

**Phase:** Requirements (ready for design)
**Validation:** ✅ Valid

**User Stories:** 2
  - US-1: User Login (4 acceptance criteria)
  - US-2: Password Reset (3 acceptance criteria)

**Guardrail Coverage:** 8/8 (100%)
  - All core guardrails addressed
  - 0 marked N/A

**Question-Packs Answered:** 4
  - security.yaml ✅
  - testing.yaml ✅
  - api-design.yaml ✅
  - data-model.yaml ✅

**Next Steps:** Create design.md
```

**Token savings:** Instead of reading 5,000-token requirements.md, used ~200-token tool response.

---

### Query 3: Check Guardrail Coverage

**You:**
```
Which guardrails are not yet addressed in the payment-flow spec?
```

**Claude Code (using spec_inspector.get_guardrail_coverage):**
```
Guardrail coverage for payment-flow:

**Fully Addressed (11/13):**
✅ 1. Testing Coverage
✅ 2. Security Basics
✅ 3. Error Handling
✅ 4. Logging & Observability
✅ 5. API Design
✅ 6. Data Validation
✅ 7. Database Migrations
✅ 8. Documentation
✅ 9. Multi-Tenancy (RLS)
✅ 10. Tenant Isolation
✅ 11. Subscription Management

**Not Yet Addressed (2/13):**
⚠️ 12. Usage Metering - Marked TBD in requirements
⚠️ 13. Data Export - Missing from requirements

**Recommendation:** Address guardrails 12 and 13 before moving to design phase.
```

---

### Query 4: Search Across Specs

**You:**
```
Which specs mention Stripe?
```

**Claude Code (using spec_inspector.search_specs):**
```
Found "Stripe" in 2 specs:

1. **payment-flow** (3 mentions)
   - requirements.md: "Payment gateway: Stripe"
   - design.md: "Stripe SDK integration"
   - answerpacks/billing.yaml: "payment_gateway: Stripe"

2. **subscription-management** (2 mentions)
   - requirements.md: "Stripe webhooks for subscription events"
   - answerpacks/billing.yaml: "subscription_model: Stripe Billing"
```

**Use case:** Find all specs affected by a technology change (e.g., migrating from Stripe to a different provider).

---

## Step 5: Using Coverage Reporter

The `coverage_reporter` MCP server provides test coverage insights.

### Prerequisites

Run your tests with coverage first:

**Python (pytest):**
```bash
pytest --cov=your_package --cov-report=json
```

**JavaScript (Jest):**
```bash
jest --coverage --coverageReporters=json
```

This creates a `coverage.json` file.

---

### Query Coverage

**You:**
```
What's the current test coverage?
```

**Claude Code (using coverage_reporter.get_coverage):**
```
Test Coverage Report
====================

**Overall:** 87.5% (target: 80%) ✅

**By Module:**
- src/auth/: 92.1% ✅
- src/payments/: 81.3% ✅
- src/admin/: 78.4% ⚠️ (below 80%)
- src/utils/: 95.2% ✅

**Files Below Target:**
1. src/admin/dashboard.py: 68.2%
   - Missing: Error handling paths
2. src/admin/reports.py: 73.1%
   - Missing: Edge cases (empty data)

**Recommendation:** Add tests for src/admin/ to reach 80% target.
```

---

### Coverage by Spec

**You:**
```
What's the coverage for the user-auth spec?
```

**Claude Code (using coverage_reporter.get_spec_coverage):**
```
Coverage for user-auth spec:

**Overall:** 91.2% ✅ (target: 90%)

**By Component:**
- AuthService: 95.3%
- PasswordHasher: 100%
- JWTGenerator: 89.1%
- RateLimiter: 87.5%

**Acceptance Criteria Coverage:**
✅ AC-1.1: Login with valid credentials - Covered (test_login_success)
✅ AC-1.2: Invalid credentials return 401 - Covered (test_login_invalid)
✅ AC-1.5: Rate limiting - Covered (test_rate_limit_exceeded)
⚠️ AC-1.6: Account lockout - Partially covered (missing unlock after 1 hour)

**Gaps:**
- Account unlock after timeout (AC-1.6)
- Concurrent login attempts (edge case)

**Recommendation:** Add test_account_unlock_after_timeout.
```

---

## Advanced: Custom MCP Tools

You can extend LDF's MCP servers with custom tools.

### Create Custom Tool

**File:** `.ldf/mcp/custom_tools.py`

```python
from ldf.mcp import MCPTool

class GetHighPriorityTasksTool(MCPTool):
    name = "get_high_priority_tasks"
    description = "Get all high-priority tasks across all specs"

    def execute(self, args):
        """Find tasks marked with [HIGH PRIORITY] or [CRITICAL]"""
        high_priority_tasks = []

        for spec in self.get_all_specs():
            tasks_file = self.get_spec_file(spec, "tasks.md")
            if not tasks_file:
                continue

            for line in tasks_file.lines():
                if "[HIGH PRIORITY]" in line or "[CRITICAL]" in line:
                    high_priority_tasks.append({
                        "spec": spec,
                        "task": line.strip(),
                        "completed": "[x]" in line.lower()
                    })

        return {
            "total": len(high_priority_tasks),
            "uncompleted": len([t for t in high_priority_tasks if not t["completed"]]),
            "tasks": high_priority_tasks
        }
```

### Register Custom Tool

**File:** `.ldf/config.yaml`

```yaml
mcp:
  servers:
    spec_inspector:
      enabled: true
      custom_tools:
        - .ldf/mcp/custom_tools.py::GetHighPriorityTasksTool
```

### Use Custom Tool

**You:**
```
What are the high-priority tasks?
```

**Claude Code:**
```
Found 5 high-priority tasks:

**Uncompleted (3):**
1. [user-auth] Task 2.1: Implement rate limiting [HIGH PRIORITY]
2. [payment-flow] Task 1.3: Add fraud detection rules [CRITICAL]
3. [admin-dashboard] Task 3.2: Add audit logging [HIGH PRIORITY]

**Completed (2):**
✅ [user-auth] Task 1.1: Set up database migrations [HIGH PRIORITY]
✅ [payment-flow] Task 2.2: Implement idempotency [CRITICAL]
```

---

## Troubleshooting

### Issue: "MCP servers not found"

**Error:**
```
Claude Code: I don't have access to any LDF MCP tools.
```

**Solution:**

1. **Check .agent/mcp.json exists:**
   ```bash
   ls .agent/mcp.json
   # If not found, run: ldf mcp-config > .agent/mcp.json
   ```

2. **Verify MCP extras installed:**
   ```bash
   ldf mcp-health
   # If unhealthy, run: pip install llm-ldf[mcp]
   ```

3. **Restart Claude Code:**
   ```bash
   # Exit current session
   exit

   # Start new session
   claude
   ```

---

### Issue: "Tool call failed"

**Error:**
```
Error calling spec_inspector.get_spec_status: Spec not found
```

**Solution:**

1. **Check spec exists:**
   ```bash
   ls .ldf/specs/
   # Ensure the spec name is spelled correctly
   ```

2. **Check LDF_PROJECT_ROOT:**
   ```bash
   cat .agent/mcp.json | grep LDF_PROJECT_ROOT
   # Should point to your project root
   ```

3. **Regenerate config:**
   ```bash
   ldf mcp-config > .agent/mcp.json
   ```

---

### Issue: High latency on tool calls

**Symptom:** MCP tools take 5-10 seconds to respond

**Solution:**

1. **Check if coverage.json is huge:**
   ```bash
   ls -lh coverage.json
   # If >10 MB, coverage data might be too large
   ```

2. **Exclude test files from coverage:**
   ```bash
   # In pytest.ini or .coveragerc
   [coverage:run]
   omit = tests/*
   ```

3. **Use summary-only coverage:**
   ```bash
   pytest --cov=your_package --cov-report=term
   # Then manually create lightweight coverage.json
   ```

---

## Best Practices

### 1. Keep MCP Config in Version Control

**In .gitignore:**
```gitignore
# Don't ignore .agent/mcp.json - it's project config
!.agent/mcp.json

# But ignore personal AI assistant settings
.agent/personal-settings.json
```

**Why:** Team members can use MCP immediately after cloning the repo.

---

### 2. Use MCP for Frequent Queries

**Good MCP use cases:**
- "What specs are ready for review?"
- "Which tasks are incomplete in the user-auth spec?"
- "What's the current coverage?"
- "Which specs use PostgreSQL?"

**Bad MCP use cases:**
- "Read the full requirements.md for user-auth" (just use Read tool)
- "Show me all acceptance criteria" (too broad, MCP overhead not worth it)

**Rule:** Use MCP for **queries and filters**, use Read for **full content**.

---

### 3. Combine MCP with Direct File Access

**Efficient workflow:**

```
You: "Which spec has the most incomplete tasks?"

Claude (MCP query):
- spec_inspector.list_specs()
- Result: "payment-flow has 8/15 tasks incomplete"

You: "Show me those incomplete tasks"

Claude (Read tool):
- Read .ldf/specs/payment-flow/tasks.md
- Shows full task list with details
```

**Why:** MCP for discovery, Read for details.

---

## Real-World Use Case: Sprint Planning

**Scenario:** Weekly sprint planning meeting

**You:**
```
Help me plan this week's sprint. Show me:
1. Specs ready for implementation
2. High-priority incomplete tasks
3. Current coverage gaps
```

**Claude Code (using MCP):**

```
Sprint Planning Summary
=======================

## 1. Specs Ready for Implementation (2)

**user-auth** ✅
- Phase: Complete (requirements + design + tasks)
- Tasks: 0/12 started
- Priority: HIGH
- Estimated effort: 3 days

**payment-flow** ✅
- Phase: Complete
- Tasks: 0/18 started
- Priority: CRITICAL
- Estimated effort: 5 days

## 2. High-Priority Incomplete Tasks (5)

From in-progress specs:

1. **admin-dashboard** - Task 2.3: Add audit logging [CRITICAL]
   - Blockers: None
   - Estimated: 4 hours

2. **email-notifications** - Task 1.2: Set up SendGrid [HIGH]
   - Blockers: Need SendGrid API key
   - Estimated: 2 hours

... (3 more) ...

## 3. Coverage Gaps

**Below 80% Target:**
- src/admin/: 78.4% (-1.6%)
- src/webhooks/: 76.1% (-3.9%)

**Recommendation:** Allocate 1 day for test writing this sprint.

## Suggested Sprint Plan

**Day 1-2:** Complete admin-dashboard critical tasks
**Day 3-5:** Start payment-flow implementation (highest business value)
**Day 5:** Coverage improvement session
```

**Token savings:** Instead of manually reading 10+ files (~50,000 tokens), used ~2,000 tokens via MCP tools.

**Time savings:** 5-minute meeting prep instead of 30 minutes.

---

## Next Steps

Now that you've set up MCP:

1. **Practice:** Ask Claude Code to analyze your LDF project
2. **Experiment:** Try different queries to see what MCP tools can do
3. **Advanced:** Create custom MCP tools for your team's specific workflows
4. **Review:** Go back to [Multi-Agent Review](04-multi-agent-review.md) and use MCP for faster spec queries

---

## Quick Reference: MCP Tools

### spec_inspector Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `list_specs` | List all specs | "What specs exist?" |
| `get_spec_status` | Get detailed spec info | "Status of user-auth?" |
| `get_guardrail_coverage` | Check guardrail matrix | "Which guardrails are missing?" |
| `search_specs` | Full-text search | "Which specs mention Redis?" |

### coverage_reporter Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `get_coverage` | Overall coverage stats | "What's our test coverage?" |
| `get_spec_coverage` | Coverage for one spec | "Coverage for user-auth?" |
| `compare_coverage` | Compare with baseline | "Did coverage improve?" |

---

## Summary

You've learned:

✅ What MCP is and why it saves 90% tokens
✅ How to install LDF MCP extras
✅ How to generate and configure mcp.json
✅ How to query specs using spec_inspector
✅ How to query coverage using coverage_reporter
✅ When to use MCP vs direct file reading

**Result:** Faster AI interactions, lower costs, better developer experience.

---

**Congratulations!** You've completed all 5 LDF tutorials. You now know:

1. [How to create your first spec](01-first-spec.md)
2. [How to use guardrails effectively](02-guardrails.md)
3. [How to work with question-packs](03-question-packs.md)
4. [How to get multi-agent reviews](04-multi-agent-review.md)
5. [How to set up MCP for AI assistants](05-mcp-setup.md)

**Next:** Start using LDF on a real project! See [Getting Started](../getting-started.md) for production workflows.
