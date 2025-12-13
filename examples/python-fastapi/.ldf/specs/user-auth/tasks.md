# user-auth - Tasks

**Status:** Ready for Implementation
**Total Tasks:** 20
**Completed:** 0

## Per-Task Guardrail Checklist

**Reference:** `.ldf/guardrails.yaml`

Before implementing each task, verify applicable guardrails:

- [ ] **1. Testing Coverage:** Unit tests for business logic; integration tests for APIs; coverage ≥80%
- [ ] **2. Security Basics:** Input validation; parameterized queries; auth/authz checks; no secrets in code
- [ ] **3. Error Handling:** Consistent error responses; proper exception hierarchy; user-friendly messages
- [ ] **4. Logging & Observability:** Structured logging; correlation IDs; appropriate log levels
- [ ] **5. API Design:** Versioned endpoints (/v1/); cursor pagination; consistent error format
- [ ] **6. Data Validation:** Request schema validation; business rule validation; output sanitization
- [ ] **7. Database Migrations:** Reversible migrations; rollback tested; backfills separate from schema
- [ ] **8. Documentation:** API docs updated; inline comments for complex logic; README current

**Mark N/A if not applicable to the task.**

---

## Phase 1: Setup

### Task 1.1: Create project structure
**Guardrail Checklist:**
- [ ] Testing: Test directory created
- [ ] API Design: Router structure follows /api/v1 pattern
- [ ] Documentation: README updated

**Subtasks:**
- [ ] Create `src/auth/` directory
- [ ] Create `src/auth/router.py`
- [ ] Create `src/auth/service.py`
- [ ] Create `src/auth/schemas.py`
- [ ] Create `src/auth/repository.py`
- [ ] Create `tests/auth/` directory

### Task 1.2: Create database migrations
**Guardrail Checklist:**
- [ ] Database Migrations: Reversible with downgrade
- [ ] Database Migrations: Separate from backfills

**Subtasks:**
- [ ] Create `001_create_users_table.py` migration
- [ ] Create `002_create_refresh_tokens_table.py` migration
- [ ] Create `003_create_login_attempts_table.py` migration
- [ ] Test upgrade and downgrade

### Task 1.3: Create SQLAlchemy models
**Guardrail Checklist:**
- [ ] Data Validation: Proper column constraints

**Subtasks:**
- [ ] Create `User` model
- [ ] Create `RefreshToken` model
- [ ] Create `LoginAttempt` model

## Phase 2: Core Authentication

### Task 2.1: Implement password utilities
**Guardrail Checklist:**
- [ ] Security: bcrypt with cost factor 12
- [ ] Testing: Unit tests for hash/verify

**Subtasks:**
- [ ] Create `hash_password()` function
- [ ] Create `verify_password()` function
- [ ] Write unit tests

### Task 2.2: Implement input validation schemas
**Guardrail Checklist:**
- [ ] Data Validation: Password complexity rules
- [ ] Data Validation: Email format validation
- [ ] Testing: Unit tests for validators

**Subtasks:**
- [ ] Create `RegisterRequest` schema with password validator
- [ ] Create `LoginRequest` schema
- [ ] Create `UserResponse` schema (no password)
- [ ] Write unit tests for validators

### Task 2.3: Implement JWT utilities
**Guardrail Checklist:**
- [ ] Security: Secure token generation
- [ ] Testing: Unit tests for token creation/validation

**Subtasks:**
- [ ] Create `create_access_token()` function
- [ ] Create `verify_access_token()` function
- [ ] Create `hash_refresh_token()` function
- [ ] Configure from environment variables
- [ ] Write unit tests

### Task 2.4: Implement AuthService
**Guardrail Checklist:**
- [ ] Security: No email enumeration
- [ ] Security: Account lockout logic
- [ ] Error Handling: Consistent error types
- [ ] Testing: Unit tests with mocked repos

**Subtasks:**
- [ ] Implement `register()` method
- [ ] Implement `login()` method with lockout check
- [ ] Implement `logout()` method
- [ ] Implement `refresh()` method
- [ ] Implement `_is_locked_out()` helper
- [ ] Implement `_record_failed_attempt()` helper
- [ ] Write comprehensive unit tests

## Phase 3: API Endpoints

