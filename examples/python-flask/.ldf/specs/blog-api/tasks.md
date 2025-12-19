# blog-api - Tasks

**Status:** Ready for Implementation
**Total Tasks:** 18
**Completed:** 0

## Per-Task Guardrail Checklist

**Reference:** `.ldf/guardrails.yaml`

**Mark N/A if not applicable to the task.**

Before implementing each task, verify applicable guardrails:

- [ ] **1. Testing Coverage:** Unit tests for business logic; integration tests for APIs; coverage ≥85%
- [ ] **2. Security Basics:** Input validation; parameterized queries; auth/authz checks; no secrets in code
- [ ] **3. Error Handling:** Consistent error responses; proper exception hierarchy; user-friendly messages
- [ ] **4. Logging & Observability:** Structured logging; correlation IDs; appropriate log levels
- [ ] **5. API Design:** Versioned endpoints (/v1/); cursor pagination; consistent error format
- [ ] **6. Data Validation:** Request schema validation; business rule validation; output sanitization
- [ ] **7. Database Migrations:** Reversible migrations; rollback tested; backfills separate from schema
- [ ] **8. Documentation:** API docs updated; inline comments for complex logic; README current

---

## Phase 1: Setup

### Task 1.1: Create project structure
**Guardrail Checklist:**
- [ ] Testing: Test directory structure created
- [ ] API Design: Router structure follows /api/v1 pattern
- [ ] Documentation: README with setup instructions

**Subtasks:**
- [ ] Create `src/` directory with `__init__.py`
- [ ] Create `src/api/v1/` for blueprints
- [ ] Create `src/models/` for SQLAlchemy models
- [ ] Create `src/services/` for business logic
- [ ] Create `src/schemas/` for Marshmallow schemas
- [ ] Create `src/errors.py` for custom exceptions
- [ ] Create `tests/` with unit and integration subdirectories
- [ ] Create `config.py` for application configuration

### Task 1.2: Set up Flask application
**Guardrail Checklist:**
- [ ] Error Handling: Global error handlers registered
- [ ] Logging: Structured logging configured
- [ ] Security: JWT configuration set

**Subtasks:**
- [ ] Create `src/app.py` with Flask app factory
- [ ] Configure SQLAlchemy
- [ ] Configure Flask-JWT-Extended
- [ ] Configure Flask-Limiter for rate limiting
- [ ] Register error handlers
- [ ] Set up logging with correlation IDs

### Task 1.3: Create database migrations
**Guardrail Checklist:**
- [ ] Database Migrations: All migrations reversible
- [ ] Database Migrations: Tested rollback functionality

**Subtasks:**
- [ ] Initialize Alembic via Flask-Migrate
- [ ] Create migration: `001_create_users_table`
- [ ] Create migration: `002_create_posts_table`
- [ ] Create migration: `003_create_tags_and_post_tags_tables`
- [ ] Create migration: `004_create_comments_table`
- [ ] Add indexes as specified in design
- [ ] Test upgrade and downgrade for each migration

---

## Phase 2: Core Models and Services

### Task 2.1: Implement User model
**Guardrail Checklist:**
- [ ] Testing: Unit tests for model methods
- [ ] Documentation: Model fields documented

**Subtasks:**
- [ ] Create `src/models/user.py` with SQLAlchemy model
- [ ] Add password hashing methods
- [ ] Add relationships to posts and comments
- [ ] Write unit tests for User model

### Task 2.2: Implement Post model
**Guardrail Checklist:**
- [ ] Testing: Unit tests for model methods
- [ ] Data Validation: Slug generation validated

**Subtasks:**
- [ ] Create `src/models/post.py` with SQLAlchemy model
- [ ] Implement slug generation from title
- [ ] Add status property validators
- [ ] Add relationships to author, tags, comments
- [ ] Write unit tests for Post model

### Task 2.3: Implement Tag and Comment models
**Guardrail Checklist:**
- [ ] Testing: Unit tests for models

