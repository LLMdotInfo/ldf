# Data Pipeline Service - Development Guide

## Project Overview

**Name:** Data Pipeline Service
**Purpose:** Process and transform data streams with configurable pipelines
**Stack:** Go 1.21+ with Chi router, PostgreSQL, Redis

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
├── cmd/
│   └── server/
│       └── main.go           # Entry point
├── internal/
│   ├── api/                  # HTTP handlers
│   ├── pipeline/             # Pipeline logic
│   ├── processor/            # Data processors
│   ├── storage/              # Database layer
│   └── config/               # Configuration
├── pkg/                      # Shared packages
├── migrations/               # SQL migrations
└── tests/                    # Integration tests
```

### Service Layer Pattern

```go
// internal/pipeline/service.go
type Service struct {
    repo    Repository
    cache   Cache
    logger  *slog.Logger
}

func NewService(repo Repository, cache Cache, logger *slog.Logger) *Service {
    return &Service{repo: repo, cache: cache, logger: logger}
}

func (s *Service) ProcessBatch(ctx context.Context, batch Batch) error {
    // Business logic here
}
```

### Error Handling

```go
// Use typed errors
var (
    ErrPipelineNotFound = errors.New("pipeline not found")
    ErrInvalidConfig    = errors.New("invalid pipeline configuration")
)

// Wrap errors with context
return fmt.Errorf("failed to process batch %s: %w", batchID, err)
```

### API Design

```go
// Chi router with middleware
r := chi.NewRouter()
r.Use(middleware.RequestID)
r.Use(middleware.Logger)
r.Use(middleware.Recoverer)

r.Route("/api/v1", func(r chi.Router) {
    r.Route("/pipelines", func(r chi.Router) {
        r.Get("/", h.ListPipelines)
        r.Post("/", h.CreatePipeline)
        r.Get("/{id}", h.GetPipeline)
        r.Put("/{id}", h.UpdatePipeline)
        r.Delete("/{id}", h.DeletePipeline)
    })
})
```

## Testing Standards

### Coverage Requirements
- Minimum: 80% overall
- Pipeline logic: 90%
- Processor logic: 90%

### Test Structure

```go
func TestService_ProcessBatch(t *testing.T) {
    t.Run("success", func(t *testing.T) {
        // Arrange
        svc := NewService(mockRepo, mockCache, slog.Default())

        // Act
        err := svc.ProcessBatch(ctx, batch)

        // Assert
        require.NoError(t, err)
    })

    t.Run("invalid config", func(t *testing.T) {
        // ...
    })
}
```

## Commit Message Format

```
type(scope): brief description

- Detailed change 1
- Detailed change 2

Related spec: .ldf/specs/{feature}/tasks.md [Task X.Y]
```

## Technology Stack

- **Go 1.21+** - Language
- **Chi** - HTTP router
- **sqlx** - Database access
- **Redis** - Caching
- **slog** - Structured logging
- **testify** - Testing assertions

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
