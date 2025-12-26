# User Auth Service - Development Guide

## Project Overview

**Name:** User Auth Service
**Purpose:** Secure user authentication and authorization for FastAPI applications
**Stack:** Python 3.11+, FastAPI, PostgreSQL, SQLAlchemy

## Development Methodology: LDF (Spec-Driven)

This project uses LDF - a spec-driven development approach with three phases:

### Phase 1: Requirements
- **Location:** `.ldf/specs/{feature}/requirements.md`
- **Format:** User stories with acceptance criteria

### Phase 2: Design
- **Location:** `.ldf/specs/{feature}/design.md`
- **Format:** Architecture, components, data models, APIs

### Phase 3: Tasks
- **Location:** `.ldf/specs/{feature}/tasks.md`
- **Format:** Numbered implementation checklist with guardrail checklists

**CRITICAL RULE:** Do NOT write code until all three phases are approved.

## Commands

### `/project:create-spec {feature-name}`
Creates new feature specification through the three phases.

### `/project:implement-task {spec-name} {task-number}`
Implements a specific task from an approved spec.

### `/project:review-spec {spec-name}`
Reviews spec for completeness and quality.

## Architecture Standards

### Project Structure

```
.
├── src/
│   ├── main.py               # FastAPI app entry point
│   ├── api/
│   │   ├── routes/           # API route handlers
│   │   └── deps.py           # Dependency injection
│   ├── core/
│   │   ├── config.py         # Settings management
│   │   └── security.py       # JWT, password hashing
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   └── services/             # Business logic
├── migrations/               # Alembic migrations
└── tests/                    # Test suite
```

### Service Layer Pattern

```python
# src/services/auth.py
class AuthService:
    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
```

### Error Handling

```python
# Use HTTPException for API errors
from fastapi import HTTPException, status

class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
```

### API Design

```python
# src/api/routes/auth.py
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    user = await auth_service.authenticate(form_data.username, form_data.password)
    if not user:
        raise AuthenticationError()
    return auth_service.create_tokens(user)
```

## Testing Standards

### Coverage Requirements
- Minimum: 80% overall
- Auth logic: 90%
- API routes: 85%

### Test Structure

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "testpass123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "bad@email.com", "password": "wrongpass"}
    )
    assert response.status_code == 401
```

## Commit Message Format

```
type(scope): brief description

- Detailed change 1
- Detailed change 2

Related spec: .ldf/specs/{feature}/tasks.md [Task X.Y]
```

## Technology Stack

- **Python 3.11+** - Language
- **FastAPI** - Web framework
- **SQLAlchemy 2.0** - ORM
- **Pydantic 2.0** - Data validation
- **Alembic** - Migrations
- **pytest** - Testing
- **bcrypt** - Password hashing
- **python-jose** - JWT handling

## When to Ask Clarification

**ALWAYS ask before:**
- Writing code without approved spec
- Making architectural decisions not in design.md
- Changing API contracts
- Modifying database schema

**Can proceed without asking:**
- Following patterns in existing code
- Implementing approved tasks
- Writing tests for new code
