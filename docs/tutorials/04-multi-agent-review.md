# Tutorial: Multi-Agent Review Workflow

> **For**: Users with completed specs ready for review
> **Time**: 30 minutes
> **Prerequisites**: [Working with Question-Packs](03-question-packs.md), completed spec
> **What you'll learn**: Get external AI review of your specs, import feedback, iterate to improve quality

---

## Why Get AI Review of AI-Generated Specs?

**Paradox:** If AI helped you write the spec, why ask another AI to review it?

**Answer:** Different perspectives catch different issues.

### The Multi-Agent Advantage

**Analogy:** Peer code review

In traditional development:
- **You write code** (with your biases, blind spots)
- **Colleague reviews code** (fresh eyes, different experience)
- **Result:** Bugs caught before production

In LDF:
- **Agent 1 (Claude Code) writes spec** with you
- **Agent 2 (ChatGPT/Gemini) reviews spec** independently
- **Result:** Gaps, edge cases, and assumptions caught before coding

---

### What AI Reviewers Catch

Real examples from multi-agent reviews:

#### Gap Analysis

**Your spec (written with Claude):**
```markdown
### US-1: User Login
- [ ] AC-1.1: Returns 200 + JWT on valid credentials
- [ ] AC-1.2: Returns 401 on invalid credentials
```

**ChatGPT review:**
```
GAPS IDENTIFIED:
1. No rate limiting mentioned - vulnerable to brute force
2. No account lockout after failed attempts
3. No password reset flow
4. No "remember me" option mentioned
5. What happens if user is already logged in?
```

**Result:** 5 missing requirements caught before coding!

---

#### Edge Cases

**Your spec:**
```markdown
### US-2: File Upload
- [ ] AC-2.1: Accepts .jpg, .png, .pdf files
- [ ] AC-2.2: Max 10 MB per file
```

**Gemini review:**
```
EDGE CASES TO CONSIDER:
1. What if file extension is uppercase (.JPG)?
2. What if malicious file has fake extension (virus.jpg.exe)?
3. What if user uploads 1000 files at once?
4. What if file is exactly 10 MB vs 10 MB + 1 byte?
5. What about animated GIFs or HEIC (Apple) format?
6. What if upload is interrupted mid-transfer?
```

**Result:** 6 edge cases to add to acceptance criteria!

---

#### Security Issues

**Your spec:**
```markdown
### Security
- Auth method: JWT
- Password storage: bcrypt cost 12
```

**ChatGPT security audit:**
```
SECURITY CONCERNS:
1. No HTTPS enforcement mentioned - JWTs can be intercepted
2. No CORS policy defined - vulnerable to XSS
3. No mention of JWT secret rotation strategy
4. No SQL injection prevention mentioned
5. No XSS sanitization for user inputs
6. No CSRF protection for state-changing endpoints
```

**Result:** 6 security gaps to address!

---

## The Multi-Agent Workflow

```
┌──────────────────────────────────────────────────────┐
│  STEP 1: Create Spec with Claude Code              │
│  (You + Agent 1)                                     │
│                                                      │
│  Output: requirements.md, answerpacks               │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│  STEP 2: Generate Audit Request                     │
│  (LDF CLI)                                           │
│                                                      │
│  $ ldf audit --type spec-review --agent chatgpt     │
│  Output: audit-request.md                           │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│  STEP 3: Submit to External AI                      │
│  (ChatGPT, Gemini, Claude via web)                  │
│                                                      │
│  Copy audit-request.md → Paste in ChatGPT           │
│  Save response → feedback.md                         │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│  STEP 4: Import Feedback                            │
│  (LDF CLI)                                           │
│                                                      │
│  $ ldf audit --import feedback.md                   │
│  Updates: requirements.md with new ACs              │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│  STEP 5: Iterate & Re-Review                        │
│  (You)                                               │
│                                                      │
│  Review changes, accept/reject suggestions           │
│  Re-lint, repeat if needed                          │
└──────────────────────────────────────────────────────┘
```

---

## Step 1: Create Your Spec

Start with a complete spec (requirements.md + answerpacks):

**Example:** User authentication spec from previous tutorials

