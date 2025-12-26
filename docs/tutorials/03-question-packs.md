# Tutorial: Working with Question-Packs

> **For**: Users familiar with basic LDF concepts
> **Time**: 25 minutes
> **Prerequisites**: [Understanding Guardrails](02-guardrails.md)
> **What you'll learn**: Answer question-packs effectively, create answerpacks, reference answers in specs

---

## What Are Question-Packs?

**Question-packs** are pre-built templates of critical questions you should answer before designing a feature.

Think of them like an **architect's checklist** before building a house:
- "What's the foundation type?" (clay, bedrock, sand?)
- "How many floors?" (affects structural requirements)
- "Fire safety requirements?" (sprinklers, exits, materials)

**In LDF**, question-packs surface critical decisions **early** when they're cheap to make, not late when they're expensive to change.

---

## Why Question-Packs Matter

### Without Question-Packs

Developer starts coding a user authentication feature:

```python
# Day 1: Write authentication
def login(email, password):
    user = db.get_user(email)
    if user.password == password:  # Oops, plaintext!
        return {"token": "abc123"}  # Oops, not a real JWT!

# Day 5: Security review finds issues
# "You need to hash passwords with bcrypt!"
# "You need proper JWTs with expiry!"
# "You need rate limiting!"

# Day 6-10: Rewrite everything
```

**Cost:** 5 days wasted + complete rewrite

---

### With Question-Packs

Developer answers security question-pack before coding:

```yaml
# .ldf/answerpacks/user-auth/security.yaml
spec: user-auth
pack: security
answers:
  auth_method: JWT
  password_storage: bcrypt cost 12
  session_duration: 15 minutes
  refresh_token_duration: 7 days
  rate_limiting: 5 login attempts per 15 minutes per IP
```

Then writes code based on answers:

```python
# Day 1: Write authentication (correct from the start)
from passlib.hash import bcrypt
import jwt

def login(email: str, password: str) -> LoginResponse:
    user = db.get_user(email)

    # Answer: "bcrypt cost 12"
    if not bcrypt.verify(password, user.password_hash):
        return error_response(401, "INVALID_CREDENTIALS")

    # Answer: "JWT with 15-minute expiry"
    token = jwt.encode({
        "user_id": user.id,
        "exp": now() + timedelta(minutes=15)
    }, secret_key)

    return {"access_token": token}
```

**Cost:** 30 minutes to answer questions + correct implementation

**Savings:** 4.5 days + no rework

---

## The Core Question-Packs

Every LDF project has **4 core question-packs**:

| Pack | Purpose | Example Questions |
|------|---------|-------------------|
| **security** | Auth, secrets, vulnerabilities | How are passwords stored? What authentication method? |
| **testing** | Coverage, test types, strategies | What's the coverage target? What test types are needed? |
| **api-design** | REST, versioning, errors | What's the base path? How are errors formatted? |
| **data-model** | Schema, migrations, indexes | What tables are needed? What indexes? |

These are **always installed** with `ldf init`.

---

## Optional Question-Packs

Depending on your domain, you can add optional packs:

| Pack | When to Use | Example Questions |
|------|-------------|-------------------|
| **billing** | Payment processing, subscriptions | Payment gateway? Subscription model? Invoice generation? |
| **multi-tenancy** | SaaS applications | How is tenant isolation enforced? Shared or separate databases? |
| **provisioning** | Async jobs, external services | Queue system? Retry strategy? Timeout handling? |
| **webhooks** | Event delivery | Signature verification? Retry logic? Delivery guarantees? |

**Add optional packs:**
```bash
ldf add-pack billing
ldf add-pack multi-tenancy
```

**Or specify during init:**
```bash
ldf init --question-packs security,testing,api-design,data-model,billing,webhooks
```

---

## Question-Pack Structure

Let's look inside a question-pack file:

**File:** `.ldf/question-packs/core/security.yaml`

