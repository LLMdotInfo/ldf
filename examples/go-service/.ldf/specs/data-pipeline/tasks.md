# data-pipeline - Tasks

**Status:** Ready for Implementation

## Per-Task Guardrail Checklist

**Reference:** `.ldf/guardrails.yaml`

Before implementing each task, verify applicable guardrails:

- [ ] **1. Testing Coverage:** Unit tests for business logic; integration tests for APIs; coverage ≥80%
- [ ] **2. Security Basics:** Input validation; parameterized queries; auth/authz checks
- [ ] **3. Error Handling:** Consistent error responses; proper exception hierarchy
- [ ] **4. Logging & Observability:** Structured logging with slog; correlation IDs
- [ ] **5. API Design:** Versioned endpoints (/v1/); consistent error format
- [ ] **6. Data Validation:** Request schema validation; business rule validation
- [ ] **7. Database Migrations:** Reversible migrations; rollback tested
- [ ] **8. Documentation:** API docs updated; README current

---

## Phase 1: Setup

- [ ] **Task 1.1:** Create project structure
  - [ ] Create `cmd/server/main.go`
  - [ ] Create `internal/api/`, `internal/pipeline/`, `internal/storage/`
  - [ ] Create `tests/` directory
  - [ ] Initialize go.mod

- [ ] **Task 1.2:** Create database migrations
  - [ ] Create migrations for pipelines, batches, batch_errors
  - [ ] Add indexes
  - [ ] Test migrate up/down

- [ ] **Task 1.3:** Create repository layer
  - [ ] Create Pipeline, Batch, BatchError structs
  - [ ] Implement PipelineRepository interface
  - [ ] Implement sqlx repository

## Phase 2: Core Service

- [ ] **Task 2.1:** Implement API key authentication
  - [ ] Create KeyStore interface
  - [ ] Create auth middleware with rate limiting
  - [ ] Write unit tests

- [ ] **Task 2.2:** Implement input validation
  - [ ] Create request DTOs with validation
  - [ ] Write unit tests for validators

- [ ] **Task 2.3:** Implement PipelineService
  - [ ] Implement CRUD methods with owner scoping
  - [ ] Implement StartPipeline/StopPipeline
  - [ ] Write comprehensive unit tests

- [ ] **Task 2.4:** Implement ProcessorEngine
  - [ ] Create Processor interface
  - [ ] Create ProcessorEngine with chain execution
  - [ ] Implement per-record error capture
  - [ ] Write unit tests

## Phase 3: API Layer

- [ ] **Task 3.1:** Implement pipeline endpoints
  - [ ] Create Chi router with `/api/v1` prefix
  - [ ] Implement CRUD endpoints for pipelines
  - [ ] Write integration tests

- [ ] **Task 3.2:** Implement batch endpoints
  - [ ] Implement batch submission and status endpoints
  - [ ] Write integration tests

- [ ] **Task 3.3:** Implement error handlers
  - [ ] Create custom error types
  - [ ] Create error handler middleware
  - [ ] Format errors as standard JSON

- [ ] **Task 3.4:** Add logging middleware
  - [ ] Create request ID middleware
  - [ ] Create structured logging middleware
  - [ ] Verify no secrets in logs

## Phase 4: Testing

- [ ] **Task 4.1:** Write unit tests
  - [ ] Test PipelineService (90% coverage)
  - [ ] Test ProcessorEngine
  - [ ] Test validators and auth middleware

- [ ] **Task 4.2:** Write integration tests
  - [ ] Test pipeline CRUD flow
  - [ ] Test batch submission flow
  - [ ] Test error responses

- [ ] **Task 4.3:** Write E2E tests
  - [ ] Test full pipeline → batch → completion flow
  - [ ] Test concurrent batches

## Phase 5: Documentation

- [ ] **Task 5.1:** Update documentation
  - [ ] Add swaggo annotations to handlers
  - [ ] Generate OpenAPI spec
  - [ ] Update project README
  - [ ] Document environment variables

## Completion Checklist

- [ ] All tasks completed
- [ ] All tests passing
- [ ] Coverage ≥80% overall, ≥90% for pipeline/processor
- [ ] Documentation complete
- [ ] Code reviewed
