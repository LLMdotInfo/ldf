<!-- TEMPLATE EXAMPLE: This is a reference implementation showing how to complete
     a requirements document. Modify for your specific project needs. -->

# blog-api - Requirements

## Overview

Blog API system for the Flask application allowing users to create, read, update, and delete blog posts. Includes support for post drafts, publishing, and basic commenting functionality.

## User Stories

### US-1: Create Blog Post

**As a** authenticated user
**I want to** create a new blog post
**So that** I can share my content with others

**Acceptance Criteria:**
- [ ] AC-1.1: User can submit title, content, and optional tags
- [ ] AC-1.2: Title must be 1-200 characters
- [ ] AC-1.3: Content must be non-empty (max 50,000 characters)
- [ ] AC-1.4: Posts default to draft status
- [ ] AC-1.5: Successful creation returns post with ID and timestamps

### US-2: Publish Blog Post

**As a** post author
**I want to** publish my draft post
**So that** others can read it

**Acceptance Criteria:**
- [ ] AC-2.1: Only post author can publish
- [ ] AC-2.2: Published posts get published_at timestamp
- [ ] AC-2.3: Cannot unpublish (status change is one-way)
- [ ] AC-2.4: Returns 404 if post not found
- [ ] AC-2.5: Returns 403 if user is not the author

### US-3: List Blog Posts

**As a** visitor
**I want to** view published blog posts
**So that** I can read available content

**Acceptance Criteria:**
- [ ] AC-3.1: Returns only published posts (not drafts)
- [ ] AC-3.2: Results are paginated (20 per page default)
- [ ] AC-3.3: Posts ordered by published_at (newest first)
- [ ] AC-3.4: Includes author information in response
- [ ] AC-3.5: Supports filtering by tag

### US-4: View Single Post

**As a** visitor
**I want to** view a specific blog post
**So that** I can read its full content

**Acceptance Criteria:**
- [ ] AC-4.1: Returns full post with content and metadata
- [ ] AC-4.2: Includes author information
- [ ] AC-4.3: Returns 404 if post not found or not published
- [ ] AC-4.4: Drafts only visible to author

### US-5: Update Blog Post

**As a** post author
**I want to** edit my blog post
**So that** I can correct mistakes or add new information

**Acceptance Criteria:**
- [ ] AC-5.1: Only author can update their posts
- [ ] AC-5.2: Can update title, content, and tags
- [ ] AC-5.3: Cannot change author or creation date
- [ ] AC-5.4: Updated_at timestamp is automatically set
- [ ] AC-5.5: Returns 403 if user is not the author

### US-6: Delete Blog Post

**As a** post author
**I want to** delete my blog post
**So that** I can remove unwanted content

**Acceptance Criteria:**
- [ ] AC-6.1: Only author can delete their posts
- [ ] AC-6.2: Soft delete (marks as deleted, doesn't remove from DB)
- [ ] AC-6.3: Deleted posts are not visible in listings
- [ ] AC-6.4: Returns 404 if post not found
- [ ] AC-6.5: Returns 403 if user is not the author

### US-7: Add Comment

**As a** authenticated user
**I want to** comment on a blog post
**So that** I can engage with the content

**Acceptance Criteria:**
- [ ] AC-7.1: User can submit comment text (1-1000 characters)
- [ ] AC-7.2: Comments can only be added to published posts
- [ ] AC-7.3: Comment includes author info and timestamp
- [ ] AC-7.4: Returns 404 if post not found

## Question-Pack Answers

### Security

**Authentication Method:**
- Method: JWT tokens via Flask-JWT-Extended
- Rationale: Stateless authentication, integrates well with Flask

**Authorization:**
- Model: Resource-based (only authors can modify their posts)
- Implementation: Decorator functions checking user_id == post.author_id
- Rationale: Simple, clear ownership model

**Input Validation:**
- Method: Flask-Marshmallow schemas with validation
- Sanitization: HTML tags stripped from content (Bleach library)
- Rationale: Prevent XSS attacks, maintain data integrity

**Rate Limiting:**
- Create post: 10 per hour per user
- Add comment: 30 per hour per user
- Read operations: 1000 per hour per IP
- Rationale: Prevent spam and abuse

### Testing

**Test Coverage Goals:**
- Overall: 85%
- API routes: 90%
- Service layer: 95%

**Test Types:**
- Unit: Service functions, validators, helpers
- Integration: API endpoints with test database
- E2E: Full user workflows (create → publish → comment)

**Test Data Strategy:**
- Fixtures: pytest fixtures for users and posts
- Factory: Factory functions for test data creation
- Isolation: Each test uses transaction rollback

**Critical Paths:**
1. Post creation and publishing flow
2. Authorization checks (author-only operations)
3. Pagination and filtering
4. Soft delete functionality

### API Design

**Versioning:**
- Pattern: URL prefix `/api/v1/`
- Migration: New versions introduced, old ones deprecated over 6 months
- Rationale: Clear version identification, predictable deprecation

**Pagination:**
- Method: Offset-based (`?page=1&per_page=20`)
- Default: 20 items per page
- Max: 100 items per page
- Response: Includes total, page, per_page, has_next, has_prev

**Error Format:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title is required",
    "details": {
      "field": "title",
      "constraint": "required"
    }
  }
}
```

**Status Codes:**
- 200: Success (GET, PUT)
- 201: Created (POST)
- 204: No content (DELETE)
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 429: Too many requests
- 500: Server error

### Data Model

**Post States:**
- Draft: Created but not published
- Published: Visible to all users
- Deleted: Soft deleted, not visible

**Relationships:**
- User → Posts: One-to-many
- Post → Comments: One-to-many
- User → Comments: One-to-many

**Indexes:**
- posts.author_id (foreign key)
- posts.status (for filtering)
- posts.published_at (for sorting)
- comments.post_id (foreign key)
- tags.post_id (for filtering)

**Timestamps:**
- All entities have created_at and updated_at
- Posts additionally have published_at (nullable)

## Guardrail Coverage Matrix

| # | Guardrail | Applicable | Covered By | Notes |
|---|-----------|------------|------------|-------|
| 1 | Testing Coverage | ✅ Yes | All tasks | 85% overall, 90% routes, 95% services |
| 2 | Security Basics | ✅ Yes | Tasks 1.1, 2.x, 3.x | JWT auth, input validation, XSS prevention |
| 3 | Error Handling | ✅ Yes | Task 1.2, all routes | Consistent error responses, proper HTTP codes |
| 4 | Logging & Observability | ✅ Yes | Task 1.3 | Structured logging with context |
| 5 | API Design | ✅ Yes | Task 2.x | Versioned (/v1/), paginated, consistent errors |
| 6 | Data Validation | ✅ Yes | Task 2.x, 3.x | Marshmallow schemas, business rules |
| 7 | Database Migrations | ✅ Yes | Task 1.4 | Alembic migrations, reversible |
| 8 | Documentation | ✅ Yes | Task 4.x | API docs, inline comments, README |

## Success Metrics

**Performance:**
- API response time: p95 < 200ms
- Database query time: p95 < 50ms

**Quality:**
- Test coverage: ≥85%
- Zero high-severity security issues

**Usability:**
- API consistency score: 100% (all endpoints follow same patterns)
- Error message clarity: User-friendly, actionable messages
