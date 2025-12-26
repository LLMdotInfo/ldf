# Tutorial: Understanding Guardrails

> **For**: Users who completed the first spec tutorial
> **Time**: 30 minutes
> **Prerequisites**: [Your First LDF Spec](01-first-spec.md)
> **What you'll learn**: Deep dive into the 8 core guardrails, when to mark N/A, how to complete coverage matrices

---

## What Are Guardrails?

**Guardrails** are quality constraints that prevent common bugs and ensure production-ready code.

Think of them like a **pre-flight checklist** for pilots:
- Every flight uses the same checklist
- Each item prevents a specific type of failure
- You can't skip items just because you're in a hurry
- Marking something "N/A" requires justification

**In LDF**, guardrails force you to think about quality concerns **before writing code**, when they're cheap to fix.

---

## Why Guardrails Matter

**Without guardrails:**
```python
# Developer writes code
def process_payment(amount):
    charge_card(amount)  # What if this fails?
    send_receipt()       # What if email is invalid?
    return "Done"
```

**With guardrails** (Error Handling + Data Validation):
```python
def process_payment(amount: float) -> PaymentResult:
    # Guardrail 6: Data Validation
    if amount <= 0 or amount > 10000:
        raise ValueError("Invalid amount")

    try:
        # Guardrail 3: Error Handling
        transaction_id = charge_card(amount)
        send_receipt(transaction_id)
        return PaymentResult(success=True, id=transaction_id)
    except PaymentError as e:
        logger.error(f"Payment failed: {e}")
        return PaymentResult(success=False, error=str(e))
```

The guardrails prompted you to:
- Validate input (prevents negative charges)
- Handle failures gracefully
- Log errors for debugging
- Return structured results

---

## The 8 Core Guardrails

Every LDF project has these 8 guardrails, regardless of preset:

| # | Guardrail | Prevents |
|---|-----------|----------|
| **1** | **Testing Coverage** | Untested code making it to production |
| **2** | **Security Basics** | OWASP Top 10 vulnerabilities |
| **3** | **Error Handling** | Crashes and silent failures |
| **4** | **Logging & Observability** | Blind debugging in production |
| **5** | **API Design** | Breaking changes and inconsistent APIs |
| **6** | **Data Validation** | Bad data corrupting your database |
| **7** | **Database Migrations** | Schema changes breaking production |
| **8** | **Documentation** | Future you not understanding past you's code |

Let's explore each one in detail.

---

## Guardrail 1: Testing Coverage

**Requirement**: Minimum 80% coverage, 90% for critical paths

**What it prevents:**
- Deploying untested code
- Regressions (breaking existing features)
- Fear of refactoring

**In the coverage matrix:**

**Good:**
```markdown
| 1. Testing Coverage | [US-1: 80% target, integration tests for /hello] | [Section 4: pytest + coverage.py] | [Task 3.1: Write test_hello.py] | Dev | TODO |
```

**Too vague:**
```markdown
| 1. Testing Coverage | We'll test it | TBD | TBD | Dev | TODO |
```

**Example test strategy for a login endpoint:**

**In requirements.md:**
```markdown
### US-1: User Login

**Acceptance Criteria:**
- [ ] AC-1.1: Returns 200 + JWT on valid credentials
- [ ] AC-1.2: Returns 401 on invalid credentials
- [ ] AC-1.3: Rate limits to 5 attempts per 15 minutes

**Testing approach:**
- Integration tests: All 3 acceptance criteria
- Unit tests: Password hashing, JWT generation
- Load tests: Rate limiting under concurrent requests
- Coverage target: 90% (authentication is critical)
```

**In the matrix:**
```markdown
| 1. Testing Coverage | [US-1: 90% target, integration + unit + load tests] | [Section 4: pytest fixtures, mock database] | [Task 3.1-3.3: test_login.py, test_rate_limit.py] | QA + Dev | TODO |
```

---

## Guardrail 2: Security Basics

**Requirement**: Address OWASP Top 10, secure defaults

**What it prevents:**
- SQL injection, XSS, CSRF
- Hardcoded secrets
- Insecure authentication

**Common security decisions to document:**

1. **Authentication method**: JWT, sessions, OAuth, API keys?
2. **Password storage**: bcrypt cost 12, argon2id, scrypt?
3. **Secrets management**: Environment variables, vault, KMS?
4. **HTTPS enforcement**: Required for all endpoints?
5. **Rate limiting**: Per IP, per user, per endpoint?