```yaml
name: Security
category: core
description: Security and authentication decisions

questions:
  - id: auth_method
    question: What authentication method will be used?
    type: choice
    options:
      - JWT
      - Session cookies
      - OAuth 2.0
      - API keys
      - None (public endpoint)
    required: true
    hint: Consider stateless (JWT) vs stateful (sessions) tradeoffs

  - id: password_storage
    question: How will passwords be stored?
    type: text
    required: true
    hint: "e.g., bcrypt cost 12, argon2id, scrypt"
    validation: Must not be 'plaintext' or 'MD5'

  - id: session_duration
    question: How long should sessions/tokens last?
    type: text
    required: false
    depends_on: auth_method
    hint: "e.g., 15 minutes (access), 7 days (refresh)"

  - id: rate_limiting
    question: What rate limiting is required?
    type: text
    required: true
    hint: "e.g., 5 requests per minute per IP, 100 per hour per user"

  - id: secrets_management
    question: How are secrets (API keys, DB passwords) managed?
    type: choice
    options:
      - Environment variables
      - Secrets management service (Vault, AWS Secrets Manager)
      - Encrypted config files
      - Hardcoded (NOT RECOMMENDED)
    required: true
```

**Key fields:**
- `id`: Unique identifier for the answer
- `question`: The actual question text
- `type`: `choice`, `text`, `boolean`, `number`
- `options`: For choice questions
- `required`: Must be answered?
- `hint`: Helpful examples or guidance
- `depends_on`: Only show if another answer is set
- `validation`: Rules for acceptable answers

---

## Creating Answerpacks

**Answerpacks** are your answers to question-packs, stored as YAML files.

### Step 1: Create a Spec

```bash
ldf create-spec user-auth
```

This creates `.ldf/specs/user-auth/requirements.md`.

### Step 2: Create Answerpack Directory

```bash
mkdir -p .ldf/answerpacks/user-auth
```

### Step 3: Answer the Security Pack

Create **`.ldf/answerpacks/user-auth/security.yaml`**:

```yaml
spec: user-auth
pack: security
created_at: 2024-01-15
updated_at: 2024-01-15

answers:
  auth_method: JWT
  password_storage: bcrypt cost 12
  session_duration: 15 minutes (access token), 7 days (refresh token)
  rate_limiting: 5 login attempts per 15 minutes per IP
  secrets_management: Environment variables

rationale:
  auth_method: |
    JWT chosen for stateless authentication, enabling horizontal scaling.
    No server-side session storage required.
    Refresh tokens stored in database for revocation capability.

  password_storage: |
    bcrypt cost 12 provides good security/performance balance.
    Cost factor can be increased later as hardware improves.
    Meets OWASP password storage recommendations.

  rate_limiting: |
    Prevents brute force attacks on login endpoint.
    5 attempts per 15 minutes strikes balance between security and UX.
    Based on OWASP authentication cheat sheet recommendations.
```

**Key sections:**
- `spec`: Name of the spec this answers
- `pack`: Which question-pack this answers
- `answers`: Your answers to each question (use question IDs as keys)
- `rationale`: **Optional but recommended** - explain non-obvious decisions

---

## Answering All Core Packs

For a complete feature, answer all 4 core packs:

### Security Pack (user-auth/security.yaml)

```yaml
spec: user-auth
pack: security
answers:
  auth_method: JWT
  password_storage: bcrypt cost 12
  session_duration: 15 minutes (access), 7 days (refresh)
  rate_limiting: 5 attempts per 15 min per IP
  secrets_management: Environment variables (.env file, not committed)
```

### Testing Pack (user-auth/testing.yaml)

```yaml
spec: user-auth
pack: testing
answers:
  coverage_target: 90%
  test_types: Integration (full login flow), Unit (password verification, JWT generation), Security (brute force, token tampering)
  test_framework: pytest
  mocking_strategy: Mock database with pytest fixtures, mock external services (email) with responses
  performance_tests: Load test with 100 concurrent logins
```

### API Design Pack (user-auth/api-design.yaml)

