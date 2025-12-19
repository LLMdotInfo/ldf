# Blog API - Development Guide

## Project Overview

**Name:** Blog API Service
**Purpose:** RESTful API for blog post management with authentication
**Stack:** Python 3.10+ with Flask, PostgreSQL, SQLAlchemy

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
│   ├── __init__.py
│   ├── app.py                # Flask app factory
│   ├── config.py             # Configuration
│   ├── models/               # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── tag.py
│   │   └── comment.py
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   ├── post_service.py
│   │   └── comment_service.py
│   ├── schemas/              # Marshmallow schemas
│   │   ├── __init__.py
│   │   ├── post_schemas.py
│   │   └── comment_schemas.py
│   ├── api/                  # API blueprints
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── posts.py
│   │       └── comments.py
│   ├── utils/                # Helper functions
│   │   ├── __init__.py
│   │   └── auth.py
│   └── errors.py             # Custom exceptions
├── tests/
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── migrations/               # Alembic migrations
└── requirements.txt          # Python dependencies
```

### App Factory Pattern

```python
# src/app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter

db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    
    # Register blueprints
    from src.api.v1 import posts, comments
    app.register_blueprint(posts.bp)
    app.register_blueprint(comments.bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app
```

### Service Layer Pattern

```python
# src/services/post_service.py
from src.models.post import Post
from src.errors import NotFoundError, ForbiddenError

class PostService:
    def __init__(self, db_session):
        self.db = db_session
    
    def create_post(self, user_id, title, content, tags=None):
        """Create a new blog post"""
        slug = self._generate_slug(title)
        post = Post(
            title=title,
            content=content,
            slug=slug,
            author_id=user_id,
            status='draft'
        )
        
        if tags:
            post.tags = self._get_or_create_tags(tags)
        
        self.db.add(post)
        self.db.commit()
        return post
    
    def publish_post(self, user_id, post_id):
        """Publish a draft post"""
        post = self._get_post_or_404(post_id)
        self._check_author(post, user_id)
        
        if post.status != 'draft':
            raise ValidationError("Only draft posts can be published")
        
        post.status = 'published'
        post.published_at = datetime.utcnow()
        self.db.commit()
        return post
    
    def _check_author(self, post, user_id):
        """Verify user is the post author"""
        if post.author_id != user_id:
            raise ForbiddenError("Only the author can modify this post")
```

### Blueprint Pattern

```python
# src/api/v1/posts.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.post_service import PostService
from src.schemas.post_schemas import CreatePostSchema, PostResponseSchema

bp = Blueprint('posts', __name__, url_prefix='/api/v1/posts')

@bp.route('/', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def create_post():
    """Create a new blog post"""
    schema = CreatePostSchema()
    data = schema.load(request.json)
    
    user_id = get_jwt_identity()
    service = PostService(db.session)
    post = service.create_post(user_id, **data)
    
    response_schema = PostResponseSchema()
    return response_schema.dump(post), 201

@bp.route('/', methods=['GET'])
def list_posts():
    """List published posts"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    tag = request.args.get('tag', None)
    
    service = PostService(db.session)
    result = service.list_posts(page, per_page, tag)
    
    return jsonify(result), 200
```

### Error Handling

```python
# src/errors.py
class APIError(Exception):
    """Base API error"""
    status_code = 500
    code = "INTERNAL_ERROR"
    
    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details

class ValidationError(APIError):
    status_code = 400
    code = "VALIDATION_ERROR"

class NotFoundError(APIError):
    status_code = 404
    code = "NOT_FOUND"

class ForbiddenError(APIError):
    status_code = 403
    code = "FORBIDDEN"

# Error handler registration
@app.errorhandler(APIError)
def handle_api_error(error):
    response = {
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details
        }
    }
    return jsonify(response), error.status_code
```

### Marshmallow Schemas

```python
# src/schemas/post_schemas.py
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

class PostResponseSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    content = fields.Str()
    slug = fields.Str()
    status = fields.Str()
    published_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    author = fields.Nested('UserSchema', only=['id', 'username'])
    tags = fields.List(fields.Str())
```

## Testing Standards

### Coverage Requirements
- Overall: 85%
- API routes: 90%
- Service layer: 95%

### Test Structure

```python
# tests/unit/test_post_service.py
import pytest
from src.services.post_service import PostService
from src.errors import ForbiddenError

def test_create_post(mock_db):
    service = PostService(mock_db)
    post = service.create_post(
        user_id=1,
        title="Test Post",
        content="Test content",
        tags=["test"]
    )
    
    assert post.title == "Test Post"
    assert post.slug == "test-post"
    assert post.status == "draft"

def test_publish_post_wrong_author(mock_db):
    service = PostService(mock_db)
    # Mock existing post with author_id=1
    
    with pytest.raises(ForbiddenError):
        service.publish_post(user_id=2, post_id=1)

# tests/integration/test_posts_api.py
def test_create_post_endpoint(client, auth_headers):
    response = client.post(
        '/api/v1/posts',
        json={"title": "Test", "content": "Content"},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json['status'] == 'draft'
    assert 'id' in response.json
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_post_service.py

# Run with verbose output
pytest -v
```

## Database Migrations

### Creating Migrations

```bash
# Initialize migrations (first time)
flask db init

# Create new migration
flask db migrate -m "Create posts table"

# Apply migrations
flask db upgrade

# Rollback one migration
flask db downgrade

# Show migration history
flask db history
```

### Migration Template

```python
# migrations/versions/001_create_posts_table.py
def upgrade():
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('slug', sa.String(250), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_index('idx_posts_slug', 'posts', ['slug'], unique=True)
    op.create_foreign_key(None, 'posts', 'users', ['author_id'], ['id'])

def downgrade():
    op.drop_table('posts')
```

## Commit Message Format

```
type(scope): brief description

- Detailed change 1
- Detailed change 2

Related spec: .ldf/specs/{feature}/tasks.md [Task X.Y]
```

**Types:** feat, fix, refactor, test, docs, chore

## Technology Stack

- **Python 3.10+** - Language
- **Flask 3.0+** - Web framework
- **SQLAlchemy 2.0+** - ORM
- **PostgreSQL 14+** - Database
- **Flask-JWT-Extended** - Authentication
- **Marshmallow 3.0+** - Serialization/validation
- **Flask-Limiter** - Rate limiting
- **pytest** - Testing
- **Alembic** - Database migrations

## When to Ask Clarification

**ALWAYS ask before:**
- Writing code without approved spec
- Making architectural decisions not in design.md
- Changing API contracts
- Modifying database schema
- Adding new dependencies

**Can proceed without asking:**
- Following patterns in existing code
- Implementing approved tasks
- Writing tests for new code
- Fixing typos in comments
