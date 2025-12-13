# Task Format Guide

Complete reference for task formatting in LDF (LLM Development Framework).

## Supported Task Formats

LDF supports two task formats. Use either consistently within a file, or clearly separate them with `## Phase` boundaries.

### Heading Format

Tasks defined using markdown headings.

```markdown
### Task 1.1: Create authentication service
- [ ] Implement login endpoint
- [ ] Implement logout endpoint
- [ ] Add JWT generation

### Task 1.2: Add password hashing
- [ ] Install bcrypt
- [ ] Hash passwords on registration
```

**Requirements:**
- Heading marker: `#`, `##`, or `###` (REQUIRED)
- "Task" keyword: OPTIONAL
- Colon after task ID: REQUIRED
- Task ID format: `1.1` or `1.1.1`

**Variations:**
```markdown
### Task 1.1: With Task keyword
### 1.1: Without Task keyword (also valid)
## Task 2.3: Different heading level
# Task 1.1.1: Subtask with 3-level ID
```

### Checklist Format (Official Template)

Tasks defined using checkbox lists. This is the official template format.

```markdown
## Phase 1: Setup

- [ ] **Task 1.1:** Create authentication service
  - [ ] Implement login endpoint
  - [ ] Implement logout endpoint
  - [ ] Add JWT generation

- [ ] **Task 1.2:** Add password hashing
  - [ ] Install bcrypt
  - [ ] Hash passwords on registration
```

**Requirements:**
- Checkbox: `- [ ]` or `- [x]` (REQUIRED)
- "Task" keyword: REQUIRED
- Colon after task ID: REQUIRED
- Task ID format: `1.1` or `1.1.1`
- Bold markers: OPTIONAL (but recommended for clarity)

**Variations:**
```markdown
- [ ] **Task 1.1:** With bold markers (recommended)
- [ ] Task 1.1: Without bold markers (also valid)
- [x] **Task 1.1:** Completed task
- [X] Task 1.1: Uppercase X also works
  - [ ] Task 1.2: Indented tasks supported
```

## Task Numbering

### Two-Level Task IDs (Standard)

Format: `Phase.Task` (e.g., `1.1`, `2.3`, `5.2`)

Use for main implementation tasks within a phase.

**Example:**
```markdown
## Phase 1: Foundation
- [ ] **Task 1.1:** Setup project
- [ ] **Task 1.2:** Configure database

## Phase 2: Core Features
- [ ] **Task 2.1:** Implement service
- [ ] **Task 2.2:** Add validation
```

### Three-Level Subtask IDs

Format: `Phase.Task.Subtask` (e.g., `1.1.1`, `2.3.2`)

Use when breaking down complex tasks into smaller units.

**Example:**
```markdown
## Phase 1: Authentication

- [ ] **Task 1.1:** Implement auth service
  - [ ] Core functionality

- [ ] **Task 1.1.1:** Add JWT support
  - [ ] Generate tokens
  - [ ] Validate tokens
  - **Depends on:** Task 1.1

- [ ] **Task 1.1.2:** Add refresh tokens
  - [ ] Store refresh tokens
  - [ ] Implement rotation
  - **Depends on:** Task 1.1.1
```

**When to use subtasks:**
- Complex tasks requiring multiple distinct steps
- Tasks with clear internal dependencies
- When you need finer-grained progress tracking

## Task Status Detection

The linter automatically determines task status from checkboxes within the task section.

### Status Values

- **pending**: No checkboxes OR all unchecked `- [ ]`
- **in_progress**: Some checked, some unchecked (mix of `[x]` and `[ ]`)
- **complete**: All checkboxes checked `- [x]`

### How Status is Determined

The parser looks at all checkboxes **within a task's section** (from the task header to the next task or phase).