```yaml
spec: user-auth
pack: api-design
answers:
  base_path: /api/v1
  endpoints:
    - POST /auth/login
    - POST /auth/logout
    - POST /auth/refresh
  versioning_strategy: URL path versioning (/v1, /v2)
  error_format: |
    {
      "error": {
        "code": "INVALID_CREDENTIALS",
        "message": "Email or password incorrect",
        "details": []
      }
    }
  response_format: |
    {
      "data": {
        "access_token": "eyJ...",
        "refresh_token": "eyJ...",
        "expires_in": 900
      }
    }
```

### Data Model Pack (user-auth/data-model.yaml)

```yaml
spec: user-auth
pack: data-model
answers:
  tables:
    users:
      columns:
        - id (UUID, primary key)
        - email (VARCHAR(255), unique, not null)
        - password_hash (VARCHAR(255), not null)
        - failed_login_attempts (INT, default 0)
        - locked_until (TIMESTAMP, nullable)
        - created_at (TIMESTAMP, default NOW())
        - updated_at (TIMESTAMP, default NOW())
      indexes:
        - email (UNIQUE)
        - locked_until (WHERE locked_until > NOW())

    refresh_tokens:
      columns:
        - id (UUID, primary key)
        - user_id (UUID, foreign key to users.id, on delete cascade)
        - token_hash (VARCHAR(255), not null)
        - expires_at (TIMESTAMP, not null)
        - created_at (TIMESTAMP, default NOW())
      indexes:
        - token_hash
        - user_id
        - expires_at

  migrations:
    - 001_create_users_table.sql
    - 002_create_refresh_tokens_table.sql

  relationships:
    - users.id → refresh_tokens.user_id (one-to-many)
```

---

## Referencing Answerpacks in requirements.md

Once you've created answerpacks, **summarize** the key decisions in `requirements.md`:

**File:** `.ldf/specs/user-auth/requirements.md`

```markdown
# user-auth - Requirements

## Overview

Email/password authentication system with JWT tokens.

## User Stories

### US-1: User Login
...

## Question-Pack Answers

This section summarizes key decisions from answerpacks. See `.ldf/answerpacks/user-auth/` for complete details.

### Security

**Answerpack:** `.ldf/answerpacks/user-auth/security.yaml`

- **Authentication method:** JWT tokens (stateless, scalable)
- **Password storage:** bcrypt cost 12
- **Token duration:** 15-minute access tokens, 7-day refresh tokens
- **Rate limiting:** 5 login attempts per 15 minutes per IP
- **Secrets management:** Environment variables (.env file)

**Rationale:** JWT enables horizontal scaling without session storage. bcrypt cost 12 balances security and performance.

### Testing

**Answerpack:** `.ldf/answerpacks/user-auth/testing.yaml`

- **Coverage target:** 90% (authentication is security-critical)
- **Test types:** Integration (full flows), unit (bcrypt, JWT), security (brute force, tampering)
- **Framework:** pytest with fixtures for database mocking

### API Design

**Answerpack:** `.ldf/answerpacks/user-auth/api-design.yaml`

- **Endpoints:**
  - `POST /api/v1/auth/login` - Returns access + refresh tokens
  - `POST /api/v1/auth/logout` - Invalidates refresh token
  - `POST /api/v1/auth/refresh` - Returns new access token
- **Versioning:** URL path (/v1, /v2)
- **Error format:** Structured JSON with error codes

### Data Model

**Answerpack:** `.ldf/answerpacks/user-auth/data-model.yaml`

- **Tables:** users, refresh_tokens
- **Key columns:** email (UNIQUE), password_hash, failed_login_attempts, locked_until
- **Migrations:** 001_create_users, 002_create_refresh_tokens
- **Indexes:** email (UNIQUE), token_hash, expires_at

## Guardrail Coverage Matrix
...
```

**Key principles:**
- **Don't duplicate** - Summarize in requirements.md, full details in answerpack YAML
- **Link** - Reference the answerpack file location
- **Highlight** - Include the most critical decisions
- **Rationale** - Briefly explain non-obvious choices

---

## When to Use Optional Packs

### Billing Pack

