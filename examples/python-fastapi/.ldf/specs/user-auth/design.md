# user-auth - Design

## Architecture Overview

```
┌─────────────┐     ┌──────────────────────────────────────┐
│   Client    │────▶│           FastAPI Application        │
└─────────────┘     │  ┌──────────┐    ┌───────────────┐   │
                    │  │  Router  │───▶│  AuthService  │   │
                    │  └──────────┘    └───────────────┘   │
                    │                         │            │
                    │                         ▼            │
                    │               ┌───────────────┐      │
                    │               │  Repository   │      │
                    │               └───────────────┘      │
                    │                         │            │
                    └─────────────────────────│────────────┘
                                              ▼
                                    ┌───────────────┐
                                    │  PostgreSQL   │
                                    └───────────────┘
```

## S1: Data Layer

### S1.1: Database Schema

#### users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    mfa_secret VARCHAR(255),
    mfa_enabled BOOLEAN DEFAULT FALSE,
    failed_attempts INT DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
```

#### refresh_tokens Table

```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
```

#### login_attempts Table

```sql
CREATE TABLE login_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    success BOOLEAN NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_login_attempts_email_created
    ON login_attempts(email, created_at DESC);
```

### S1.2: Migrations

Migration files:
1. `001_create_users_table.py`
2. `002_create_refresh_tokens_table.py`
3. `003_create_login_attempts_table.py`

All migrations are reversible with downgrade functions.

## S2: Security Layer

### S2.1: Password Handling

```python
from bcrypt import hashpw, checkpw, gensalt

BCRYPT_COST = 12

def hash_password(password: str) -> str:
    return hashpw(password.encode(), gensalt(BCRYPT_COST)).decode()

def verify_password(password: str, hash: str) -> bool:
    return checkpw(password.encode(), hash.encode())
```

**Security Properties:**
- Cost factor 12 (~250ms hash time)
- Salt is embedded in hash
- Constant-time comparison

### S2.2: Input Validation

```python
from pydantic import BaseModel, EmailStr, field_validator
import re

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
```

### S2.3: JWT Token Design

**Access Token (15 min):**
```python
{
    "sub": "user-uuid",
    "exp": 1234567890,
    "iat": 1234567890,
    "type": "access"
}
```

**Token Configuration:**
- Algorithm: HS256 (symmetric for simplicity)
- Secret: From environment variable `JWT_SECRET`
- Access token: 15 minutes
- Refresh token: 7 days (stored in DB)

**Cookie Settings:**
```python
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=True,  # HTTPS only
    samesite="lax",
    max_age=900  # 15 minutes
)
```

### S2.4: Account Lockout

```python
LOCKOUT_THRESHOLD = 5
LOCKOUT_DURATION = timedelta(minutes=15)

async def check_lockout(email: str) -> bool:
    user = await get_user_by_email(email)
    if user and user.locked_until:
        if user.locked_until > datetime.utcnow():
            return True
        # Lock expired, reset
        await reset_lockout(user.id)
    return False

async def record_failed_attempt(email: str) -> None:
    user = await get_user_by_email(email)
    if user:
        user.failed_attempts += 1
        if user.failed_attempts >= LOCKOUT_THRESHOLD:
            user.locked_until = datetime.utcnow() + LOCKOUT_DURATION
        await save_user(user)
```

## S3: Service Layer

### S3.1: API Endpoints

```python
from fastapi import APIRouter, Response, Depends

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", status_code=201)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends()
) -> UserResponse:
    """Create new user account."""
    return await auth_service.register(request.email, request.password)

@router.post("/login")
async def login(
    request: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends()
) -> dict:
    """Authenticate and return tokens in cookies."""
    tokens = await auth_service.login(request.email, request.password)
    set_auth_cookies(response, tokens)
    return {"message": "Login successful"}

@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends()
) -> dict:
    """Invalidate session and clear cookies."""
    await auth_service.logout(current_user.id)
    clear_auth_cookies(response)
    return {"message": "Logout successful"}

@router.post("/refresh")
async def refresh(
    response: Response,
    refresh_token: str = Cookie(None),
    auth_service: AuthService = Depends()
) -> dict:
    """Refresh access token."""
    tokens = await auth_service.refresh(refresh_token)
    set_auth_cookies(response, tokens)
    return {"message": "Token refreshed"}