**Subtasks:**
- [ ] Create `src/models/tag.py` with SQLAlchemy model
- [ ] Create `src/models/comment.py` with SQLAlchemy model
- [ ] Add necessary relationships
- [ ] Write unit tests

### Task 2.4: Implement PostService
**Guardrail Checklist:**
- [ ] Testing: Unit tests with mocked repository (95% coverage)
- [ ] Security: Authorization checks for author-only operations
- [ ] Error Handling: Proper exception raising
- [ ] Logging: Key operations logged

**Subtasks:**
- [ ] Create `src/services/post_service.py`
- [ ] Implement `create_post()` method
- [ ] Implement `publish_post()` method with authorization
- [ ] Implement `update_post()` method with authorization
- [ ] Implement `delete_post()` method (soft delete) with authorization
- [ ] Implement `get_post()` method with visibility rules
- [ ] Implement `list_posts()` method with pagination
- [ ] Write comprehensive unit tests

### Task 2.5: Implement CommentService
**Guardrail Checklist:**
- [ ] Testing: Unit tests (95% coverage)
- [ ] Security: Validation against published posts only
- [ ] Error Handling: Proper exceptions

**Subtasks:**
- [ ] Create `src/services/comment_service.py`
- [ ] Implement `create_comment()` method
- [ ] Implement `list_comments()` method with pagination
- [ ] Implement `delete_comment()` method with authorization
- [ ] Write unit tests

---

## Phase 3: API Layer

### Task 3.1: Create Marshmallow schemas
**Guardrail Checklist:**
- [ ] Data Validation: All input fields validated
- [ ] Testing: Schema validation tests

**Subtasks:**
- [ ] Create `src/schemas/post_schemas.py`
- [ ] Implement `CreatePostSchema` with validators
- [ ] Implement `UpdatePostSchema`
- [ ] Implement `PostResponseSchema`
- [ ] Create `src/schemas/comment_schemas.py`
- [ ] Implement `CreateCommentSchema`
- [ ] Write validation tests

### Task 3.2: Implement Posts blueprint
**Guardrail Checklist:**
- [ ] Testing: Integration tests for all endpoints (90% coverage)
- [ ] Security: JWT authentication on protected routes
- [ ] Security: Rate limiting on write operations
- [ ] API Design: Consistent response format
- [ ] API Design: Proper status codes
- [ ] Error Handling: All errors return standard format
- [ ] Logging: All requests logged with correlation ID

**Subtasks:**
- [ ] Create `src/api/v1/posts.py` blueprint
- [ ] Implement POST `/api/v1/posts` (create)
- [ ] Implement GET `/api/v1/posts` (list with pagination)
- [ ] Implement GET `/api/v1/posts/{id}` (get single)
- [ ] Implement PUT `/api/v1/posts/{id}` (update)
- [ ] Implement DELETE `/api/v1/posts/{id}` (soft delete)
- [ ] Implement POST `/api/v1/posts/{id}/publish`
- [ ] Add rate limiting decorators
- [ ] Write integration tests for happy paths
- [ ] Write integration tests for error cases

### Task 3.3: Implement Comments blueprint
**Guardrail Checklist:**
- [ ] Testing: Integration tests (90% coverage)
- [ ] Security: JWT authentication on protected routes
- [ ] Security: Rate limiting on write operations
- [ ] API Design: Consistent response format
- [ ] Error Handling: Standard error format

**Subtasks:**
- [ ] Create `src/api/v1/comments.py` blueprint
- [ ] Implement POST `/api/v1/posts/{post_id}/comments`
- [ ] Implement GET `/api/v1/posts/{post_id}/comments` (with pagination)
- [ ] Implement DELETE `/api/v1/comments/{id}`
- [ ] Add rate limiting decorators
- [ ] Write integration tests

### Task 3.4: Implement error handlers
**Guardrail Checklist:**
- [ ] Error Handling: All error types handled
- [ ] Error Handling: Consistent response format
- [ ] Testing: Error handler tests

