# blog-api - Design

## Architecture Overview

```
┌─────────────┐     ┌──────────────────────────────────────┐
│   Client    │────▶│        Flask Application             │
└─────────────┘     │  ┌──────────┐    ┌──────────────┐    │
                    │  │Blueprint │───▶│   Service    │    │
                    │  │ (Routes) │    │   Layer      │    │
                    │  └──────────┘    └──────────────┘    │
                    │                         │             │
                    │                         ▼             │
                    │               ┌───────────────┐       │
                    │               │  Repository   │       │
                    │               │  (SQLAlchemy) │       │
                    │               └───────────────┘       │
                    │                         │             │
                    └─────────────────────────│─────────────┘
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
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_username ON users(username);
```

#### posts Table

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    slug VARCHAR(250) NOT NULL UNIQUE,
    author_id INTEGER NOT NULL REFERENCES users(id),
    status VARCHAR(20) NOT NULL DEFAULT 'draft', -- draft, published, deleted
    published_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_posts_author_id ON posts(author_id);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_published_at ON posts(published_at DESC);
CREATE UNIQUE INDEX idx_posts_slug ON posts(slug);
```

#### tags Table

```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_tags_name ON tags(name);
```

#### post_tags Table (Many-to-Many)

```sql
CREATE TABLE post_tags (
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);

CREATE INDEX idx_post_tags_post_id ON post_tags(post_id);
CREATE INDEX idx_post_tags_tag_id ON post_tags(tag_id);
```

#### comments Table

```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_author_id ON comments(author_id);
CREATE INDEX idx_comments_created_at ON comments(created_at DESC);
```

### S1.2: SQLAlchemy Models

**Location:** `src/models/`

#### User Model

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    posts = relationship('Post', back_populates='author', lazy='dynamic')
    comments = relationship('Comment', back_populates='author', lazy='dynamic')
```

#### Post Model

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    slug = Column(String(250), unique=True, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(20), default='draft', nullable=False)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = relationship('User', back_populates='posts')
    tags = relationship('Tag', secondary='post_tags', back_populates='posts')
    comments = relationship('Comment', back_populates='post', lazy='dynamic')
```

## S2: Service Layer

### S2.1: Post Service

**Location:** `src/services/post_service.py`

**Responsibilities:**
- Business logic for post operations
- Authorization checks
- Slug generation
- Status transitions

**Key Methods:**
```python
class PostService:
    def create_post(user_id, title, content, tags) -> Post
    def publish_post(user_id, post_id) -> Post
    def update_post(user_id, post_id, **updates) -> Post
    def delete_post(user_id, post_id) -> None
    def get_post(post_id, user_id=None) -> Post
    def list_posts(page, per_page, tag=None) -> dict
```

**Authorization Logic:**
```python
def _check_author(self, post: Post, user_id: int):
    if post.author_id != user_id:
        raise ForbiddenError("Only the author can modify this post")
```

### S2.2: Comment Service

**Location:** `src/services/comment_service.py`

**Responsibilities:**
- Comment creation
- Validation against published posts
- List comments for a post

**Key Methods:**
```python
class CommentService:
    def create_comment(user_id, post_id, content) -> Comment
    def list_comments(post_id, page, per_page) -> dict
    def delete_comment(user_id, comment_id) -> None
```

## S3: API Layer

### S3.1: Posts Blueprint

**Location:** `src/api/v1/posts.py`

**Endpoints:**

| Method | Path | Handler | Auth Required |
|--------|------|---------|---------------|
| POST | `/api/v1/posts` | create_post | Yes |
| GET | `/api/v1/posts` | list_posts | No |
| GET | `/api/v1/posts/{id}` | get_post | No* |
| PUT | `/api/v1/posts/{id}` | update_post | Yes |
| DELETE | `/api/v1/posts/{id}` | delete_post | Yes |
| POST | `/api/v1/posts/{id}/publish` | publish_post | Yes |

*Auth optional - drafts visible only to author

**Request/Response Schemas:**

```python
# Create Post Request
{
    "title": "string (1-200 chars)",
    "content": "string (1-50000 chars)",
    "tags": ["string", "string"]  # optional
}

# Post Response
{
    "id": 1,
    "title": "string",
    "content": "string",
    "slug": "string",
    "author": {
        "id": 1,
        "username": "string"
    },
    "tags": ["string"],
    "status": "draft|published",
    "published_at": "ISO8601 timestamp or null",
    "created_at": "ISO8601 timestamp",
    "updated_at": "ISO8601 timestamp"
}