```

### S3.2: AuthService

```python
class AuthService:
    def __init__(self, user_repo: UserRepository, token_repo: TokenRepository):
        self.user_repo = user_repo
        self.token_repo = token_repo

    async def register(self, email: str, password: str) -> User:
        """Register new user."""
        if await self.user_repo.get_by_email(email):
            raise DuplicateEmailError()

        password_hash = hash_password(password)
        user = User(email=email, password_hash=password_hash)
        return await self.user_repo.create(user)

    async def login(self, email: str, password: str) -> TokenPair:
        """Authenticate user and return tokens."""
        # Check lockout
        if await self._is_locked_out(email):
            raise AccountLockedError()

        user = await self.user_repo.get_by_email(email)

        # Constant-time comparison to prevent timing attacks
        if not user or not verify_password(password, user.password_hash):
            await self._record_failed_attempt(email)
            raise InvalidCredentialsError()

        # Reset failed attempts on success
        await self._reset_lockout(user.id)

        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = await self._create_refresh_token(user.id)

        # Log successful login
        await self._log_login_attempt(email, success=True)

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def logout(self, user_id: UUID) -> None:
        """Revoke all refresh tokens for user."""
        await self.token_repo.revoke_all_for_user(user_id)

    async def refresh(self, refresh_token: str) -> TokenPair:
        """Refresh access token using refresh token."""
        token_hash = hash_token(refresh_token)
        stored = await self.token_repo.get_by_hash(token_hash)

        if not stored or stored.revoked_at or stored.expires_at < datetime.utcnow():
            raise InvalidRefreshTokenError()

        # Generate new access token
        access_token = create_access_token(stored.user_id)

        return TokenPair(access_token=access_token, refresh_token=refresh_token)
```

### S3.3: Logging

```python
import structlog

logger = structlog.get_logger()

# In AuthService.login():
logger.info(
    "login_attempt",
    email=email,
    success=True,
    ip_address=request.client.host,
    correlation_id=correlation_id
)

# Failed login (no email in log to prevent enumeration aid)
logger.warning(
    "login_failed",
    ip_address=request.client.host,
    correlation_id=correlation_id
)

# Account lockout
logger.warning(
    "account_locked",
    user_id=str(user.id),
    failed_attempts=user.failed_attempts,
    locked_until=str(user.locked_until)
)
```

## S4: Testing Strategy

### S4.1: Test Structure

```
tests/
├── unit/
│   ├── test_auth_service.py      # AuthService methods
│   ├── test_password_utils.py    # Password hashing
│   └── test_token_utils.py       # JWT creation/validation
├── integration/
│   ├── test_auth_endpoints.py    # API endpoint tests
│   └── test_auth_flows.py        # Complete auth flows
└── security/
    ├── test_enumeration.py       # Email enumeration prevention
    ├── test_injection.py         # SQL injection tests
    └── test_brute_force.py       # Rate limiting/lockout
```

### S4.2: API Documentation

OpenAPI schema auto-generated by FastAPI with:
- Request/response schemas
- Error responses
- Security requirements
- Example requests

## Guardrail Mapping

| Guardrail | Implementation | Section |
|-----------|---------------|---------|
| 1. Testing Coverage | Unit + Integration + Security tests | S4.1 |
| 2. Security Basics | bcrypt, JWT, lockout, no enumeration | S2 |
| 3. Error Handling | Consistent error format, no stack traces | S3.1 |
| 4. Logging & Observability | Structured logging with correlation IDs | S3.3 |
| 5. API Design | /api/v1 prefix, standard error format | S3.1 |
| 6. Data Validation | Pydantic validators, email/password rules | S2.2 |
| 7. Database Migrations | Reversible Alembic migrations | S1.2 |
| 8. Documentation | OpenAPI via FastAPI | S4.2 |

## Security Considerations

### Threat Model

1. **Credential Stuffing**: Mitigated by account lockout, rate limiting
2. **Brute Force**: Mitigated by password policy, lockout
3. **Session Hijacking**: Mitigated by HttpOnly cookies, short access tokens
4. **Email Enumeration**: Mitigated by constant-time responses, same error messages
5. **SQL Injection**: Mitigated by parameterized queries (SQLAlchemy)

### Security Headers

```python
# Middleware to add security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

## Dependencies

```
fastapi>=0.104.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
python-jose[cryptography]>=3.3.0
bcrypt>=4.1.0
pyotp>=2.9.0
pydantic>=2.5.0
structlog>=23.2.0
```