```bash
# Create spec
ldf create-spec user-auth

# Fill out requirements.md
# Create answerpacks (security, testing, etc.)

# Validate
ldf lint user-auth
# ✅ READY FOR DESIGN PHASE
```

---

## Step 2: Generate Audit Request

Use the `ldf audit` command to create a review prompt for an external AI.

### Basic Spec Review

```bash
ldf audit --type spec-review --agent chatgpt > audit-request.md
```

**Options:**
- `--type`: Type of audit (see table below)
- `--agent`: Target AI agent (`chatgpt`, `gemini`, `claude-web`)

**Output:** `audit-request.md` - A formatted prompt for the AI

---

### Audit Types

| Type | Purpose | What It Checks |
|------|---------|----------------|
| `spec-review` | General review | Completeness, clarity, consistency |
| `gap-analysis` | Find missing requirements | Edge cases, error scenarios, unhappy paths |
| `security` | Security audit | OWASP Top 10, auth issues, data exposure |
| `edge-cases` | Edge case identification | Boundary conditions, race conditions, null/empty states |
| `architecture` | Architecture review | Scalability, performance, design patterns |
| `pre-launch` | Comprehensive check | All of the above + production readiness |

---

### Example: Gap Analysis

```bash
ldf audit --type gap-analysis --agent chatgpt > gap-analysis-request.md
```

**Generated prompt (gap-analysis-request.md):**

````markdown
# Gap Analysis Request for LDF Spec: user-auth

You are an expert software architect reviewing a feature specification. Your task is to identify **gaps** in the requirements - things that are missing, under-specified, or not considered.

## Instructions

1. Read the spec below carefully
2. Identify gaps in these categories:
   - **Missing requirements**: Scenarios not covered
   - **Edge cases**: Boundary conditions not addressed
   - **Error handling**: Failure modes not specified
   - **Security**: Security considerations missing
   - **Performance**: Scalability concerns not mentioned
   - **UX**: User experience gaps

3. For each gap, provide:
   - **Category**: (e.g., Missing requirement, Edge case)
   - **Description**: What's missing
   - **Impact**: Why it matters
   - **Suggestion**: Specific acceptance criterion to add

## Spec to Review

```markdown
# user-auth - Requirements

## Overview
Email/password authentication with JWT tokens.

## User Stories

### US-1: User Login
**As a** registered user
**I want to** log in with email and password
**So that** I can access my account

**Acceptance Criteria:**
- [ ] AC-1.1: Returns 200 + JWT on valid credentials
- [ ] AC-1.2: Returns 401 on invalid credentials

... (full spec content) ...
```

## Output Format

Please structure your response as:

### Gap 1: [Category] - [Brief title]
**Description:** [What's missing]
**Impact:** [Why it matters]
**Suggested AC:** [Specific acceptance criterion]

**Example:**
### Gap 1: Security - No Rate Limiting
**Description:** No rate limiting on login endpoint, vulnerable to brute force attacks
**Impact:** Attacker could try millions of passwords per minute
**Suggested AC:** AC-1.5: Login endpoint rate limited to 5 attempts per 15 minutes per IP address
````

---

## Step 3: Submit to External AI

Copy the audit request and submit to your chosen AI.

### Using ChatGPT

1. **Open ChatGPT** (https://chat.openai.com)
2. **Start new chat**
3. **Paste** the entire contents of `audit-request.md`
4. **Wait** for response (30-60 seconds)
5. **Copy response** to `feedback.md`

**Example ChatGPT response:**

```markdown
### Gap 1: Security - No Rate Limiting
**Description:** No rate limiting on login endpoint
**Impact:** Vulnerable to brute force attacks
**Suggested AC:** AC-1.5: Rate limit to 5 login attempts per 15 minutes per IP

### Gap 2: Missing Requirement - Account Lockout
**Description:** No account lockout after repeated failed attempts
**Impact:** Attacker can keep trying passwords indefinitely
**Suggested AC:** AC-1.6: Lock account for 1 hour after 10 failed login attempts

### Gap 3: Edge Case - Already Logged In
**Description:** Behavior not specified if user is already logged in
**Impact:** Could create multiple sessions, token conflicts
**Suggested AC:** AC-1.7: If user already has valid token, return existing token or error

### Gap 4: Error Handling - Database Unreachable
**Description:** No handling for database connection failures
**Impact:** User sees 500 error instead of helpful message
**Suggested AC:** AC-1.8: Return 503 Service Unavailable if database is unreachable

### Gap 5: UX - No "Forgot Password" Flow
**Description:** No password reset mechanism mentioned
**Impact:** Users locked out if they forget password
**Suggested AC:** New US-2: Password Reset Flow (link on login page)

... (10-20 more gaps) ...
```

---

### Using Gemini

1. **Open Gemini** (https://gemini.google.com)
2. **Start new chat**
3. **Paste** audit request
4. **Wait** for response
5. **Save** to `feedback-gemini.md`

**Tip:** Gemini tends to find different gaps than ChatGPT - use both for comprehensive review!

---

### Using Claude (Web Interface)

1. **Open Claude** (https://claude.ai)
2. **Start new chat**
3. **Paste** audit request
4. **Save** response

**Note:** This is different from Claude Code (the CLI). Using web Claude gives you a "third opinion" beyond the Claude Code agent that helped write the spec.

---

## Step 4: Import Feedback

LDF can automatically import structured feedback and suggest changes to your spec.

### Preview Changes (Dry Run)

```bash
ldf audit --import feedback.md --dry-run
```

**Output:**
```
Analyzing feedback from: feedback.md

Found 15 suggestions:
  - 7 new acceptance criteria
  - 3 new user stories
  - 2 security question-pack updates
  - 2 guardrail matrix updates
  - 1 design consideration

Suggested changes to .ldf/specs/user-auth/requirements.md:

  [+] AC-1.5: Rate limit to 5 login attempts per 15 minutes per IP
  [+] AC-1.6: Lock account for 1 hour after 10 failed login attempts
  [+] AC-1.7: If user already has valid token, return existing token
  [+] AC-1.8: Return 503 Service Unavailable if database unreachable
  [+] US-2: Password Reset Flow

Suggested changes to .ldf/answerpacks/user-auth/security.yaml:

  [+] rate_limiting: 5 attempts per 15 min per IP
  [+] account_lockout: 10 failed attempts, 1 hour lockout

Suggested changes to guardrail coverage matrix:

  [M] Guardrail 2 (Security): Add [AC-1.5, AC-1.6: Rate limiting, account lockout]
  [M] Guardrail 3 (Error Handling): Add [AC-1.8: Handle DB unreachable]

Run without --dry-run to apply changes.
```

---

### Apply Changes

```bash
ldf audit --import feedback.md
```

**Output:**
```
Importing feedback from: feedback.md

✓ Updated .ldf/specs/user-auth/requirements.md
  - Added 4 new acceptance criteria to US-1
  - Added new user story US-2: Password Reset Flow
  - Updated guardrail coverage matrix

✓ Updated .ldf/answerpacks/user-auth/security.yaml
  - Added rate_limiting answer
  - Added account_lockout answer

✓ Created .ldf/specs/user-auth/feedback-log.md
  - Documented all imported suggestions
  - Includes rejected suggestions with reasons

Changes applied. Next steps:
  1. Review changes: git diff .ldf/specs/user-auth/
  2. Validate: ldf lint user-auth
  3. Commit: git add . && git commit -m "Apply AI audit feedback"
```

---

## Step 5: Review and Iterate

### Review the Changes

```bash
# See what changed
git diff .ldf/specs/user-auth/requirements.md
```

**Example diff:**

```diff
 ### US-1: User Login
 **Acceptance Criteria:**
 - [ ] AC-1.1: Returns 200 + JWT on valid credentials
 - [ ] AC-1.2: Returns 401 on invalid credentials
+- [ ] AC-1.5: Rate limited to 5 login attempts per 15 minutes per IP
+- [ ] AC-1.6: Account locked for 1 hour after 10 failed attempts
+- [ ] AC-1.7: If user already logged in, return existing token
+- [ ] AC-1.8: Returns 503 Service Unavailable if database unreachable

+### US-2: Password Reset Flow
+**As a** user who forgot password
+**I want to** reset my password via email
+**So that** I can regain access to my account
+
+**Acceptance Criteria:**
+- [ ] AC-2.1: "Forgot password" link on login page
+- [ ] AC-2.2: Sends email with time-limited reset token (1 hour expiry)
+- [ ] AC-2.3: Reset token single-use only
```

---

### Accept or Reject Suggestions

Not all suggestions may be valid. Review each one:

**Accept:** Keep the change

**Reject:** Remove from requirements.md, document why in `feedback-log.md`

**Example rejection:**

```markdown
# feedback-log.md

## Rejected Suggestions

### Gap 12: UX - Remember Me Checkbox
**Reason for rejection:** Out of scope for MVP. Will add in v2.
**Decided by:** Product team
**Date:** 2024-01-15
```

---

### Validate

After making changes, re-lint:

```bash
ldf lint user-auth
```

**Expected output:**
```
Linting spec: user-auth
✓ requirements.md: valid (8 user stories, 24 acceptance criteria)
✓ Guardrail coverage matrix complete
✓ All question-packs referenced

Status: ✅ READY FOR DESIGN PHASE
```

---

### Iterate (Optional)

If major changes were made, consider a second review:

```bash
# Generate new audit request with updated spec
ldf audit --type security --agent gemini > security-audit-v2.md

# Submit to Gemini, get feedback-v2.md

# Import second round of feedback
ldf audit --import feedback-v2.md
```

**When to iterate:**
- First review found >20 gaps
- Major changes to requirements
- High-risk features (security, payments, healthcare)
- Team wants second opinion

**When one review is enough:**
- <10 gaps found
- Changes are minor
- Low-risk features

---

## Advanced: API-Based Audits

**Requires:** `ldf[automation]` package

Instead of manual copy-paste, automate the review:

```bash
# Install automation extras
pip install llm-ldf[automation]

# Set API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Run automated audit
ldf audit --api --type security --agent chatgpt
```

**What happens:**
1. LDF generates audit request
2. Sends to ChatGPT API automatically
3. Receives response
4. Parses feedback
5. Suggests changes (--dry-run by default)

**Cost:** ~$0.10-0.50 per audit (depending on spec size)

**Benefits:**
- Faster (no copy-paste)
- Can run in CI/CD pipelines
- Consistent formatting

**Setup:**

```bash
# 1. Install extras
pip install llm-ldf[automation]

# 2. Configure API keys
# Option A: Environment variables
export OPENAI_API_KEY="sk-..."

# Option B: .env file (don't commit!)
echo "OPENAI_API_KEY=sk-..." >> .env

# 3. Run API audit
ldf audit --api --type gap-analysis --agent chatgpt

# 4. Review and apply
ldf audit --apply-last  # Apply the last API audit
```

---

## Real-World Example: Payment Feature Audit

Let's walk through a complete multi-agent review for a payment feature.

### Initial Spec (Before Review)

```markdown
# stripe-payments - Requirements

## User Stories

### US-1: Process Payment
**As a** user
**I want to** pay for my subscription
**So that** I can access premium features

**Acceptance Criteria:**
- [ ] AC-1.1: Accepts credit card via Stripe
- [ ] AC-1.2: Returns success or error
- [ ] AC-1.3: Activates subscription on success

## Question-Pack Answers

### Security
- Payment gateway: Stripe
- Secrets: Stripe API key in .env

### Testing
- Coverage: 80%
- Types: Integration tests

## Guardrail Coverage Matrix
... (8 guardrails, mostly TBD) ...
```

---

### Step 1: Generate Gap Analysis Request

```bash
ldf audit --type gap-analysis --agent chatgpt > gap-analysis.md
```

### Step 2: Submit to ChatGPT

**ChatGPT finds 18 gaps:**

1. No idempotency handling (duplicate charges)
2. No refund flow
3. No handling of declined cards
4. No 3D Secure / SCA support (EU requirement)
5. No currency specification
6. No tax calculation
7. No invoice generation
8. No webhook handling for async events
9. No partial payment support
10. No subscription downgrade flow
11. ... (8 more)

---

### Step 3: Security Audit with Gemini

```bash
ldf audit --type security --agent gemini > security-audit.md
```

**Gemini finds 12 security issues:**

1. No PCI compliance strategy mentioned
2. Raw card data storage (should use Stripe tokens only)
3. No fraud detection rules
4. No amount validation (could charge negative amounts!)
5. No HTTPS enforcement
6. No CORS policy
7. ... (6 more)

---

### Step 4: Import Both Feedbacks

```bash
# Import ChatGPT gap analysis
ldf audit --import gap-analysis-feedback.md

# Import Gemini security audit
ldf audit --import security-audit-feedback.md
```

---

### After Review: Improved Spec

```markdown
# stripe-payments - Requirements

## User Stories

### US-1: Process Payment
**Acceptance Criteria:**
- [ ] AC-1.1: Accepts credit card via Stripe Elements (PCI-compliant)
- [ ] AC-1.2: Returns success (200), declined (402), or error (500)
- [ ] AC-1.3: Activates subscription on success
- [ ] AC-1.4: Idempotent (duplicate requests don't double-charge)
- [ ] AC-1.5: Supports 3D Secure / SCA for EU cards
- [ ] AC-1.6: Validates amount > 0 and < $10,000
- [ ] AC-1.7: Handles webhooks for async payment confirmation

### US-2: Handle Declined Payments
- [ ] AC-2.1: Returns 402 Payment Required with decline reason
- [ ] AC-2.2: Logs decline for fraud analysis
- [ ] AC-2.3: Suggests alternative payment methods

### US-3: Refund Payment
- [ ] AC-3.1: Admin can issue full or partial refund
- [ ] AC-3.2: Refund processed via Stripe API
- [ ] AC-3.3: Webhook updates subscription status

## Question-Pack Answers

### Security
- **Payment gateway:** Stripe
- **PCI compliance:** Using Stripe Elements (card data never touches our servers)
- **Fraud detection:** Stripe Radar enabled, block >$10k without verification
- **Idempotency:** Stripe idempotency keys on all payment requests
- **HTTPS:** Required for all endpoints (enforced by middleware)
- **Secrets:** Stripe keys in environment variables, rotated quarterly

### Testing
- **Coverage:** 95% (payments are critical)
- **Types:** Integration (Stripe test mode), unit (amount validation), E2E (checkout flow), security (fraud scenarios)
- **Webhooks:** Test all 5 webhook events in test mode

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [US-1, US-2, US-3: 95% target, integration + unit + E2E] | TBD | TBD | QA + Dev | TODO |
| 2. Security Basics | [AC-1.1: PCI via Stripe, AC-1.4: Idempotency, AC-1.6: Amount validation, Fraud detection] | TBD | TBD | Security + Dev | TODO |
| 3. Error Handling | [AC-1.2, AC-2.1: Structured error responses, AC-1.7: Webhook error handling] | TBD | TBD | Dev | TODO |
| ... (full matrix) ...
```

**Result:**
- 3 user stories (was 1)
- 17 acceptance criteria (was 3)
- Detailed security answers
- Complete guardrail matrix
- Ready for design phase with confidence

---

## Best Practices

### 1. Use Multiple Agents

**Single agent:**
```
Claude Code writes spec → ChatGPT reviews → Done
```
**Result:** ~10 gaps found

**Multiple agents:**
```
Claude Code writes spec → ChatGPT gap analysis → Gemini security audit → Done
```
**Result:** ~20 gaps found (less overlap than you'd expect!)

**Why:** Different LLMs have different strengths and blind spots.

---

### 2. Timing Matters

**Too early:**
```
Draft 1 sentence overview → Get AI review
```
❌ Premature - not enough context for meaningful review

**Too late:**
```
Complete requirements + design + tasks → Get AI review
```
❌ Too late - design decisions already made, expensive to change

**Just right:**
```
Complete requirements.md + answerpacks → Get AI review → Update requirements → Design
```
✅ Optimal - catches gaps before design, cheap to fix

---

### 3. Be Specific with Audit Types

**Vague:**
```bash
ldf audit --type spec-review  # Generic review
```
**Result:** Surface-level feedback

**Specific:**
```bash
ldf audit --type security       # Deep security dive
ldf audit --type edge-cases     # Boundary conditions
ldf audit --type architecture   # Scalability concerns
```
**Result:** Targeted, actionable feedback

---

### 4. Track Feedback History

Create a `feedback-log.md` in each spec:

```markdown
# user-auth - Feedback History

## Round 1: ChatGPT Gap Analysis (2024-01-15)

**Reviewer:** ChatGPT-4
**Type:** gap-analysis
**Gaps found:** 15

**Applied (12):**
- AC-1.5: Rate limiting
- AC-1.6: Account lockout
- US-2: Password reset flow
... (9 more) ...

**Rejected (3):**
- Remember me checkbox → Out of scope for MVP
- Social login (Google, GitHub) → V2 feature
- Biometric auth → Not supported on web

## Round 2: Gemini Security Audit (2024-01-16)

**Reviewer:** Gemini Advanced
**Type:** security
**Issues found:** 8

**Applied (7):**
- HTTPS enforcement
- CORS policy
- JWT secret rotation
... (4 more) ...

**Rejected (1):**
- Hardware security module → Over-engineering for startup
```

**Benefits:**
- Audit trail for compliance
- Explains why suggestions were rejected
- Prevents re-litigating decisions

---

### 5. Don't Blindly Accept All Suggestions

**Example over-reach:**

**ChatGPT suggestion:**
```
Gap 15: Performance - No Caching Strategy
Suggested AC: AC-3.5: Implement Redis caching with 1-hour TTL
```

**Your response:**
```markdown
# feedback-log.md

## Rejected

### Gap 15: Caching
**Reason:** Premature optimization. Login endpoint called once per session.
No performance issues expected for <10k users.
Will revisit if p95 latency >500ms in production.
**Decided by:** Tech lead
```

**Rule:** Apply suggestions that prevent bugs/security issues. Question suggestions that add complexity without clear benefit.

---

## Troubleshooting

### Q: ChatGPT/Gemini doesn't follow the output format

**A:** Add to audit request:
```markdown
IMPORTANT: Structure your response EXACTLY as shown in the Output Format section.
Start each gap with "### Gap N: [Category] - [Title]"
```

Or use `--api` mode for consistent parsing.

---

### Q: Too many suggestions (overwhelming)

**A:** Prioritize by impact:

1. **High priority (must fix):**
   - Security vulnerabilities
   - Data loss scenarios
   - Legal/compliance issues

2. **Medium priority (should fix):**
   - Edge cases causing errors
   - UX confusion
   - Missing error handling

3. **Low priority (nice to have):**
   - Performance optimizations
   - Additional features
   - Code quality suggestions

Apply high priority immediately, defer low priority to backlog.

---

### Q: Feedback contradicts my design decisions

**A:** Document your rationale:

```markdown
## Design Decision: Using Sessions Instead of JWT

**ChatGPT suggested:** JWT for stateless auth

**Our decision:** Session cookies with Redis

**Rationale:**
- Need server-side revocation (user logout from all devices)
- Sensitive financial app, want centralized session control
- Redis already in infrastructure for rate limiting
- Session data <1 KB, not a scaling concern for <100k users

**Approved by:** Security team, 2024-01-15
```

---

## Next Steps

Now that you understand multi-agent review:

1. **Practice:** Get a review of your first spec from Tutorial 1
2. **Experiment:** Try both ChatGPT and Gemini, compare results
3. **Continue learning:**
   - [Tutorial 5: MCP Setup](05-mcp-setup.md) - Integrate AI assistants directly
   - [Multi-Agent Workflow Guide](../multi-agent-workflow.md) - Advanced techniques

---

## Quick Reference: Audit Types

| Type | Best For | Expected Gaps |
|------|----------|---------------|
| `spec-review` | General completeness | 10-15 gaps |
| `gap-analysis` | Missing requirements | 15-25 gaps |
| `security` | Security vulnerabilities | 8-15 issues |
| `edge-cases` | Boundary conditions | 10-20 cases |
| `architecture` | Scalability, design | 5-10 concerns |
| `pre-launch` | Final review | 20-40 items |

---

**Next Tutorial**: [MCP Setup for AI Assistants](05-mcp-setup.md)
