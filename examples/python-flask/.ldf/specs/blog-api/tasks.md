# blog-api - Tasks

**Status:** Ready for Implementation

## Per-Task Guardrail Checklist

**Reference:** `.ldf/guardrails.yaml`

Before implementing each task, verify applicable guardrails:

- [ ] **1. Testing Coverage:** Unit tests for business logic; integration tests for APIs; coverage ≥85%
- [ ] **2. Security Basics:** Input validation; parameterized queries; auth/authz checks
- [ ] **3. Error Handling:** Consistent error responses; proper exception hierarchy
- [ ] **4. Logging & Observability:** Structured logging; correlation IDs
- [ ] **5. API Design:** Versioned endpoints (/v1/); pagination; consistent format
- [ ] **6. Data Validation:** Schema validation; business rule validation
- [ ] **7. Database Migrations:** Reversible migrations; rollback tested
- [ ] **8. Documentation:** API docs updated; README current

---

## Phase 1: Setup

- [ ] **Task 1.1:** Create project structure
  - [ ] Create `src/` directory with `__init__.py`
  - [ ] Create `src/api/v1/` for blueprints
  - [ ] Create `src/models/`, `src/services/`, `src/schemas/`
  - [ ] Create `tests/` with unit and integration subdirectories

- [ ] **Task 1.2:** Set up Flask application
  - [ ] Create `src/app.py` with Flask app factory
  - [ ] Configure SQLAlchemy and Flask-JWT-Extended
  - [ ] Configure Flask-Limiter for rate limiting
  - [ ] Register error handlers

- [ ] **Task 1.3:** Create database migrations
  - [ ] Create migrations for users, posts, tags, comments
  - [ ] Add indexes as specified in design
  - [ ] Test upgrade and downgrade for each migration

## Phase 2: Core Models and Services

- [ ] **Task 2.1:** Implement User model
  - [ ] Create SQLAlchemy model with password hashing
  - [ ] Add relationships to posts and comments
  - [ ] Write unit tests

- [ ] **Task 2.2:** Implement Post model
  - [ ] Create SQLAlchemy model with slug generation
  - [ ] Add relationships to author, tags, comments
  - [ ] Write unit tests

- [ ] **Task 2.3:** Implement Tag and Comment models
  - [ ] Create Tag and Comment SQLAlchemy models
  - [ ] Add necessary relationships
  - [ ] Write unit tests

- [ ] **Task 2.4:** Implement PostService
  - [ ] Implement CRUD methods with authorization
  - [ ] Implement `publish_post()` with author check
  - [ ] Write comprehensive unit tests (95% coverage)

- [ ] **Task 2.5:** Implement CommentService
  - [ ] Implement CRUD methods
  - [ ] Validate against published posts only
  - [ ] Write unit tests

## Phase 3: API Layer

- [ ] **Task 3.1:** Create Marshmallow schemas
  - [ ] Create post and comment schemas with validators
  - [ ] Write validation tests

- [ ] **Task 3.2:** Implement Posts blueprint
  - [ ] Implement CRUD endpoints under `/api/v1/posts`
  - [ ] Add JWT authentication and rate limiting
  - [ ] Write integration tests (90% coverage)

- [ ] **Task 3.3:** Implement Comments blueprint
  - [ ] Implement endpoints under `/api/v1/posts/{id}/comments`
  - [ ] Add authentication and rate limiting
  - [ ] Write integration tests

- [ ] **Task 3.4:** Implement error handlers
  - [ ] Create custom exception classes
  - [ ] Register error handlers in app factory
  - [ ] Ensure standard JSON error format

## Phase 4: Security and Polish

- [ ] **Task 4.1:** Implement input sanitization
  - [ ] Add Bleach for HTML sanitization
  - [ ] Apply to post content and comments
  - [ ] Write XSS prevention tests

- [ ] **Task 4.2:** Add authorization helpers
  - [ ] Create `require_author()` decorator
  - [ ] Write authorization tests

- [ ] **Task 4.3:** Configure rate limiting
  - [ ] Configure Flask-Limiter with Redis
  - [ ] Apply limits to write operations
  - [ ] Write rate limit tests

## Phase 5: Documentation and Testing

- [ ] **Task 5.1:** Write comprehensive tests
  - [ ] Achieve overall coverage ≥85%
  - [ ] Add E2E workflow tests

- [ ] **Task 5.2:** Write API documentation
  - [ ] Document all endpoints with examples
  - [ ] Document rate limits

- [ ] **Task 5.3:** Update README
  - [ ] Add setup and testing instructions
  - [ ] Document environment variables

## Completion Checklist

- [ ] All tasks completed
- [ ] All tests passing
- [ ] Coverage meets thresholds
- [ ] Documentation complete
- [ ] Code reviewed
