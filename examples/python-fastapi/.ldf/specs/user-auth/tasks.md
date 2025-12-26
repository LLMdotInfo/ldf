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

- [ ] **Task 1.1:** Create project structure
  - [ ] Create `src/auth/` directory
  - [ ] Create `src/auth/router.py`
  - [ ] Create `src/auth/service.py`
  - [ ] Create `src/auth/schemas.py`
  - [ ] Create `src/auth/repository.py`
  - [ ] Create `tests/auth/` directory

- [ ] **Task 1.2:** Create database migrations
  - [ ] Create `001_create_users_table.py` migration
  - [ ] Create `002_create_refresh_tokens_table.py` migration
  - [ ] Create `003_create_login_attempts_table.py` migration
  - [ ] Test upgrade and downgrade

- [ ] **Task 1.3:** Create SQLAlchemy models
  - [ ] Create `User` model
  - [ ] Create `RefreshToken` model
  - [ ] Create `LoginAttempt` model

## Phase 2: Core Authentication

- [ ] **Task 2.1:** Implement password utilities
  - [ ] Create `hash_password()` function (bcrypt cost factor 12)
  - [ ] Create `verify_password()` function
  - [ ] Write unit tests

- [ ] **Task 2.2:** Implement input validation schemas
  - [ ] Create `RegisterRequest` schema with password validator
  - [ ] Create `LoginRequest` schema
  - [ ] Create `UserResponse` schema (no password)
  - [ ] Write unit tests for validators

- [ ] **Task 2.3:** Implement JWT utilities
  - [ ] Create `create_access_token()` function
  - [ ] Create `verify_access_token()` function
  - [ ] Create `hash_refresh_token()` function
  - [ ] Configure from environment variables
  - [ ] Write unit tests

- [ ] **Task 2.4:** Implement AuthService
  - [ ] Implement `register()` method
  - [ ] Implement `login()` method with lockout check
  - [ ] Implement `logout()` method
  - [ ] Implement `refresh()` method
  - [ ] Implement `_is_locked_out()` helper
  - [ ] Implement `_record_failed_attempt()` helper
  - [ ] Write comprehensive unit tests

## Phase 3: API Endpoints

- [ ] **Task 3.1:** Implement /register endpoint
  - [ ] Create endpoint in router (POST /api/v1/auth/register)
  - [ ] Handle DuplicateEmailError (409)
  - [ ] Return 201 with UserResponse
  - [ ] Write integration tests

- [ ] **Task 3.2:** Implement /login endpoint
  - [ ] Create endpoint in router
  - [ ] Set access_token and refresh_token cookies (HttpOnly)
  - [ ] Handle InvalidCredentialsError (401)
  - [ ] Handle AccountLockedError (423)
  - [ ] Write integration tests

- [ ] **Task 3.3:** Implement /logout endpoint
  - [ ] Create endpoint in router
  - [ ] Require authentication dependency
  - [ ] Clear cookies and revoke tokens
  - [ ] Write integration tests

- [ ] **Task 3.4:** Implement /refresh endpoint
  - [ ] Create endpoint in router
  - [ ] Read and validate refresh_token from cookie
  - [ ] Issue new access token
  - [ ] Write integration tests

- [ ] **Task 3.5:** Implement error handlers
  - [ ] Create custom exception classes
  - [ ] Create exception handlers
  - [ ] Format errors as `{"error": {"code": "", "message": ""}}`
  - [ ] Test error responses

- [ ] **Task 3.6:** Add logging middleware
  - [ ] Create correlation ID middleware
  - [ ] Configure structlog
  - [ ] Add request/response logging
  - [ ] Verify no sensitive data in logs

## Phase 4: Testing

- [ ] **Task 4.1:** Write unit tests
  - [ ] Test AuthService.register() (success, duplicate)
  - [ ] Test AuthService.login() (success, invalid, locked)
  - [ ] Test AuthService.logout()
  - [ ] Test AuthService.refresh() (success, expired, revoked)
  - [ ] Test password utilities
  - [ ] Test JWT utilities

- [ ] **Task 4.2:** Write integration tests
  - [ ] Test registration flow
  - [ ] Test login flow
  - [ ] Test logout flow
  - [ ] Test token refresh flow
  - [ ] Test error responses

- [ ] **Task 4.3:** Write security tests
  - [ ] Test email enumeration (timing, response)
  - [ ] Test account lockout after 5 attempts
  - [ ] Test SQL injection attempts
  - [ ] Test XSS in error messages

## Phase 5: Documentation

- [ ] **Task 5.1:** Update documentation
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
