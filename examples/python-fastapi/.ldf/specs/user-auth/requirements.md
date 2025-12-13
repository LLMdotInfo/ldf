# user-auth - Requirements

## Overview

User authentication system for the FastAPI application using email/password with optional MFA support. Provides secure session management with JWT tokens.

## User Stories

### US-1: User Registration

**As a** new user
**I want to** create an account with my email and password
**So that** I can access the application

**Acceptance Criteria:**
- [ ] AC-1.1: User can submit email and password
- [ ] AC-1.2: Email must be unique and valid format
- [ ] AC-1.3: Password must be 12+ characters with complexity
- [ ] AC-1.4: Successful registration returns user info (no password)
- [ ] AC-1.5: Duplicate email returns 409 Conflict

### US-2: User Login

**As a** registered user
**I want to** log in with my email and password
**So that** I can access my account

**Acceptance Criteria:**
- [ ] AC-2.1: User can submit email and password
- [ ] AC-2.2: Valid credentials return JWT tokens (access + refresh)
- [ ] AC-2.3: Invalid credentials return 401 (same message for all failures)
- [ ] AC-2.4: Account locks after 5 failed attempts for 15 minutes
- [ ] AC-2.5: Tokens are HttpOnly cookies (not in response body)

### US-3: User Logout

**As a** logged-in user
**I want to** log out
**So that** my session is invalidated

**Acceptance Criteria:**
- [ ] AC-3.1: Logout invalidates current session
- [ ] AC-3.2: Refresh token is revoked
- [ ] AC-3.3: Cookies are cleared

### US-4: Token Refresh

**As a** logged-in user
**I want to** refresh my access token
**So that** I stay logged in without re-entering credentials

**Acceptance Criteria:**
- [ ] AC-4.1: Valid refresh token returns new access token
- [ ] AC-4.2: Expired refresh token returns 401
- [ ] AC-4.3: Revoked refresh token returns 401

### US-5: MFA Enrollment (Optional)

**As a** security-conscious user
**I want to** enable two-factor authentication
**So that** my account has additional protection

**Acceptance Criteria:**
- [ ] AC-5.1: User can generate TOTP secret
- [ ] AC-5.2: QR code is provided for authenticator apps
- [ ] AC-5.3: User must verify code to complete enrollment
- [ ] AC-5.4: MFA can be disabled with password confirmation

## Question-Pack Answers

### Security

**Authentication Method:**
- Method: Email/password with bcrypt (cost factor 12)
- Rationale: Industry standard, configurable work factor

**Session Management:**
- Access token: JWT, 15 minutes, HttpOnly cookie
- Refresh token: Opaque UUID, 7 days, HttpOnly cookie, stored in DB
- Rationale: Short-lived access limits exposure, refresh enables UX

**Password Policy:**
- Minimum 12 characters
- At least one uppercase, lowercase, number, special character
- Checked against common password list (top 10k)
- Rationale: NIST guidelines, balance security with usability

**Account Lockout:**
- Lock after 5 failed attempts
- Lock duration: 15 minutes
- Reset on successful login
- Rationale: Prevent brute force without permanent lockout

**MFA:**
- Type: TOTP (RFC 6238)
- Optional for users, step-up for sensitive operations
- Recovery: 10 backup codes generated on enrollment

### Testing

**Coverage Requirements:**
- Auth service: 90% minimum
- Endpoints: 85% minimum
- Overall: 80% minimum

**Test Types:**
- Unit tests for AuthService methods
- Integration tests for API endpoints
- Security tests for enumeration, injection

### API Design

**Base Path:** `/api/v1/auth`

**Endpoints:**
- POST `/register` - Create account
- POST `/login` - Authenticate
- POST `/logout` - End session
- POST `/refresh` - Refresh tokens
- POST `/mfa/enroll` - Start MFA setup
- POST `/mfa/verify` - Complete MFA setup
- DELETE `/mfa` - Disable MFA

**Error Format:**
```json
{
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

### Data Model

**Tables:**
- `users`: id, email, password_hash, mfa_secret, created_at, updated_at
- `refresh_tokens`: id, user_id, token_hash, expires_at, revoked_at
- `login_attempts`: id, email, success, ip_address, created_at

**Indexes:**
- users(email) UNIQUE
- refresh_tokens(token_hash)
- login_attempts(email, created_at)

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [US-1..5] | [S4.1] | [T-4.1, T-4.2, T-4.3] | Dev | TODO |
| 2. Security Basics | [US-2, US-5] | [S2.1, S2.3] | [T-2.3, T-3.4] | Dev | TODO |
| 3. Error Handling | [US-1..5] | [S3.2] | [T-2.4, T-3.5] | Dev | TODO |
| 4. Logging & Observability | [US-2] | [S3.3] | [T-3.6] | Dev | TODO |
| 5. API Design | [US-1..5] | [S3.1] | [T-1.1] | Dev | TODO |
| 6. Data Validation | [US-1, US-2] | [S2.2] | [T-2.1, T-2.2] | Dev | TODO |
| 7. Database Migrations | [All] | [S1.2] | [T-1.2] | Dev | TODO |
| 8. Documentation | [All] | [S4.2] | [T-5.1] | Dev | TODO |

## Dependencies

- FastAPI 0.104+
- SQLAlchemy 2.0+
- python-jose (JWT)
- bcrypt
- pyotp (TOTP)
- pydantic v2

## Out of Scope

- Social login (OAuth providers)
- Password reset flow (separate spec)
- Email verification (separate spec)
- Admin user management
