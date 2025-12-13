# data-pipeline - Tasks

**Status:** Ready for Implementation
**Total Tasks:** 15
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

### Task 1.1: Create project structure
**Guardrail Checklist:**
- [ ] Testing: Test directory created
- [ ] API Design: Router structure follows /api/v1 pattern
- [ ] Documentation: README updated

**Subtasks:**
- [ ] Create `cmd/server/main.go`
- [ ] Create `internal/api/` directory
- [ ] Create `internal/pipeline/` directory
- [ ] Create `internal/storage/` directory
- [ ] Create `tests/` directory
- [ ] Initialize go.mod

### Task 1.2: Create database migrations
**Guardrail Checklist:**
- [ ] Database Migrations: Reversible with down migrations
- [ ] Database Migrations: Separate from backfills

**Subtasks:**
- [ ] Create `001_create_pipelines.up.sql` / `.down.sql`
- [ ] Create `002_create_batches.up.sql` / `.down.sql`
- [ ] Create `003_create_batch_errors.up.sql` / `.down.sql`
- [ ] Add indexes
- [ ] Test migrate up/down

### Task 1.3: Create repository layer
**Guardrail Checklist:**
- [ ] Data Validation: Proper column constraints
- [ ] Security: Parameterized queries

**Subtasks:**
- [ ] Create `Pipeline` struct
- [ ] Create `Batch` struct
- [ ] Create `BatchError` struct
- [ ] Implement `PipelineRepository` interface
- [ ] Implement sqlx repository

## Phase 2: Core Service

### Task 2.1: Implement API key authentication
**Guardrail Checklist:**
- [ ] Security: Hash API keys in storage
- [ ] Security: Rate limiting per key
- [ ] Testing: Unit tests for auth middleware

**Subtasks:**
- [ ] Create `KeyStore` interface
- [ ] Create auth middleware
- [ ] Add rate limiting
- [ ] Write unit tests

### Task 2.2: Implement input validation
**Guardrail Checklist:**
- [ ] Data Validation: Request schema validation
- [ ] Error Handling: Validation error format
- [ ] Testing: Unit tests for validators

**Subtasks:**
- [ ] Create `CreatePipelineRequest` DTO
- [ ] Create `PipelineConfig` validation
- [ ] Create `SubmitBatchRequest` DTO
- [ ] Write unit tests

### Task 2.3: Implement PipelineService
**Guardrail Checklist:**
- [ ] Security: Owner scoping
- [ ] Error Handling: Typed errors
- [ ] Testing: Unit tests with mocked repos

**Subtasks:**
- [ ] Implement `CreatePipeline()`
- [ ] Implement `GetPipeline()` with owner check
- [ ] Implement `UpdatePipeline()`
- [ ] Implement `DeletePipeline()` with active batch check
- [ ] Implement `StartPipeline()` / `StopPipeline()`
- [ ] Write comprehensive unit tests

### Task 2.4: Implement ProcessorEngine
**Guardrail Checklist:**
- [ ] Error Handling: Per-record error capture
- [ ] Logging: Processing metrics
- [ ] Testing: Unit tests for each processor

**Subtasks:**
- [ ] Create `Processor` interface
- [ ] Create `ProcessorEngine` with chain execution
- [ ] Implement error capture per record
- [ ] Write unit tests

## Phase 3: API Layer

### Task 3.1: Implement pipeline endpoints
**Guardrail Checklist:**
- [ ] API Design: RESTful with /api/v1 prefix
- [ ] Error Handling: Consistent error format
- [ ] Testing: Integration tests

**Subtasks:**
- [ ] Create Chi router
- [ ] Implement `POST /pipelines`
- [ ] Implement `GET /pipelines`
- [ ] Implement `GET /pipelines/{id}`
- [ ] Implement `PUT /pipelines/{id}`
- [ ] Implement `DELETE /pipelines/{id}`
- [ ] Write integration tests

### Task 3.2: Implement batch endpoints
**Guardrail Checklist:**
- [ ] API Design: Async processing pattern
- [ ] Error Handling: Batch status tracking
- [ ] Testing: Integration tests

**Subtasks:**
- [ ] Implement `POST /pipelines/{id}/batches`
- [ ] Implement `GET /pipelines/{id}/batches`
- [ ] Implement `GET /pipelines/{id}/batches/{batchId}`
- [ ] Write integration tests

### Task 3.3: Implement error handlers
**Guardrail Checklist:**
- [ ] Error Handling: Consistent error format
- [ ] Security: No stack traces in production

**Subtasks:**
- [ ] Create custom error types
- [ ] Create error handler middleware
- [ ] Format errors as `{"error": {"code": "", "message": ""}}`
- [ ] Test error responses

### Task 3.4: Add logging middleware
**Guardrail Checklist:**
- [ ] Logging: Structured logging with slog
- [ ] Logging: Request ID correlation
- [ ] Security: No sensitive data in logs

**Subtasks:**
- [ ] Create request ID middleware
- [ ] Create logging middleware
- [ ] Add request/response logging
- [ ] Verify no secrets in logs

## Phase 4: Testing

### Task 4.1: Write unit tests
**Guardrail Checklist:**
- [ ] Testing: 90% coverage for pipeline service

**Subtasks:**
- [ ] Test PipelineService methods
- [ ] Test ProcessorEngine
- [ ] Test validators
- [ ] Test auth middleware

### Task 4.2: Write integration tests
**Guardrail Checklist:**
- [ ] Testing: Full API flow tests

**Subtasks:**
- [ ] Test pipeline CRUD flow
- [ ] Test batch submission flow
- [ ] Test error responses
- [ ] Test rate limiting

### Task 4.3: Write E2E tests
**Guardrail Checklist:**
- [ ] Testing: Complete pipeline processing

**Subtasks:**
- [ ] Test full pipeline creation → batch → completion
- [ ] Test error handling flow
- [ ] Test concurrent batches

## Phase 5: Documentation

### Task 5.1: Update documentation
**Guardrail Checklist:**
- [ ] Documentation: API docs complete
- [ ] Documentation: README updated

**Subtasks:**
- [ ] Add swaggo annotations to handlers
- [ ] Generate OpenAPI spec
- [ ] Update project README
- [ ] Document environment variables

## Completion Checklist

- [ ] All 15 tasks completed
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All E2E tests passing
- [ ] Test coverage >= 80% overall, >= 90% for pipeline/processor
- [ ] No linting errors
- [ ] Documentation complete
- [ ] Code reviewed