**Use when:**
- Processing payments (Stripe, PayPal, etc.)
- Subscription management (monthly, annual)
- Invoice generation
- Refunds and disputes

**Example answerpack:**

```yaml
spec: subscription-management
pack: billing
answers:
  payment_gateway: Stripe
  subscription_model: Tiered (Free, Pro $29/mo, Enterprise $99/mo)
  billing_cycle: Monthly with annual discount (2 months free)
  payment_methods: Credit card, ACH (US only)
  failed_payment_handling: Retry 3 times (day 1, 3, 7), then downgrade to Free
  invoice_generation: PDF via Stripe Invoicing API
  refund_policy: Pro-rated refunds within 30 days
  tax_calculation: Stripe Tax (automatic sales tax)
```

### Multi-Tenancy Pack

**Use when:**
- SaaS application with multiple customers
- Each customer's data must be isolated
- Shared infrastructure across tenants

**Example answerpack:**

```yaml
spec: saas-core
pack: multi-tenancy
answers:
  isolation_model: Row-Level Security (RLS) with tenant_id column
  database_model: Shared database, shared schema
  tenant_identification: Subdomain (acme.yourapp.com) + JWT tenant_id claim
  cross_tenant_access: Forbidden - enforced by RLS policies
  tenant_provisioning: Automatic on signup, async job to create tenant record
  data_migration: Per-tenant export via Admin API
```

### Provisioning Pack

**Use when:**
- Long-running async jobs
- Integration with external services
- Batch processing

**Example answerpack:**

```yaml
spec: report-generation
pack: provisioning
answers:
  queue_system: Celery with Redis broker
  job_types: Generate monthly report (15-60 seconds), Generate annual report (5-10 minutes)
  retry_strategy: Exponential backoff, max 3 retries, 10-minute max delay
  timeout_handling: 30-minute timeout, then fail and notify user
  monitoring: Track job status in database, expose /jobs/:id API endpoint
  external_services: PDF generation via wkhtmltopdf, S3 for storage
```

### Webhooks Pack

**Use when:**
- Sending events to external systems
- User-configured webhook endpoints
- Event-driven architecture

**Example answerpack:**

```yaml
spec: webhook-delivery
pack: webhooks
answers:
  events:
    - user.created
    - user.updated
    - payment.succeeded
    - payment.failed
  signature_method: HMAC-SHA256 with per-webhook secret
  delivery_guarantee: At-least-once (retry on failure)
  retry_strategy: 5 retries with exponential backoff (10s, 1m, 10m, 1h, 24h)
  timeout: 10 seconds per attempt
  failure_handling: Mark webhook as failed after 5 retries, notify user via email
  payload_format: JSON with timestamp, event type, data
```

---

## Creating Custom Question-Packs

If none of the built-in packs fit your domain, create a custom pack.

### Step 1: Create Pack File

**File:** `.ldf/question-packs/custom/gaming.yaml`

```yaml
name: Gaming
category: custom
description: Questions for game development features

questions:
  - id: game_engine
    question: What game engine or framework is used?
    type: choice
    options:
      - Unity
      - Unreal Engine
      - Godot
      - Custom engine
      - Browser-based (Phaser, Three.js)
    required: true

  - id: multiplayer
    question: Does this feature involve multiplayer?
    type: boolean
    required: true

  - id: networking_model
    question: If multiplayer, what networking model?
    type: choice
    options:
      - Client-server
      - Peer-to-peer
      - Lockstep (deterministic)
      - Server authoritative
    depends_on: multiplayer
    required: false

  - id: anti_cheat
    question: What anti-cheat measures are needed?
    type: text
    depends_on: multiplayer
    hint: "e.g., Server-side validation, client signatures, rate limiting"

  - id: save_system
    question: How is game state persisted?
    type: choice
    options:
      - Local save files
      - Cloud saves
      - Database backend
      - Blockchain (Web3)
      - Not applicable
    required: true
```

### Step 2: Use Custom Pack

```bash
# Add to your project
ldf add-pack gaming
```

Or manually add to `.ldf/config.yaml`:

```yaml
question_packs:
  core:
    - security
    - testing
    - api-design
    - data-model
  optional:
    - billing
  custom:
    - gaming  # Your custom pack
```

### Step 3: Answer Custom Pack

**File:** `.ldf/answerpacks/player-inventory/gaming.yaml`

```yaml
spec: player-inventory
pack: gaming
answers:
  game_engine: Unity
  multiplayer: true
  networking_model: Server authoritative
  anti_cheat: Server-side inventory validation, client cannot modify item counts
  save_system: Database backend (PostgreSQL) with hourly cloud backup
```

---

## Best Practices

### 1. Answer Questions Before Design

❌ **Wrong order:**
```
Create spec → Write design.md → "Oh, should we use JWT or sessions?" → Redesign
```

✅ **Correct order:**
```
Create spec → Answer question-packs → Write requirements.md → Design with answers in mind
```

### 2. Provide Rationale for Non-Obvious Decisions

❌ **Not helpful:**
```yaml
answers:
  auth_method: OAuth 2.0
```

✅ **Helpful:**
```yaml
answers:
  auth_method: OAuth 2.0

rationale:
  auth_method: |
    Chose OAuth 2.0 because:
    - Need integration with Google, GitHub, Microsoft SSO
    - Don't want to handle password storage/resets
    - Enterprise customers require SSO support
    - Delegation model allows third-party app integrations
```

### 3. Update Answerpacks When Requirements Change

If you change your mind (e.g., switching from JWT to sessions):

1. Update the answerpack YAML file
2. Update the summary in requirements.md
3. Update design.md and tasks.md if they exist
4. Re-run `ldf lint` to ensure consistency
5. Document why you changed (in git commit or changelog)

### 4. Don't Leave Questions Unanswered

❌ **Procrastinating:**
```yaml
answers:
  auth_method: TBD - need to research
  password_storage: Not sure yet
```

This defeats the purpose! **Research now** while it's cheap to change.

✅ **If truly blocked:**

1. Mark as "TBD - needs research" in answerpack
2. Add to "Outstanding Questions" in requirements.md
3. **Don't proceed to design phase** until answered
4. Set a deadline (e.g., "Research by Friday")

### 5. Version Control Answerpacks

Answerpacks contain critical architectural decisions.

**In .gitignore:**
```gitignore
# Only ignore if answerpacks contain secrets
.ldf/answerpacks/**/secrets.yaml

# Commit everything else
!.ldf/answerpacks/**/*.yaml
```

**Why version control?**
- Track decision history
- Team can review in pull requests
- New team members understand past choices
- Audit trail for compliance

---

## Example: Complete Answerpack Workflow

Let's walk through answering all packs for a **subscription payment feature**.

### Step 1: Create Spec

```bash
ldf create-spec subscription-payments
```

### Step 2: Identify Required Packs

- **Core packs:** security, testing, api-design, data-model
- **Optional packs:** billing (payment processing), webhooks (Stripe events)

Add billing pack:
```bash
ldf add-pack billing
```

### Step 3: Create Answerpack Directory

```bash
mkdir -p .ldf/answerpacks/subscription-payments
```

### Step 4: Answer Security Pack

**File:** `security.yaml`

```yaml
spec: subscription-payments
pack: security
answers:
  auth_method: JWT (from existing auth system)
  payment_data_storage: PCI-compliant (use Stripe, don't store card numbers)
  secrets_management: Stripe API keys in environment variables
  rate_limiting: 10 payment attempts per hour per user
  fraud_detection: Stripe Radar + custom rules (block >$10k without verification)

rationale:
  payment_data_storage: |
    Using Stripe means we never touch raw card data.
    PCI compliance is Stripe's responsibility.
    We only store Stripe customer IDs and payment method IDs.
```

### Step 5: Answer Testing Pack

**File:** `testing.yaml`

```yaml
spec: subscription-payments
pack: testing
answers:
  coverage_target: 95%
  test_types: |
    - Integration: Full payment flow with Stripe test mode
    - Unit: Price calculation, proration logic
    - E2E: Selenium tests for checkout UI
    - Security: Test failed payments, refund abuse, duplicate charges
  test_framework: pytest + Stripe test fixtures
  mocking_strategy: Use Stripe test mode (not mocks) for realistic testing
```