**Example:**
```markdown
- [ ] **Task 1.1:** First task
  - [ ] Step one          ← Both unchecked
  - [ ] Step two          ← Status: pending

- [ ] **Task 1.2:** Second task
  - [x] Step one          ← One checked
  - [ ] Step two          ← One unchecked
                          ← Status: in_progress

- [x] **Task 1.3:** Third task
  - [x] Step one          ← All checked
  - [x] Step two          ← Status: complete
```

**Important:** Each task's status is scoped to its own section only. Task 1.2's checkboxes don't affect Task 1.1's status.

## Requirements Summary

|                       | Heading Format | Checklist Format |
|-----------------------|----------------|------------------|
| "Task" keyword        | OPTIONAL       | REQUIRED         |
| Colon after ID        | REQUIRED       | REQUIRED         |
| Marker required       | `#` `##` `###` | `- [ ]` `- [x]`  |
| Bold markers          | N/A            | OPTIONAL         |
| Indentation allowed   | N/A            | YES              |
| Task ID levels        | 2 or 3         | 2 or 3           |

## Common Mistakes

### 1. Missing "Task" Keyword in Checklist Format

**❌ Incorrect:**
```markdown
- [ ] 1.1: Create service
```

**✓ Correct:**
```markdown
- [ ] **Task 1.1:** Create service
```

The parser requires "Task" keyword for checklist format to avoid false positives.

### 2. Missing Colon After Task ID

**❌ Incorrect:**
```markdown
### Task 1.1 Create service    ← Space instead of colon
- [ ] **Task 1.1** Create service    ← No colon
```

**✓ Correct:**
```markdown
### Task 1.1: Create service
- [ ] **Task 1.1:** Create service
```

Colon is REQUIRED for all formats.

### 3. Mixing Formats Without Phase Boundaries

**⚠️ Avoid:**
```markdown
## Phase 1

### Task 1.1: Heading format
- [ ] Step one

- [ ] **Task 1.2:** Checklist format    ← Mixed without clear boundary
```

**✓ Better:**
```markdown
## Phase 1: Heading Format Tasks

### Task 1.1: Setup
- [ ] Step one

### Task 1.2: Configure
- [ ] Step two

## Phase 2: Checklist Format Tasks

- [ ] **Task 2.1:** Implement
  - [ ] Step one
```

Use consistent format within a phase, or use clear `## Phase` boundaries.

### 4. Inline References (These Are Ignored - Correctly)

These will NOT be matched as tasks:

```markdown
See task 1.1 for prerequisites.
Based on version 2.3, implement feature X.
Task 1.1 is the foundation for this work.
```

This is correct behavior - inline references are not tasks.

## Best Practices

### Choose One Primary Format

**Recommended:** Use checklist format (matches official template)
```markdown
- [ ] **Task 1.1:** Create service
```

**Alternative:** Use heading format (shorter, cleaner)
```markdown
### Task 1.1: Create service
```

Both are valid. Pick one and use it consistently.

### Use Descriptive Task Titles

**❌ Vague:**
```markdown
- [ ] **Task 1.1:** Do the thing
- [ ] **Task 1.2:** Fix stuff
```

**✓ Specific:**
```markdown
- [ ] **Task 1.1:** Create AuthService class with login/logout methods
- [ ] **Task 1.2:** Add bcrypt password hashing on registration
```

### Break Down Complex Tasks

If a task has more than 5-7 subtasks, consider using 3-level IDs:

**Instead of:**
```markdown
- [ ] **Task 1.1:** Implement entire auth system
  - [ ] Create service
  - [ ] Add login
  - [ ] Add logout
  - [ ] Add registration
  - [ ] Add password reset
  - [ ] Add email verification
  - [ ] Add MFA
  - [ ] Add session management
```

**Better:**
```markdown
- [ ] **Task 1.1:** Create auth service foundation
  - [ ] Create AuthService class
  - [ ] Set up dependency injection

- [ ] **Task 1.1.1:** Implement login/logout
  - [ ] Login endpoint
  - [ ] Logout endpoint

- [ ] **Task 1.1.2:** Implement registration
  - [ ] Registration endpoint
  - [ ] Email verification

- [ ] **Task 1.1.3:** Add MFA support
  - [ ] TOTP implementation
  - [ ] Backup codes
```

