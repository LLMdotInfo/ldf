# Guardrail Coverage Matrix Examples

Real-world examples showing how to complete the guardrail coverage matrix correctly (no [TBD] placeholders).

---

## Table of Contents

- [Example 1: Simple API Endpoint (Hello World)](#example-1-simple-api-endpoint-hello-world)
- [Example 2: User Authentication System](#example-2-user-authentication-system)
- [Example 3: SaaS Multi-Tenant Feature](#example-3-saas-multi-tenant-feature)
- [Example 4: Fintech Payment Processing](#example-4-fintech-payment-processing)
- [Common Patterns](#common-patterns)
- [Tips for Completing Your Matrix](#tips-for-completing-your-matrix)

---

## Example 1: Simple API Endpoint (Hello World)

**Feature:** GET /hello endpoint

**Complexity:** Simple
**Guardrails:** Core 8 only
**Applicable:** 6/8 (2 N/A)

### Guardrail Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [US-1, AC-1.2: 80% target] | [Section 4.1: Integration tests] | [Task 3.1: Write test_hello_endpoint] | Dev | TODO |
| 2. Security Basics | N/A - Public read-only endpoint, no auth | N/A | N/A | - | N/A |
| 3. Error Handling | [US-1, AC-1.3: 500 on errors] | [Section 3.2: FastAPI exception handler] | [Task 2.2: Add error middleware] | Dev | TODO |
| 4. Logging & Observability | [US-1: Log all requests] | [Section 3.3: Request logging middleware] | [Task 2.3: Add logging] | Dev | TODO |
| 5. API Design | [US-1: JSON response, /api/v1 prefix] | [Section 2.1: Route definition] | [Task 1.1: Create route] | Dev | TODO |
| 6. Data Validation | N/A - No input parameters | N/A | N/A | - | N/A |
| 7. Database Migrations | N/A - No database access | N/A | N/A | - | N/A |
| 8. Documentation | [US-1: OpenAPI auto-docs] | [Section 4.2: FastAPI docstrings] | [Task 3.2: Add docstrings] | Dev | TODO |

### Key Lessons

✅ **It's OK to mark guardrails N/A** - with a clear reason
✅ **Link to specific requirements** - Use US-X, AC-X.Y notation
✅ **Link to design sections** - Section numbers make it trackable
✅ **Link to task numbers** - Task X.Y notation
✅ **Owner can be role or person** - "Dev" or "Alice"

---

## Example 2: User Authentication System

**Feature:** Email/password login with JWT

**Complexity:** Medium
**Guardrails:** Core 8 only
**Applicable:** 8/8 (all apply)

### Guardrail Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [US-1..5: 90% for auth, 85% for endpoints] | [S4.1: pytest fixtures, integration tests] | [T-4.1: Unit tests, T-4.2: Integration tests, T-4.3: Security tests] | Alice | DONE |
| 2. Security Basics | [US-2: bcrypt cost 12, US-3: Account lockout after 5 fails, US-5: TOTP MFA] | [S2.1: AuthService with bcrypt, S2.3: RateLimiter, S2.4: MFAService] | [T-2.3: Implement password hashing, T-2.4: Add rate limiting, T-3.4: MFA enrollment] | Bob | IN_PROGRESS |
| 3. Error Handling | [US-2, AC-2.3: Generic 401 for all auth failures (no enumeration)] | [S3.2: AuthenticationError class] | [T-2.5: Exception handlers, T-3.5: Error middleware] | Alice | DONE |
| 4. Logging & Observability | [US-2: Log all auth attempts (success/fail) with IP, no passwords in logs] | [S3.3: Structured logging with correlation IDs] | [T-3.6: Add auth event logging] | Charlie | TODO |
| 5. API Design | [US-1..5: /api/v1/auth/* endpoints, RFC 7807 error format] | [S3.1: FastAPI router, OpenAPI specs] | [T-1.1: Create router structure] | Alice | DONE |
| 6. Data Validation | [US-1, AC-1.2: Email format, AC-1.3: 12+ char password with complexity] | [S2.2: Pydantic schemas with validators] | [T-2.1: Email validation, T-2.2: Password policy] | Bob | DONE |
| 7. Database Migrations | [All: users, refresh_tokens, login_attempts tables] | [S1.2: Alembic migrations] | [T-1.2: Create migration, T-1.3: Test up/down] | Alice | DONE |
| 8. Documentation | [All: API docs, README for setup, inline comments] | [S4.2: OpenAPI with examples, docstrings] | [T-5.1: Write API docs, T-5.2: Update README] | Charlie | TODO |

### Key Lessons

✅ **Multiple references per cell** - US-1..5 means US-1 through US-5
✅ **Specific details in brackets** - bcrypt cost 12, 90% coverage
✅ **Multiple design sections** - S2.1, S2.3, S2.4
✅ **Multiple tasks** - T-2.3, T-2.4, T-3.4
✅ **Status progression** - TODO → IN_PROGRESS → DONE
✅ **Different owners** - Alice, Bob, Charlie for different concerns

---

## Example 3: SaaS Multi-Tenant Feature

**Feature:** Tenant-isolated blog posts

**Complexity:** Medium-High
**Guardrails:** Core 8 + SaaS Preset (+5)
**Applicable:** 13/13 (all apply)

### Guardrail Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| **CORE GUARDRAILS** |
| 1. Testing Coverage | [US-1..3: 80% overall] | [S5: pytest with tenant fixtures] | [T-6.1: Unit tests, T-6.2: RLS tests] | Dev | TODO |
| 2. Security Basics | [US-1: JWT auth, tenant_id in claims] | [S2.1: Auth middleware] | [T-2.1: Implement JWT validation] | Security | TODO |
| 3. Error Handling | [All: 404 if post not in tenant] | [S3.2: TenantIsolationError] | [T-3.3: Error handlers] | Dev | TODO |
| 4. Logging & Observability | [All: Log tenant_id with all requests] | [S3.3: tenant_id in log context] | [T-3.4: Add logging] | Ops | TODO |
| 5. API Design | [All: /api/v1/posts endpoints] | [S3.1: FastAPI routes] | [T-1.1: Create routes] | Dev | TODO |
| 6. Data Validation | [US-1: Validate post title, body] | [S2.2: Pydantic schemas] | [T-2.2: Schema validation] | Dev | TODO |
| 7. Database Migrations | [All: Add tenant_id to posts table] | [S1.2: Alembic migration] | [T-1.2: Create migration] | Dev | TODO |
| 8. Documentation | [All: API docs] | [S5.2: OpenAPI] | [T-7.1: Write docs] | TechWriter | TODO |
| **SAAS PRESET GUARDRAILS** |
| 9. Multi-Tenancy (RLS) | [All: tenant_id column, RLS policies] | [S1.1: PostgreSQL RLS ON posts table, Policy: tenant_id = current_setting('app.tenant_id')] | [T-1.3: Enable RLS, T-1.4: Create policy, T-6.3: Test cross-tenant access blocked] | DB Admin | TODO |
| 10. Tenant Isolation | [US-2: Can only view own tenant's posts] | [S2.3: set_config before queries] | [T-2.3: Tenant context manager] | Security | TODO |
| 11. Audit Logging | [US-3: Log all post creation/updates with tenant] | [S4.1: Audit log table with tenant_id, user_id, action] | [T-4.1: Create audit trigger] | Compliance | TODO |
| 12. Subscription Checks | [US-1: Check tenant's plan allows post creation] | [S2.4: SubscriptionService.can_create_post()] | [T-2.4: Implement quota check] | Billing | TODO |
| 13. Tenant Data Separation | [All: No cross-tenant data leaks] | [S2.5: Tenant middleware validates all queries] | [T-2.5: Add tenant validation, T-6.4: Test data isolation] | Security | TODO |

### Key Lessons

✅ **Separate core and preset guardrails** - Clearly labeled sections
✅ **RLS gets very specific** - Exact SQL in Design column
✅ **Tenant isolation appears in multiple guardrails** - Shows interconnected concerns
✅ **Different owners** - Dev, Security, DB Admin, Compliance, Billing
✅ **Cross-references** - RLS + Tenant Isolation related
✅ **Preset awareness** - All 13 guardrails must be addressed

---

## Example 4: Fintech Payment Processing

**Feature:** Process credit card payments

**Complexity:** High
**Guardrails:** Core 8 + Fintech Preset (+7)
**Applicable:** 15/15 (all apply)

### Guardrail Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| **CORE GUARDRAILS** |
| 1. Testing Coverage | [All: 95% for payment logic] | [S6: pytest with mocked Stripe, ledger tests] | [T-7.1: Unit tests, T-7.2: Ledger reconciliation tests] | QA | TODO |
| 2. Security Basics | [US-1: No card data stored, Stripe tokenization] | [S2.1: Stripe.js client-side, server only receives token] | [T-2.1: Integrate Stripe.js] | Security | TODO |
| 3. Error Handling | [US-1: Distinguish payment failures (declined vs error)] | [S3.2: PaymentDeclinedError, PaymentGatewayError] | [T-3.2: Error handlers with proper codes] | Dev | TODO |
| 4. Logging & Observability | [All: Log payment_id, amount, status - NO card data] | [S3.3: Structured logs with payment_id] | [T-3.3: Add payment event logging] | Ops | TODO |
| 5. API Design | [All: /api/v1/payments endpoints, idempotency headers] | [S3.1: POST /payments with X-Idempotency-Key] | [T-1.1: Idempotent payment endpoint] | Dev | TODO |
| 6. Data Validation | [US-1: Validate amount > 0, currency code] | [S2.2: Pydantic with Decimal validator] | [T-2.2: Amount validation] | Dev | TODO |
| 7. Database Migrations | [All: payments, ledger_entries tables] | [S1.2: Alembic with NUMERIC for money] | [T-1.2: Create migration with NUMERIC(15,2)] | DB | TODO |
| 8. Documentation | [All: API docs, compliance docs] | [S6.2: OpenAPI + PCI DSS docs] | [T-8.1: API docs, T-8.2: Compliance docs] | Compliance | TODO |
| **FINTECH PRESET GUARDRAILS** |
| 9. Double-Entry Ledger | [All: Every payment creates 2 entries] | [S4.1: LedgerService with debit/credit balance validation] | [T-4.1: Implement ledger, T-4.2: Balance validation] | FinEng | TODO |
| 10. Money Precision | [All: Use NUMERIC(15,2), never FLOAT] | [S1.1: NUMERIC columns, Python Decimal everywhere] | [T-1.3: Convert to Decimal, T-7.3: Test precision] | DB | DONE |
| 11. Idempotency | [US-1: Duplicate requests don't double-charge] | [S5.1: Idempotency key store (Redis), 24hr TTL] | [T-5.1: Implement idempotency layer] | Backend | TODO |
| 12. Reconciliation | [Daily: Stripe balance = ledger balance] | [S5.2: Nightly job comparing Stripe API to ledger sum] | [T-5.2: Create reconciliation job, T-5.3: Alert on mismatch] | FinEng | TODO |
| 13. PCI Compliance | [All: No card data in logs/DB, TLS 1.2+] | [S2.3: Tokenization only, TLS enforcement] | [T-2.3: Verify no card data logged] | Security | TODO |
| 14. Transaction Rollback | [US-1: Failed payments don't create partial ledger entries] | [S4.2: DB transactions, rollback on any error] | [T-4.3: Wrap in transaction, T-7.4: Test rollback] | Backend | TODO |
| 15. Audit Trail | [All: Immutable log of all payment state changes] | [S4.3: Append-only audit table] | [T-4.4: Create audit table, T-4.5: Triggers] | Compliance | TODO |

### Key Lessons

✅ **Fintech has many additional guardrails** - 15 total
✅ **Money precision very explicit** - NUMERIC(15,2), Python Decimal
✅ **Idempotency critical for payments** - Prevents double charges
✅ **Reconciliation is ongoing** - Daily job, not one-time
✅ **Multiple compliance concerns** - PCI, ledger accuracy, audit trail
✅ **Higher testing coverage** - 95% vs standard 80%
✅ **Financial engineering owner** - Specialized role for ledger/reconciliation

---

## Common Patterns

### Pattern 1: Marking N/A

**Good:**
```markdown
| 7. DB Migrations | N/A - Read-only API, no database access | N/A | N/A | - | N/A |
```

**Bad:**
```markdown
| 7. DB Migrations | N/A | N/A | N/A | - | N/A |
```

**Always explain *why* it's N/A.**

---

### Pattern 2: Linking Multiple Items

**Good:**
```markdown
| 1. Testing | [US-1, US-2, US-3: 80% target, US-4: 90% critical path] | [S4.1, S4.2] | [T-6.1, T-6.2, T-6.3] | QA | DONE |
```

**Bad:**
```markdown
| 1. Testing | [TBD] | [TBD] | [TBD] | [TBD] | TODO |
```

**Be specific about what's being tested.**

---

### Pattern 3: Progressive Status

As you work through phases:

**Requirements phase:**
```markdown
| Status |
|--------|
| TODO   |  ← All start here
```

**Design phase:**
```markdown
| Status |
|--------|
| TODO   |  ← Update Design column, Status stays TODO
```

**Tasks phase:**
```markdown
| Status |
|-------------|
| TODO        |  ← Update Tasks column
```

**Implementation:**
```markdown
| Status      |
|-------------|
| IN_PROGRESS |  ← Working on it
```

**Complete:**
```markdown
| Status |
|--------|
| DONE   |  ← All columns filled, tests passing
```

---

### Pattern 4: Owner Assignment

**Individual:**
```markdown
| Owner |
|-------|
| @alice |
```

**Role:**
```markdown
| Owner    |
|----------|
| Backend  |
| Security |
| DevOps   |
```

**Multiple (split responsibility):**
```markdown
| Owner        |
|--------------|
| Alice (dev)  |
| Bob (review) |
```

---

### Pattern 5: Detailed Requirements References

**Good - Specific:**
```markdown
| 2. Security | [US-2: bcrypt cost 12, US-3: lockout after 5 fails, Security QP: TOTP MFA] |
```

**Bad - Vague:**
```markdown
| 2. Security | [Security stuff] |
```

---

### Pattern 6: Design Section Numbering

**Good - Traceable:**
```markdown
| 5. API Design | [S3.1: FastAPI router, S3.2: Endpoint definitions, S3.3: Error schemas] |
```

**Bad - No references:**
```markdown
| 5. API Design | [Described in design doc] |
```

---

## Tips for Completing Your Matrix

### 1. Start with N/A items
**Why:** Easy wins, clarifies scope immediately.

Example:
```markdown
| 6. Data Validation | N/A - No user input for this endpoint | N/A | N/A | - | N/A |
| 7. DB Migrations | N/A - Read-only API, uses existing schema | N/A | N/A | - | N/A |
```

---

### 2. Link to specific requirements
**Use:** US-X, AC-X.Y notation, not just "requirements".

Example:
```markdown
| 1. Testing | [US-1, US-2, AC-1.1-1.4, AC-2.1-2.3: 85% coverage target] |
```

---

### 3. Be specific in Design column
**Include:** Section numbers, component names, specific technologies.

Example:
```markdown
| 2. Security | [S2.1: AuthService with bcrypt cost 12, S2.3: RateLimiter (5 req/15min)] |
```

---

### 4. Map to task numbers
**Use:** Task X.Y notation for trackability.

Example:
```markdown
| 3. Error Handling | [T-2.5: Add exception middleware, T-3.2: Test error cases] |
```

---

### 5. Update status as you progress
**Don't** leave stale statuses.

**Do** update regularly:
- TODO → IN_PROGRESS when starting work
- IN_PROGRESS → DONE when complete and tested

---

### 6. One owner per guardrail
**Ensure** clear responsibility.

If multiple people involved:
```markdown
| Owner            |
|------------------|
| Alice (primary)  |
| Bob (reviewer)   |
```

---

### 7. Include preset guardrails
**If** using SaaS/Fintech/Healthcare/API-only preset.

**Add** those guardrails to the matrix.

---

## Validation Checklist

Before running `ldf lint`:

- [ ] All 8 core guardrails present
- [ ] Preset guardrails added (if using preset)
- [ ] No [TBD] placeholders
- [ ] N/A items have clear reasons
- [ ] Requirements column filled for applicable guardrails
- [ ] Owner assigned for each applicable guardrail
- [ ] Status reflects current reality

---

## Troubleshooting Common Errors

### Error: "Guardrail matrix incomplete"

**Cause:** Missing guardrails in table.

**Solution:** Ensure all 8 core (+ preset) guardrails are listed.

---

### Error: "Guardrail N/A without reason"

**Cause:** Marked N/A but didn't explain why.

**Solution:**
```markdown
| 6. Data Validation | N/A - No user input parameters | N/A | N/A | - | N/A |
```

---

### Error: "Template markers found"

**Cause:** Left [TBD] or [TODO] in matrix.

**Solution:** Replace all placeholders with actual references or mark N/A with reason.

---

## Related Documentation

- **[Workflow Diagrams](workflows.md#guardrail-coverage-flow)** - Guardrail flow visualization
- **[Understanding Guardrails Tutorial](../tutorials/02-guardrails.md)** - Deep dive
- **[Customization Guide](../customization.md)** - Custom guardrails
- **[Concepts](../concepts.md#guardrails)** - Philosophy

---

**Need help with your matrix?**
- Review examples above
- Follow patterns section
- Check validation checklist
- Ask in [GitHub Discussions](https://github.com/LLMdotInfo/ldf/discussions)