### Step 6: Answer API Design Pack

**File:** `api-design.yaml`

```yaml
spec: subscription-payments
pack: api-design
answers:
  base_path: /api/v1
  endpoints:
    - POST /subscriptions/create - Create subscription
    - POST /subscriptions/:id/cancel - Cancel subscription
    - POST /subscriptions/:id/upgrade - Upgrade plan
    - GET /subscriptions/:id - Get subscription status
  versioning_strategy: URL path versioning
  error_format: |
    {
      "error": {
        "code": "PAYMENT_FAILED",
        "message": "Your payment method was declined",
        "stripe_error_code": "card_declined"
      }
    }
```

### Step 7: Answer Data Model Pack

**File:** `data-model.yaml`

```yaml
spec: subscription-payments
pack: data-model
answers:
  tables:
    subscriptions:
      columns:
        - id (UUID, PK)
        - user_id (UUID, FK to users.id)
        - stripe_subscription_id (VARCHAR(255), UNIQUE)
        - plan (ENUM: free, pro, enterprise)
        - status (ENUM: active, canceled, past_due)
        - current_period_end (TIMESTAMP)
        - created_at, updated_at (TIMESTAMP)
      indexes:
        - user_id
        - stripe_subscription_id (UNIQUE)
        - status

    payment_events:
      columns:
        - id (UUID, PK)
        - subscription_id (UUID, FK to subscriptions.id)
        - stripe_event_id (VARCHAR(255), UNIQUE)
        - event_type (VARCHAR(100))
        - payload (JSONB)
        - processed_at (TIMESTAMP)
      indexes:
        - subscription_id
        - stripe_event_id (UNIQUE)
        - event_type

  migrations:
    - 001_create_subscriptions_table.sql
    - 002_create_payment_events_table.sql
```

### Step 8: Answer Billing Pack

**File:** `billing.yaml`

```yaml
spec: subscription-payments
pack: billing
answers:
  payment_gateway: Stripe
  subscription_model: Tiered (Free $0, Pro $29/mo, Enterprise $99/mo)
  billing_cycle: Monthly (with annual option at 20% discount)
  payment_methods: Credit card, ACH, SEPA
  failed_payment_handling: |
    - Stripe retries automatically (Smart Retries)
    - After 3 failures over 2 weeks, cancel subscription
    - Send email notifications on each failure
  invoice_generation: Stripe-hosted invoices
  refund_policy: Pro-rated refunds within 30 days of charge
  tax_calculation: Stripe Tax (automatic)
```

### Step 9: Answer Webhooks Pack

**File:** `webhooks.yaml`

```yaml
spec: subscription-payments
pack: webhooks
answers:
  events:
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.payment_succeeded
    - invoice.payment_failed
  signature_method: Stripe webhook signatures (HMAC-SHA256)
  delivery_guarantee: At-least-once (Stripe handles retries)
  retry_strategy: N/A (Stripe retries for us)
  timeout: 30 seconds per webhook processing
  failure_handling: |
    - Return 200 OK immediately if event already processed (idempotency)
    - Return 500 on errors to trigger Stripe retry
    - After 3 days of failures, Stripe stops retrying (we monitor logs)
  payload_format: Stripe webhook event JSON
```

### Step 10: Summarize in requirements.md

**File:** `.ldf/specs/subscription-payments/requirements.md`

