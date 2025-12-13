# Audit Response Template

Use this template to capture and process responses from external AI agents.

---

## Audit Response

**Request ID:** [from original request]
**Response Date:** [YYYY-MM-DD]
**Audit Type:** [SPEC_REVIEW | CODE_AUDIT | SECURITY_CHECK | GAP_ANALYSIS | EDGE_CASES | ARCHITECTURE]
**Auditor:** [ChatGPT | Gemini | Other]

### Summary

**Overall Assessment:** [APPROVE | NEEDS_REVISION | REJECT]
**Risk Level:** [LOW | MEDIUM | HIGH | CRITICAL]

### Issues Found

#### Critical Issues
| ID | Title | Location | Status |
|----|-------|----------|--------|
| C-001 | [title] | [location] | OPEN |

#### High Priority Issues
| ID | Title | Location | Status |
|----|-------|----------|--------|
| H-001 | [title] | [location] | OPEN |

#### Medium Priority Issues
| ID | Title | Location | Status |
|----|-------|----------|--------|
| M-001 | [title] | [location] | OPEN |

#### Low Priority Issues
| ID | Title | Location | Status |
|----|-------|----------|--------|
| L-001 | [title] | [location] | OPEN |

### Full Response

```markdown
[Paste the complete response from the auditor here]
```

---

## Processing Instructions

### Step 1: Triage Issues

For each issue, determine:
1. **Validity** - Is this a real issue or false positive?
2. **Scope** - Is it in scope for this feature?
3. **Owner** - Who should address it?

Mark invalid issues as:
```
| L-001 | [title] | [location] | INVALID: [reason] |
```

### Step 2: Create Action Items

Convert valid issues to tasks:

```markdown
## Action Items from Audit [Request ID]

### Critical (Block Release)
- [ ] C-001: [Action description]
  - Assigned: [name]
  - Deadline: [date]
  - Spec update needed: Yes/No

### High (Fix Before Release)
- [ ] H-001: [Action description]
  - Assigned: [name]
  - Deadline: [date]

### Medium (Track as Tech Debt)
- [ ] M-001: [Action description]
  - Assigned: [name]
  - Ticket: [link]

### Low (Optional)
- [ ] L-001: [Action description]
```

### Step 3: Update Spec

For issues that require spec changes:

1. Update the relevant spec file
2. Note the change in the spec's revision history:
   ```markdown
   ## Revision History
   | Date | Author | Change | Source |
   |------|--------|--------|--------|
   | [date] | [name] | [change] | Audit [Request ID] |
   ```

### Step 4: Re-audit if Needed

If critical or high issues were found:
1. Make the required changes
2. Create a new audit request
3. Reference the original: `Follow-up to: [Request ID]`

### Step 5: Close the Audit

Once all issues are addressed:

```markdown
## Audit Closure

**Request ID:** [id]
**Closed Date:** [date]
**Closed By:** [name]

### Resolution Summary
- Critical Issues: [X addressed, Y deferred, Z invalid]
- High Issues: [X addressed, Y deferred, Z invalid]
- Medium Issues: [X addressed, Y deferred, Z invalid]
- Low Issues: [X addressed, Y deferred, Z invalid]

### Deferred Items
| ID | Reason | Ticket |
|----|--------|--------|
| [id] | [reason] | [link] |

### Lessons Learned
1. [What we learned from this audit]
2. [Process improvements to make]
```

---

## Example Processed Response

```markdown
## Audit Response

**Request ID:** AUDIT-2024-001
**Response Date:** 2024-01-16
**Audit Type:** SPEC_REVIEW
**Auditor:** ChatGPT

### Summary

**Overall Assessment:** NEEDS_REVISION
**Risk Level:** MEDIUM

### Issues Found

#### Critical Issues
| ID | Title | Location | Status |
|----|-------|----------|--------|
| C-001 | Missing rate limiting | US-1 | OPEN |

#### High Priority Issues
| ID | Title | Location | Status |
|----|-------|----------|--------|
| H-001 | No account lockout spec | US-1 AC | ADDRESSED: Added to v1.1 |
| H-002 | Email enumeration risk | US-2 | ADDRESSED: Added same-response pattern |

#### Medium Priority Issues
| ID | Title | Location | Status |
|----|-------|----------|--------|
| M-001 | Missing password requirements | US-3 | ADDRESSED: Added min 12 chars |
| M-002 | Session invalidation not specified | US-3 | DEFERRED: Ticket #123 |

### Action Items

- [x] C-001: Add rate limiting requirement (3 requests per 15 min)
- [x] H-001: Add account lockout after 5 failed attempts
- [x] H-002: Specify same response for existing/non-existing emails
- [x] M-001: Add password policy requirements
- [ ] M-002: Deferred - create follow-up ticket

### Spec Updates Made

requirements.md v1.1:
- Added US-4: Rate limiting (3 per 15 min per email)
- Updated US-1 AC: Added account lockout specification
- Updated US-2 AC: Same response regardless of email existence
- Added US-3 AC: Password policy (12+ chars, complexity)

### Audit Status: CLOSED
Re-audit: Not required (issues addressed inline)
```

---

## Integration with LDF

Import audit findings into the spec's guardrail coverage:

```bash
ldf audit --import audit-response.md --spec password-reset
```

This will:
1. Parse the issues
2. Update guardrail coverage matrix
3. Create tasks in tasks.md if needed
4. Update audit trail in spec metadata