**In the coverage matrix:**

**Good:**
```markdown
| 2. Security Basics | [US-1: JWT auth, bcrypt cost 12, secrets in .env] | [Section 2.3: AuthMiddleware, rate limiter] | [Task 2.1: Implement JWT verification] | Security + Dev | TODO |
```

**Example for a file upload feature:**

**In requirements.md (Question-Pack Answers):**
```markdown
### Security
- **File upload validation**: Whitelist extensions (.jpg, .png, .pdf only)
- **Size limits**: 10 MB per file, 50 MB per request
- **Virus scanning**: ClamAV scan before storage
- **Storage**: S3 with signed URLs, 1-hour expiry
- **Access control**: Users can only access their own files
```

**In the matrix:**
```markdown
| 2. Security Basics | [US-2: File validation, size limits, virus scan, signed URLs] | [Section 3.2: UploadValidator, ClamAV integration, S3 client] | [Task 2.3: Implement file validator, Task 2.4: Add ClamAV] | Security + Dev | TODO |
```

---

## Guardrail 3: Error Handling

**Requirement**: No silent failures, structured error responses

**What it prevents:**
- Crashes exposing stack traces
- Silent failures losing data
- Inconsistent error messages

**Error handling checklist:**

- [ ] All external calls (DB, API, file I/O) wrapped in try/catch
- [ ] Errors logged with context (user ID, request ID, timestamp)
- [ ] User-friendly error messages (not stack traces)
- [ ] HTTP status codes used correctly (400 vs 500)
- [ ] Retry logic for transient failures

**In the coverage matrix:**

**Good:**
```markdown
| 3. Error Handling | [AC-1.3: Return 500 on DB error, 400 on validation, with error codes] | [Section 3.4: ErrorMiddleware, custom exceptions] | [Task 2.2: Add error middleware] | Dev | TODO |
```

**Example for a payment endpoint:**

**In requirements.md:**
```markdown
### US-3: Process Payment

**Error scenarios:**
- Invalid amount (400 Bad Request): `{"error": "INVALID_AMOUNT", "message": "Amount must be between $0.01 and $10,000"}`
- Payment gateway down (503 Service Unavailable): Retry 3 times with exponential backoff, then fail gracefully
- Insufficient funds (402 Payment Required): `{"error": "INSUFFICIENT_FUNDS", "message": "Payment declined"}`
- Unexpected errors (500 Internal Server Error): Log full details, return generic message to user
```

**In the matrix:**
```markdown
| 3. Error Handling | [US-3: 4 error types with codes, retry logic, logging] | [Section 3.5: PaymentException hierarchy, retry decorator] | [Task 2.5: Implement error classes, Task 2.6: Add retry logic] | Dev | TODO |
```

---

## Guardrail 4: Logging & Observability

**Requirement**: Log key events, enable debugging

**What it prevents:**
- Blind debugging (can't reproduce issues)
- No audit trail
- Can't measure performance

**What to log:**

**Always log:**
- User actions (login, logout, create, update, delete)
- API requests (method, path, status, duration)
- Errors and exceptions (with stack traces)
- Security events (failed logins, permission denials)

**Consider logging:**
- Database query performance (slow query log)
- External API calls (latency, failures)
- Background job status
- Cache hits/misses

**Never log:**
- Passwords or secrets
- Full credit card numbers
- SSNs or other PII (unless required for compliance)

**In the coverage matrix:**

**Good:**
```markdown
| 4. Logging & Observability | [US-1: Log all requests with duration, errors with stack traces] | [Section 4.2: Structured logging (JSON), log levels] | [Task 3.4: Add request logger middleware] | Dev | TODO |
```

**Example log format:**

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "INFO",
  "request_id": "req-abc123",
  "user_id": "user-456",
  "method": "POST",
  "path": "/api/v1/payments",
  "status": 200,
  "duration_ms": 245,
  "ip": "192.168.1.1"
}
```

**In requirements.md:**
```markdown
### Logging Strategy
- Format: Structured JSON logs
- Levels: DEBUG (dev only), INFO (requests), WARNING (recoverable errors), ERROR (failures)
- Fields: timestamp, request_id, user_id, method, path, status, duration_ms
- Destination: stdout (captured by container logging)
```

---

## Guardrail 5: API Design

**Requirement**: Consistent, versioned, well-documented APIs

**What it prevents:**
- Breaking changes for existing clients
- Inconsistent response formats
- API sprawl (10 ways to do the same thing)

**API design checklist:**

- [ ] Versioned endpoints (`/api/v1/...`)
- [ ] Consistent naming (plural nouns: `/users`, `/orders`)
- [ ] Standard HTTP methods (GET, POST, PUT, DELETE, PATCH)
- [ ] Consistent response structure
- [ ] Pagination for list endpoints
- [ ] Error format standardized

**In the coverage matrix:**

**Good:**
```markdown
| 5. API Design | [US-1: /api/v1/hello, JSON response, OpenAPI spec] | [Section 2.1: FastAPI router, response models] | [Task 1.2: Define Pydantic models] | Dev | TODO |
```

**Example response structure:**

**In requirements.md:**
```markdown
### API Design Standards