```markdown
# subscription-payments - Requirements

## Overview

Subscription payment system integrated with Stripe for Free, Pro, and Enterprise tiers.

## User Stories

### US-1: Create Subscription
**As a** user
**I want to** subscribe to a paid plan
**So that** I can access premium features

**Acceptance Criteria:**
- [ ] AC-1.1: User can select Pro ($29/mo) or Enterprise ($99/mo)
- [ ] AC-1.2: Payment processed via Stripe
- [ ] AC-1.3: Subscription activated immediately on success
- [ ] AC-1.4: User receives email confirmation with invoice

### US-2: Cancel Subscription
...

## Question-Pack Answers

### Security (.ldf/answerpacks/subscription-payments/security.yaml)

- **Payment data:** PCI-compliant (Stripe handles card data)
- **Secrets:** Stripe API keys in environment variables
- **Fraud detection:** Stripe Radar + block >$10k without verification

### Testing (.ldf/answerpacks/subscription-payments/testing.yaml)

- **Coverage:** 95% (payments are critical)
- **Test types:** Integration (Stripe test mode), unit (price calc), E2E (checkout UI), security

### API Design (.ldf/answerpacks/subscription-payments/api-design.yaml)

- **Endpoints:** POST /subscriptions/create, POST /:id/cancel, POST /:id/upgrade, GET /:id
- **Error format:** Structured JSON with Stripe error codes

### Data Model (.ldf/answerpacks/subscription-payments/data-model.yaml)

- **Tables:** subscriptions, payment_events
- **Key columns:** stripe_subscription_id (UNIQUE), status, event_type
- **Migrations:** 001_subscriptions, 002_payment_events

### Billing (.ldf/answerpacks/subscription-payments/billing.yaml)

- **Gateway:** Stripe
- **Plans:** Free $0, Pro $29/mo, Enterprise $99/mo
- **Refunds:** Pro-rated within 30 days
- **Failed payments:** Auto-retry, cancel after 3 failures

### Webhooks (.ldf/answerpacks/subscription-payments/webhooks.yaml)

- **Events:** subscription.created, invoice.payment_succeeded, etc.
- **Signature:** Stripe webhook signatures (HMAC-SHA256)
- **Idempotency:** Track processed event IDs

## Guardrail Coverage Matrix
...
```

---

## Troubleshooting

### Q: Do I have to answer every question in a pack?

**A:** For `required: true` questions, yes. For optional questions, only if relevant.

### Q: Can I add custom questions to a built-in pack?

**A:** Not directly. Instead:
1. Copy the built-in pack to `.ldf/question-packs/custom/`
2. Modify the copy
3. Update `.ldf/config.yaml` to use your custom version

### Q: What if a question doesn't apply to my feature?

**A:** In the answerpack, write:
```yaml
answers:
  question_id: N/A - Reason why it doesn't apply
```

Example:
```yaml
answers:
  session_duration: N/A - Using API keys (no sessions)
```

### Q: How do I share answerpacks across multiple specs?

**A:** You can reference another spec's answerpack:

**In requirements.md:**
```markdown
### Security

See `.ldf/answerpacks/core-auth/security.yaml` - all specs use the same auth strategy.

**Specific to this spec:**
- Additional rate limiting: 100 requests per minute per user
```

---

## Next Steps

Now that you understand question-packs:

1. **Practice:** Create answerpacks for the login feature from Tutorial 2
2. **Review:** Check if your first spec (Tutorial 1) would benefit from answerpack YAML files
3. **Continue learning:**
   - [Tutorial 4: Multi-Agent Review](04-multi-agent-review.md) - Get AI feedback on your answerpacks
   - [Answerpack Guide](../answerpacks.md) - Advanced answerpack techniques

---

## Quick Reference: Core Packs

| Pack | Key Questions |
|------|---------------|
| **security** | Auth method? Password storage? Rate limiting? Secrets management? |
| **testing** | Coverage target? Test types? Framework? Mocking strategy? |
| **api-design** | Base path? Endpoints? Versioning? Error format? |
| **data-model** | Tables? Columns? Indexes? Migrations? Relationships? |

## Quick Reference: Optional Packs

| Pack | When to Use |
|------|-------------|
| **billing** | Payment processing, subscriptions, invoices, refunds |
| **multi-tenancy** | SaaS, tenant isolation, RLS |
| **provisioning** | Async jobs, queues, external services |
| **webhooks** | Event delivery, signatures, retry logic |

---

**Next Tutorial**: [Multi-Agent Review Workflow](04-multi-agent-review.md)