### Specify Dependencies

```markdown
- [ ] **Task 1.1:** Create database schema
  - **Dependencies:** None

- [ ] **Task 1.2:** Implement repository
  - **Dependencies:** Task 1.1

- [ ] **Task 1.3:** Create service layer
  - **Dependencies:** Task 1.2
```

The linter will validate that dependencies exist and detect circular dependencies.

## Examples

### Complete Example: Checklist Format

```markdown
# user-authentication - Tasks

## Task Numbering Convention
- Major phase: X.0
- Tasks: X.1, X.2, X.3...
- Subtasks: X.1.1, X.1.2... (use for complex tasks requiring breakdown)

**Note:** Both 2-level (1.1) and 3-level (1.1.1) task IDs are supported.

## Phase 1: Foundation

- [ ] **Task 1.1:** Create project structure
  - [ ] Create `src/auth` directory
  - [ ] Set up module exports
  - **Dependencies:** None

- [ ] **Task 1.2:** Set up database
  - [ ] Create migration for users table
  - [ ] Add password_hash column
  - [ ] Add email_verified column
  - **Dependencies:** None

## Phase 2: Core Implementation

- [ ] **Task 2.1:** Implement AuthService
  - [ ] Create class structure
  - [ ] Add TypeScript interfaces
  - [ ] Write class docstring
  - **Dependencies:** Task 1.1, Task 1.2

- [ ] **Task 2.1.1:** Add registration method
  - [ ] Validate email format
  - [ ] Hash password with bcrypt
  - [ ] Store user in database
  - **Dependencies:** Task 2.1

- [ ] **Task 2.1.2:** Add login method
  - [ ] Verify password
  - [ ] Generate JWT token
  - [ ] Return session info
  - **Dependencies:** Task 2.1
```

### Complete Example: Heading Format

```markdown
# user-authentication - Tasks

## Phase 1: Foundation

### Task 1.1: Create project structure
- [ ] Create `src/auth` directory
- [ ] Set up module exports
- **Dependencies:** None

### Task 1.2: Set up database
- [ ] Create migration for users table
- [ ] Add password_hash column
- **Dependencies:** None

## Phase 2: Core Implementation

### Task 2.1: Implement AuthService
- [ ] Create class structure
- [ ] Add TypeScript interfaces
- **Dependencies:** Task 1.1, Task 1.2

### Task 2.1.1: Add registration method
- [ ] Validate email format
- [ ] Hash password with bcrypt
- **Dependencies:** Task 2.1

### Task 2.1.2: Add login method
- [ ] Verify password
- [ ] Generate JWT token
- **Dependencies:** Task 2.1
```

## Related Documentation

- [Getting Started Guide](getting-started.md) - Quick start with LDF
- [Concepts](concepts.md) - Understanding the three-phase workflow
- [Template: tasks.md](../framework/templates/tasks.md) - Official template

## Troubleshooting

### "Task X.X has no checklist items"

**Cause:** Parser can't find the task.

**Solutions:**
1. Ensure "Task" keyword is present (required for checklist format)
2. Verify colon after task ID: `Task 1.1:` not `Task 1.1`
3. Check heading marker (`###`) or checkbox (`- [ ]`) is present

### "No tasks found"

**Cause:** Parser found zero tasks in the file.

**Solutions:**
1. Verify format matches one of the supported formats above
2. Ensure colon is present after all task IDs
3. For checklist format, verify "Task" keyword is present

### Tasks showing wrong status

**Cause:** Status detection looks at checkboxes within task section.

**Solution:** Ensure task sections are properly bounded:
- Each task should have its own section
- Use `## Phase` headers to create clear boundaries
- Don't put multiple tasks under one section without boundaries