**Base path:** `/api/v1`

**Success response:**
```json
{
  "data": {
    "id": "user-123",
    "email": "user@example.com"
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:45Z"
  }
}
```

**Error response:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [
      {"field": "email", "message": "Must be a valid email"}
    ]
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:45Z",
    "request_id": "req-abc123"
  }
}
```

**List endpoints:** Cursor-based pagination, max 100 items per page
```

---

## Guardrail 6: Data Validation

**Requirement**: Validate all inputs, sanitize outputs

**What it prevents:**
- SQL injection (via ORM bypass)
- XSS (via unsanitized output)
- Data corruption (invalid data in DB)

**Validation layers:**

1. **Input validation**: Type, format, range
2. **Business logic validation**: Rules (e.g., amount > 0)
3. **Database constraints**: NOT NULL, UNIQUE, CHECK constraints
4. **Output sanitization**: Escape HTML, JSON encode

**When to mark N/A:**
- No user input (e.g., GET endpoint with no parameters)
- Read-only endpoint (still validate query params!)

**In the coverage matrix:**

**Good:**
```markdown
| 6. Data Validation | [US-2: Validate email format, password strength, unique email constraint] | [Section 2.4: Pydantic validators, DB unique constraint] | [Task 1.3: Add email validator, Task 1.4: Add DB constraint] | Dev | TODO |
```

**Correct N/A usage:**
```markdown
| 6. Data Validation | N/A - No input parameters (GET endpoint with no query params) | N/A | N/A | - | N/A |
```

**Example validation for user registration:**

**In requirements.md:**
```markdown
### US-1: User Registration

**Input validation:**
- Email: Valid format (RFC 5322), max 255 chars, lowercase normalized
- Password: Min 12 chars, must contain uppercase, lowercase, number, special char
- Name: 1-100 chars, alphanumeric + spaces only

**Database constraints:**
- Email: UNIQUE constraint
- Created_at: NOT NULL, default NOW()

**Business rules:**
- Email must not be in disposable email blocklist
- Password must not be in pwned passwords database
```

---

## Guardrail 7: Database Migrations

**Requirement**: Versioned, reversible schema changes

**What it prevents:**
- Schema drift between environments
- Data loss during deployments
- Inability to rollback

**Migration checklist:**

- [ ] Every schema change has a migration file
- [ ] Migrations are numbered/timestamped
- [ ] Migrations have `up` and `down` (rollback)
- [ ] Test migrations on staging before production
- [ ] Large data migrations are idempotent