### Task 3.1: Implement /register endpoint
**Guardrail Checklist:**
- [ ] API Design: POST /api/v1/auth/register
- [ ] Error Handling: 409 for duplicate email
- [ ] Testing: Integration tests

**Subtasks:**
- [ ] Create endpoint in router
- [ ] Handle DuplicateEmailError
- [ ] Return 201 with UserResponse
- [ ] Write integration tests

### Task 3.2: Implement /login endpoint
**Guardrail Checklist:**
- [ ] Security: Set HttpOnly cookies
- [ ] Error Handling: 401 for invalid credentials
- [ ] Error Handling: 423 for locked account
- [ ] Logging: Log login attempts
- [ ] Testing: Integration tests

**Subtasks:**
- [ ] Create endpoint in router
- [ ] Set access_token cookie
- [ ] Set refresh_token cookie
- [ ] Handle InvalidCredentialsError
- [ ] Handle AccountLockedError
- [ ] Write integration tests

### Task 3.3: Implement /logout endpoint
**Guardrail Checklist:**
- [ ] Security: Revoke refresh tokens
- [ ] API Design: Requires authentication
- [ ] Testing: Integration tests

**Subtasks:**
- [ ] Create endpoint in router
- [ ] Require authentication dependency
- [ ] Clear cookies
- [ ] Revoke tokens in database
- [ ] Write integration tests

### Task 3.4: Implement /refresh endpoint
**Guardrail Checklist:**
- [ ] Security: Validate refresh token
- [ ] Error Handling: 401 for invalid/expired token
- [ ] Testing: Integration tests

**Subtasks:**
- [ ] Create endpoint in router
- [ ] Read refresh_token from cookie
- [ ] Validate token against database
- [ ] Issue new access token
- [ ] Write integration tests

### Task 3.5: Implement error handlers
**Guardrail Checklist:**
- [ ] Error Handling: Consistent error format
- [ ] Security: No stack traces in production

**Subtasks:**
- [ ] Create custom exception classes
- [ ] Create exception handlers
- [ ] Format errors as `{"error": {"code": "", "message": ""}}`
- [ ] Test error responses

### Task 3.6: Add logging middleware
**Guardrail Checklist:**
- [ ] Logging: Structured logging
- [ ] Logging: Correlation IDs
- [ ] Security: No sensitive data in logs

**Subtasks:**
- [ ] Create correlation ID middleware
- [ ] Configure structlog
- [ ] Add request/response logging
- [ ] Verify no passwords/tokens in logs

## Phase 4: Testing

### Task 4.1: Write unit tests
**Guardrail Checklist:**
- [ ] Testing: 90% coverage for auth service

**Subtasks:**
- [ ] Test AuthService.register() (success, duplicate)
- [ ] Test AuthService.login() (success, invalid, locked)
- [ ] Test AuthService.logout()
- [ ] Test AuthService.refresh() (success, expired, revoked)
- [ ] Test password utilities
- [ ] Test JWT utilities

### Task 4.2: Write integration tests
**Guardrail Checklist:**
- [ ] Testing: Full API flow tests

**Subtasks:**
- [ ] Test registration flow
- [ ] Test login flow
- [ ] Test logout flow
- [ ] Test token refresh flow
- [ ] Test error responses

### Task 4.3: Write security tests
**Guardrail Checklist:**
- [ ] Security: Verify no enumeration
- [ ] Security: Verify lockout works
- [ ] Security: Verify no injection

**Subtasks:**
- [ ] Test email enumeration (timing, response)
- [ ] Test account lockout after 5 attempts
- [ ] Test SQL injection attempts
- [ ] Test XSS in error messages

## Phase 5: Documentation

### Task 5.1: Update documentation
**Guardrail Checklist:**
- [ ] Documentation: API docs complete
- [ ] Documentation: README updated

**Subtasks:**
- [ ] Verify OpenAPI schema is complete
- [ ] Add example requests to docstrings
- [ ] Update project README
- [ ] Document environment variables

## Completion Checklist

- [ ] All 20 tasks completed
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All security tests passing
- [ ] Test coverage >= 90% for auth module
- [ ] No linting errors
- [ ] Documentation complete
- [ ] Code reviewed