**Subtasks:**
- [ ] Create `src/errors.py` with custom exceptions
- [ ] Implement APIError base class
- [ ] Implement ValidationError, NotFoundError, ForbiddenError
- [ ] Register error handlers in app factory
- [ ] Ensure all errors return standard JSON format
- [ ] Write tests for error handling

---

## Phase 4: Security and Polish

### Task 4.1: Implement input sanitization
**Guardrail Checklist:**
- [ ] Security: HTML stripped from user content
- [ ] Testing: Sanitization tests

**Subtasks:**
- [ ] Add Bleach library dependency
- [ ] Create sanitization utility functions
- [ ] Apply sanitization to post content
- [ ] Apply sanitization to comments
- [ ] Write tests for XSS prevention

### Task 4.2: Add authorization helpers
**Guardrail Checklist:**
- [ ] Security: Consistent authorization checks
- [ ] Testing: Authorization test cases

**Subtasks:**
- [ ] Create `src/utils/auth.py`
- [ ] Implement `require_author()` decorator
- [ ] Add authorization checks to service methods
- [ ] Write tests for authorization failures

### Task 4.3: Configure rate limiting
**Guardrail Checklist:**
- [ ] Security: Rate limits on all write operations
- [ ] Testing: Rate limit tests

**Subtasks:**
- [ ] Configure Flask-Limiter with Redis backend
- [ ] Apply rate limits to post creation (10/hour)
- [ ] Apply rate limits to comment creation (30/hour)
- [ ] Apply rate limits to read operations (1000/hour per IP)
- [ ] Write tests verifying rate limits

---

## Phase 5: Documentation and Testing

### Task 5.1: Write comprehensive tests
**Guardrail Checklist:**
- [ ] Testing: Overall coverage ≥85%
- [ ] Testing: API routes coverage ≥90%
- [ ] Testing: Service layer coverage ≥95%

**Subtasks:**
- [ ] Review and fill coverage gaps
- [ ] Add edge case tests
- [ ] Add E2E workflow tests (create → publish → comment)
- [ ] Verify all critical paths have tests
- [ ] Run coverage report and address gaps

### Task 5.2: Write API documentation
**Guardrail Checklist:**
- [ ] Documentation: All endpoints documented
- [ ] Documentation: Request/response examples included

**Subtasks:**
- [ ] Create `API.md` with endpoint documentation
- [ ] Document all request schemas
- [ ] Document all response schemas
- [ ] Add authentication examples
- [ ] Add error response examples
- [ ] Document rate limits

### Task 5.3: Update README
**Guardrail Checklist:**
- [ ] Documentation: Setup instructions clear
- [ ] Documentation: Running tests documented

**Subtasks:**
- [ ] Add installation instructions
- [ ] Add database setup instructions
- [ ] Add development server instructions
- [ ] Add testing instructions
- [ ] Add deployment considerations
- [ ] Add environment variable documentation

---

## Phase 6: Final Validation

### Task 6.1: Run full test suite
**Subtasks:**
- [ ] Run all unit tests
- [ ] Run all integration tests
- [ ] Verify coverage meets thresholds
- [ ] Fix any failing tests

### Task 6.2: Manual testing
**Subtasks:**
- [ ] Test full create → publish → comment workflow
- [ ] Test authorization (try accessing others' posts)
- [ ] Test rate limiting behavior
- [ ] Test error responses
- [ ] Test pagination
- [ ] Test filtering by tags

### Task 6.3: Security review
**Guardrail Checklist:**
- [ ] Security: All auth/authz paths tested
- [ ] Security: Input sanitization verified
- [ ] Security: Rate limiting verified

**Subtasks:**
- [ ] Review all authentication points
- [ ] Review all authorization checks
- [ ] Verify input sanitization
- [ ] Check for any secrets in code
- [ ] Review SQL queries for injection risks
- [ ] Test XSS prevention