# List Posts Response
{
    "posts": [Post, Post, ...],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 100,
        "has_next": true,
        "has_prev": false
    }
}
```

### S3.2: Comments Blueprint

**Location:** `src/api/v1/comments.py`

**Endpoints:**

| Method | Path | Handler | Auth Required |
|--------|------|---------|---------------|
| POST | `/api/v1/posts/{post_id}/comments` | create_comment | Yes |
| GET | `/api/v1/posts/{post_id}/comments` | list_comments | No |
| DELETE | `/api/v1/comments/{id}` | delete_comment | Yes |

## S4: Request/Response Flow

### S4.1: Create Post Flow

```
1. Client → POST /api/v1/posts
   Headers: Authorization: Bearer <token>
   Body: {title, content, tags}

2. Blueprint validates JWT token → extracts user_id

3. Marshmallow schema validates request data

4. PostService.create_post(user_id, title, content, tags)
   - Generate slug from title
   - Create Post with status='draft'
   - Associate tags (create if new)
   - Save to database

5. Response: 201 Created
   Body: Post object with author info
```

### S4.2: Publish Post Flow

```
1. Client → POST /api/v1/posts/{id}/publish
   Headers: Authorization: Bearer <token>

2. Blueprint validates JWT token → extracts user_id

3. PostService.publish_post(user_id, post_id)
   - Load post from database
   - Check user_id == post.author_id
   - Check status == 'draft'
   - Set status='published', published_at=now()
   - Save to database

4. Response: 200 OK
   Body: Updated post object
```

## S5: Error Handling

### S5.1: Error Types

**Location:** `src/errors.py`

```python
class APIError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"
    
class ValidationError(APIError):
    status_code = 400
    code = "VALIDATION_ERROR"
    
class NotFoundError(APIError):
    status_code = 404
    code = "NOT_FOUND"
    
class ForbiddenError(APIError):
    status_code = 403
    code = "FORBIDDEN"
```

### S5.2: Error Handler

```python
@app.errorhandler(APIError)
def handle_api_error(error):
    response = {
        "error": {
            "code": error.code,
            "message": str(error),
            "details": getattr(error, 'details', None)
        }
    }
    return jsonify(response), error.status_code
```

## S6: Validation Layer

### S6.1: Marshmallow Schemas

**Location:** `src/schemas/post_schemas.py`

```python
from marshmallow import Schema, fields, validate, validates, ValidationError

class CreatePostSchema(Schema):
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50000)
    )
    tags = fields.List(
        fields.Str(validate=validate.Length(max=50)),
        required=False
    )
    
    @validates('title')
    def validate_title(self, value):
        if not value.strip():
            raise ValidationError("Title cannot be empty")
```

## S7: Security Considerations

### S7.1: Authentication

- JWT tokens via Flask-JWT-Extended
- Token stored in Authorization header
- Access token lifetime: 15 minutes
- Refresh token lifetime: 7 days

### S7.2: Authorization

- Post operations: Author-only (checked in service layer)
- Comment operations: Author-only for delete
- Read operations: Public for published content

### S7.3: Input Sanitization

- HTML tags stripped from post content and comments (Bleach library)
- SQL injection prevented by SQLAlchemy parameterized queries
- XSS prevention via content sanitization

### S7.4: Rate Limiting

**Implementation:** Flask-Limiter

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

@posts_bp.route('/', methods=['POST'])
@limiter.limit("10 per hour")
@jwt_required()
def create_post():
    pass
```

## S8: Testing Strategy

### S8.1: Unit Tests

**Target:** Service layer, validators, helpers
**Framework:** pytest
**Coverage:** 95%

```python
def test_post_service_create_post():
    service = PostService(mock_repo)
    post = service.create_post(
        user_id=1,
        title="Test Post",
        content="Content",
        tags=["test"]
    )
    assert post.slug == "test-post"
    assert post.status == "draft"
```

### S8.2: Integration Tests

**Target:** API endpoints
**Framework:** pytest with Flask test client
**Coverage:** 90%

```python
def test_create_post_endpoint(client, auth_headers):
    response = client.post(
        '/api/v1/posts',
        json={"title": "Test", "content": "Content"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json['status'] == 'draft'
```

## S9: Deployment Considerations

### S9.1: Configuration

```python
# config.py
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL')
```

### S9.2: Database Migrations

**Tool:** Alembic (via Flask-Migrate)

```bash
# Initialize
flask db init

# Create migration
flask db migrate -m "Create posts table"

# Apply migration
flask db upgrade
```

## S10: Observability

### S10.1: Logging

```python
import logging
from flask import request, g

logger = logging.getLogger(__name__)

@app.before_request
def log_request():
    g.request_id = str(uuid.uuid4())
    logger.info(
        "Request started",
        extra={
            "request_id": g.request_id,
            "method": request.method,
            "path": request.path,
            "user_id": get_jwt_identity() if request.headers.get('Authorization') else None
        }
    )
```

### S10.2: Metrics

**Recommendation:** Prometheus + Flask-Prometheus-Metrics

- Request count by endpoint and status
- Request duration histogram
- Active database connections
- Cache hit rate (if caching added)