**When to mark N/A:**
- No database used
- Read-only database access
- External database (you don't control schema)

**In the coverage matrix:**

**Good:**
```markdown
| 7. Database Migrations | [US-1: Migration 001_create_users_table.sql] | [Section 3.1: Alembic migrations, indexes on email] | [Task 1.1: Create initial migration] | DBA + Dev | TODO |
```

**Correct N/A usage:**
```markdown
| 7. Database Migrations | N/A - No database access (in-memory cache only) | N/A | N/A | - | N/A |
```

**Example migration strategy:**

**In requirements.md:**
```markdown
### Database Changes

**New table: users**
- Migration: `001_create_users.sql`
- Rollback: `001_rollback_users.sql`
- Indexes: email (UNIQUE), created_at

**Migration strategy:**
- Tool: Alembic (Python) / Flyway (Java)
- Naming: `{timestamp}_{description}.sql`
- Testing: Run on staging, verify rollback works
- Safety: Use transactions, avoid data loss
```

---

## Guardrail 8: Documentation

**Requirement**: Code, API, and setup docs

**What it prevents:**
- Knowledge silos (only one person knows how it works)
- Onboarding taking weeks
- API users guessing request formats

**Documentation types:**

1. **Code comments**: For complex algorithms (not obvious code)
2. **Docstrings**: For all public functions/classes
3. **API docs**: OpenAPI/Swagger, generated from code
4. **Setup docs**: How to run locally, deploy
5. **Architecture docs**: High-level design

**In the coverage matrix:**

**Good:**
```markdown
| 8. Documentation | [US-1: OpenAPI spec auto-generated, docstrings on all routes] | [Section 5: FastAPI auto-docs at /docs] | [Task 4.1: Add route docstrings] | Dev + TechWriter | TODO |
```

**Example documentation plan:**

**In requirements.md:**
```markdown
### Documentation

**API documentation:**
- Tool: FastAPI auto-generated OpenAPI at `/docs`
- Format: Each endpoint has description, request/response examples
- Authentication: Documented with example JWT

**Code documentation:**
- Docstrings: All public functions (Google style)
- Comments: Only for non-obvious logic
- Type hints: All function signatures

**Setup documentation:**
- README.md: How to install, run tests, deploy
- CONTRIBUTING.md: Code style, PR process
```

---

## How to Fill Out the Guardrail Coverage Matrix

The matrix appears in **requirements.md** and tracks how each guardrail is addressed across all three phases.

### Matrix Structure

```markdown
| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [References] | [References] | [References] | Who | TODO/DONE |
```

### Column Explanations

**Guardrail**: Name of the guardrail (1-8 core, plus preset guardrails)

**Requirements**: References to user stories/acceptance criteria where this guardrail is addressed
- Format: `[US-1, AC-1.2: Brief description]`
- Example: `[US-1, AC-1.3: 80% coverage target, integration tests]`

**Design**: References to design.md sections
- Format: `[Section 4.2: Brief description]` or `TBD` (if not designed yet)
- Example: `[Section 4.2: pytest + coverage.py configuration]`

**Tasks/Tests**: References to tasks.md items
- Format: `[Task 3.1: Brief description]` or `TBD` (if not broken down yet)
- Example: `[Task 3.1: Write test_hello.py, Task 3.2: Run coverage report]`

**Owner**: Who's responsible (Dev, QA, DBA, Security, etc.)

**Status**: TODO, IN_PROGRESS, DONE, or N/A (with reason)

---

## When to Mark Guardrails N/A

**Marking N/A is allowed but requires justification.**

### Valid N/A Examples

**Guardrail 6: Data Validation**
```markdown
| 6. Data Validation | N/A - No input parameters | N/A | N/A | - | N/A |
```
✅ Valid: GET endpoint with no query params

**Guardrail 7: Database Migrations**
```markdown
| 7. Database Migrations | N/A - Read-only database access | N/A | N/A | - | N/A |
```
✅ Valid: Feature only reads from external database

**Guardrail 8: Documentation (specific aspect)**
```markdown
| 8. Documentation | [US-1: API docs only] - No architecture changes | [Section 5: OpenAPI] | [Task 4.1] | Dev | TODO |
```
✅ Valid: Simple endpoint doesn't need architecture docs

### Invalid N/A Examples

**Guardrail 1: Testing Coverage**
```markdown
| 1. Testing Coverage | N/A - We'll test manually | N/A | N/A | - | N/A |
```
❌ Invalid: Manual testing doesn't meet the coverage requirement

**Guardrail 2: Security Basics**
```markdown
| 2. Security Basics | N/A - Internal tool only | N/A | N/A | - | N/A |
```
❌ Invalid: Internal tools still need security

**Guardrail 3: Error Handling**
```markdown
| 3. Error Handling | N/A - Simple endpoint, won't fail | N/A | N/A | - | N/A |
```
❌ Invalid: Everything can fail (DB down, network issues, etc.)

---

## Practice: Complete a Guardrail Matrix

Let's practice filling out a coverage matrix for a user login feature.

### Feature Requirements

```markdown
## User Stories

### US-1: User Login

**As a** registered user
**I want to** log in with email and password
**So that** I can access my account

**Acceptance Criteria:**
- [ ] AC-1.1: Returns 200 + JWT token on valid credentials
- [ ] AC-1.2: Returns 401 on invalid credentials
- [ ] AC-1.3: Rate limits to 5 attempts per 15 minutes per IP
- [ ] AC-1.4: Locks account after 10 failed attempts

### US-2: User Logout

**As a** logged-in user
**I want to** log out
**So that** my session is terminated

**Acceptance Criteria:**
- [ ] AC-2.1: Invalidates JWT token
- [ ] AC-2.2: Returns 200 on success
```

### Question-Pack Answers

```markdown
### Security
- Auth method: JWT with 15-minute expiry
- Password storage: bcrypt cost 12
- Rate limiting: 5 attempts per 15 minutes per IP
- Account lockout: 10 failed attempts, unlock after 1 hour or admin action

### Testing
- Coverage target: 90% (authentication is critical)
- Test types: Integration (all flows), unit (password verification, JWT generation), security (brute force, token tampering)

### API Design
- Base path: /api/v1
- Endpoints: POST /auth/login, POST /auth/logout
- Response format: JSON with consistent structure

### Data Model
- Table: users (id, email, password_hash, failed_attempts, locked_until, created_at)
- Table: revoked_tokens (token_jti, revoked_at, expires_at)
- Indexes: email (UNIQUE), token_jti
```

---

### Your Task: Fill Out the Matrix

Try filling out the matrix yourself, then compare with the answer below.

**Template:**

```markdown
| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [Your answer] | TBD | TBD | ? | TODO |
| 2. Security Basics | [Your answer] | TBD | TBD | ? | TODO |
| 3. Error Handling | [Your answer] | TBD | TBD | ? | TODO |
| 4. Logging & Observability | [Your answer] | TBD | TBD | ? | TODO |
| 5. API Design | [Your answer] | TBD | TBD | ? | TODO |
| 6. Data Validation | [Your answer] | TBD | TBD | ? | TODO |
| 7. Database Migrations | [Your answer] | TBD | TBD | ? | TODO |
| 8. Documentation | [Your answer] | TBD | TBD | ? | TODO |
```

---

### Answer

```markdown
| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [US-1, US-2: 90% coverage target, integration + unit + security tests] | TBD | TBD | QA + Dev | TODO |
| 2. Security Basics | [US-1, AC-1.3, AC-1.4: JWT auth, bcrypt cost 12, rate limiting, account lockout] | TBD | TBD | Security + Dev | TODO |
| 3. Error Handling | [AC-1.2: Return 401 on invalid creds, AC-1.3: Return 429 on rate limit] | TBD | TBD | Dev | TODO |
| 4. Logging & Observability | [US-1: Log all login attempts with IP, timestamp, success/failure] | TBD | TBD | Dev | TODO |
| 5. API Design | [US-1, US-2: /api/v1/auth/login, /api/v1/auth/logout, JSON responses] | TBD | TBD | Dev | TODO |
| 6. Data Validation | [US-1: Validate email format, password presence, sanitize inputs] | TBD | TBD | Dev | TODO |
| 7. Database Migrations | [US-1: Migration for users table + revoked_tokens table, indexes] | TBD | TBD | DBA + Dev | TODO |
| 8. Documentation | [US-1, US-2: OpenAPI docs with request/response examples, auth flow diagram] | TBD | TBD | Dev + TechWriter | TODO |
```

**Key points:**
- **Requirements column**: Specific references to user stories and acceptance criteria
- **Design/Tasks**: "TBD" is fine during requirements phase
- **Owner**: Security guardrail involves Security team
- **Status**: All TODO (nothing implemented yet)

---

## Common Mistakes to Avoid

### Mistake 1: Too Vague

❌ **Bad:**
```markdown
| 1. Testing Coverage | We'll write tests | TBD | TBD | Dev | TODO |
```

✅ **Good:**
```markdown
| 1. Testing Coverage | [US-1: 80% target, integration tests for all endpoints] | TBD | TBD | Dev | TODO |
```

### Mistake 2: Marking N/A Without Reason

❌ **Bad:**
```markdown
| 6. Data Validation | N/A | N/A | N/A | - | N/A |
```

✅ **Good:**
```markdown
| 6. Data Validation | N/A - No input parameters (GET endpoint, no query params) | N/A | N/A | - | N/A |
```

### Mistake 3: Not Updating Design/Tasks Columns

❌ **Bad:** Leave "TBD" forever

✅ **Good:** Update as you write design.md and tasks.md:
```markdown
| 1. Testing Coverage | [US-1: 80% target] | [Section 4.2: pytest setup, fixtures] | [Task 3.1: test_hello.py, Task 3.2: coverage report] | Dev | TODO |
```

### Mistake 4: Missing Guardrails

❌ **Bad:** Only include 5 out of 8 guardrails

✅ **Good:** Include all 8 core guardrails (+ preset guardrails if applicable)

### Mistake 5: No Owner

❌ **Bad:**
```markdown
| Owner | Status |
|-------|--------|
| ? | TODO |
```

✅ **Good:**
```markdown
| Owner | Status |
|-------|--------|
| Dev + QA | TODO |
```

---

## Guardrails for Different Presets

### SaaS Preset (+5 Guardrails)

If you initialized with `ldf init --preset saas`, you have 13 total guardrails:

**Additional SaaS Guardrails:**
- **9. Multi-Tenancy (RLS)**: Row-Level Security with tenant_id
- **10. Tenant Isolation**: Cannot access other tenant's data
- **11. Subscription Management**: Grace periods, downgrades, cancellations
- **12. Usage Metering**: Track API calls, storage, compute
- **13. Data Export**: GDPR compliance, user data download

**Example SaaS guardrail in matrix:**

```markdown
| 9. Multi-Tenancy (RLS) | [US-1: All queries filter by tenant_id] | [Section 3.3: PostgreSQL RLS policies] | [Task 2.2: Enable RLS, Task 2.3: Create policies] | DBA + Dev | TODO |
```

### Fintech Preset (+7 Guardrails)

**Additional Fintech Guardrails:**
- **9. Audit Logging**: Immutable financial transaction logs
- **10. Idempotency**: Duplicate requests don't double-charge
- **11. Reconciliation**: Daily balance checks
- **12. PCI Compliance**: Payment card data handling
- **13. Transaction Atomicity**: All-or-nothing operations
- **14. Fraud Detection**: Rules engine for suspicious activity
- **15. Regulatory Reporting**: SOC2, PCI-DSS evidence

---

## Next Steps

Now that you understand guardrails:

1. **Review your first spec** from [Tutorial 1](01-first-spec.md) - can you improve the coverage matrix?

2. **Try a complex example**: Create a spec for a user registration feature with all 8 guardrails filled out

3. **Continue learning**:
   - [Tutorial 3: Working with Question-Packs](03-question-packs.md) - Deep dive into answerpacks
   - [Guardrail Examples](../visual-guides/guardrail-examples.md) - Real coverage matrices for different feature types

4. **Explore presets**: If your project is SaaS or Fintech, see how the additional guardrails apply

---

## Quick Reference: The 8 Core Guardrails

| # | Guardrail | Key Requirement |
|---|-----------|-----------------|
| **1** | Testing Coverage | 80% minimum, 90% for critical paths |
| **2** | Security Basics | OWASP Top 10, secure defaults |
| **3** | Error Handling | No silent failures, structured errors |
| **4** | Logging & Observability | Log key events, enable debugging |
| **5** | API Design | Versioned, consistent, documented |
| **6** | Data Validation | Validate inputs, sanitize outputs |
| **7** | Database Migrations | Versioned, reversible schema changes |
| **8** | Documentation | Code, API, and setup docs |

---

## Troubleshooting

### Q: What if a guardrail doesn't apply to my feature?

**A:** Mark it N/A with a specific reason:
```markdown
| 7. Database Migrations | N/A - Feature doesn't touch database (external API client) | N/A | N/A | - | N/A |
```

### Q: Can I add custom guardrails?

**A:** Yes! See [Customization Guide](../customization.md) for how to add project-specific guardrails.

### Q: How detailed should the Requirements column be?

**A:** Brief but specific. Include user story references and key details:
- ✅ Good: `[US-1, AC-1.2: 80% coverage, integration + unit tests]`
- ❌ Too brief: `[US-1]`
- ❌ Too detailed: `[US-1, AC-1.2: 80% coverage target with pytest using fixtures for database setup and mocking external APIs with responses library and...]`

### Q: What if I'm not sure about a guardrail during requirements phase?

**A:** Write "TBD - needs research" and add to "Outstanding Questions" section. Don't proceed to design until answered.

---

**Next Tutorial**: [Working with Question-Packs](03-question-packs.md)
