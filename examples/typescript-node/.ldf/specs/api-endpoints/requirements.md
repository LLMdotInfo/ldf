<!-- TEMPLATE EXAMPLE: This is a reference implementation showing how to complete
     a requirements document. Modify for your specific project needs. -->

# api-endpoints - Requirements

## Overview

RESTful API endpoints for a task management application. Provides CRUD operations for tasks with filtering and pagination.

## User Stories

### US-1: List Tasks

**As a** user
**I want to** see all my tasks with filtering options
**So that** I can find and manage my work

**Acceptance Criteria:**
- [ ] AC-1.1: GET /api/v1/tasks returns paginated task list
- [ ] AC-1.2: Can filter by status (pending, completed, archived)
- [ ] AC-1.3: Can filter by due date range
- [ ] AC-1.4: Default page size is 20, max is 100
- [ ] AC-1.5: Response includes total count and pagination metadata

### US-2: Create Task

**As a** user
**I want to** create a new task
**So that** I can track work items

**Acceptance Criteria:**
- [ ] AC-2.1: POST /api/v1/tasks creates new task
- [ ] AC-2.2: Title is required (1-200 characters)
- [ ] AC-2.3: Description is optional (max 2000 characters)
- [ ] AC-2.4: Due date is optional, must be in future
- [ ] AC-2.5: Returns 201 with created task

### US-3: Update Task

**As a** user
**I want to** update an existing task
**So that** I can modify task details

**Acceptance Criteria:**
- [ ] AC-3.1: PUT /api/v1/tasks/:id updates task
- [ ] AC-3.2: Can update title, description, due_date, status
- [ ] AC-3.3: Returns 404 if task not found
- [ ] AC-3.4: Returns 200 with updated task

### US-4: Delete Task

**As a** user
**I want to** delete a task
**So that** I can remove completed or unwanted items

**Acceptance Criteria:**
- [ ] AC-4.1: DELETE /api/v1/tasks/:id removes task
- [ ] AC-4.2: Returns 404 if task not found
- [ ] AC-4.3: Returns 204 on success

## Question-Pack Answers

### Security

**Authentication:**
- Method: Bearer token (JWT) in Authorization header
- Validation: Middleware validates on all /api/v1/tasks/* routes

**Authorization:**
- Users can only access their own tasks
- Task ownership checked on every operation

### Testing

**Coverage Requirements:**
- API routes: 85% minimum
- Service layer: 90% minimum
- Overall: 80% minimum

**Test Types:**
- Unit tests for TaskService
- Integration tests for endpoints
- E2E tests for complete flows

### API Design

**Base Path:** `/api/v1/tasks`

**Pagination Format:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 42,
    "totalPages": 3
  }
}
```

**Error Format:**
```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with ID xyz not found"
  }
}
```

### Data Model

**Tables:**
- `tasks`: id, user_id, title, description, status, due_date, created_at, updated_at

**Indexes:**
- tasks(user_id, status)
- tasks(user_id, due_date)

## Guardrail Coverage Matrix

| Guardrail | Requirements | Design | Tasks/Tests | Owner | Status |
|-----------|--------------|--------|-------------|-------|--------|
| 1. Testing Coverage | [US-1..4] | [S4.1] | [T-4.1..3] | @dev-team | IN PROGRESS |
| 2. Security Basics | [US-1..4] | [S2.1] | [T-2.1] | @security | DONE |
| 3. Error Handling | [US-1..4] | [S3.2] | [T-3.3] | @dev-team | DONE |
| 4. Logging & Observability | [US-1..4] | [S3.3] | [T-3.4] | @dev-team | DONE |
| 5. API Design | [US-1..4] | [S3.1] | [T-1.1] | @dev-team | DONE |
| 6. Data Validation | [US-2, US-3] | [S2.2] | [T-2.2] | @dev-team | DONE |
| 7. Database Migrations | [All] | [S1.2] | [T-1.2] | @dev-team | DONE |
| 8. Documentation | [All] | [S4.2] | [T-5.1] | @dev-team | TODO |

## Dependencies

- express ^4.18
- prisma ^5.0
- zod ^3.22
- winston ^3.11
- jest ^29.0
- supertest ^6.3

## Out of Scope

- Task sharing/collaboration
- Task attachments
- Task comments
- Recurring tasks
