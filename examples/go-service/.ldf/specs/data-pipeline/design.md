# data-pipeline - Design

## Architecture Overview

```
┌─────────────┐     ┌──────────────────────────────────────┐
│   Client    │────▶│           Pipeline Service           │
└─────────────┘     │  ┌──────────┐    ┌───────────────┐   │
                    │  │  Router  │───▶│PipelineService│   │
                    │  └──────────┘    └───────────────┘   │
                    │       │                 │            │
                    │       ▼                 ▼            │
                    │  ┌──────────┐    ┌───────────────┐   │
                    │  │   Auth   │    │  Processors   │   │
                    │  │Middleware│    │    Engine     │   │
                    │  └──────────┘    └───────────────┘   │
                    │                         │            │
                    └─────────────────────────│────────────┘
                                              ▼
                    ┌─────────────┐    ┌───────────────┐
                    │  PostgreSQL │    │     Redis     │
                    │  (storage)  │    │   (cache)     │
                    └─────────────┘    └───────────────┘
```

## S1: Data Layer

### S1.1: Database Schema

#### pipelines Table

```sql
CREATE TABLE pipelines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    config JSONB NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'inactive',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pipelines_owner_status ON pipelines(owner_id, status);
```

#### batches Table

```sql
CREATE TABLE batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_id UUID NOT NULL REFERENCES pipelines(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    record_count INT NOT NULL DEFAULT 0,
    processed_count INT NOT NULL DEFAULT 0,
    failed_count INT NOT NULL DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_batches_pipeline_status ON batches(pipeline_id, status);
CREATE INDEX idx_batches_pipeline_created ON batches(pipeline_id, created_at DESC);
```

#### batch_errors Table

```sql
CREATE TABLE batch_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID NOT NULL REFERENCES batches(id) ON DELETE CASCADE,
    record_index INT NOT NULL,
    error_code VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    record_data JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_batch_errors_batch ON batch_errors(batch_id);
```

### S1.2: Migrations

Migration files using golang-migrate:
1. `001_create_pipelines.up.sql` / `001_create_pipelines.down.sql`
2. `002_create_batches.up.sql` / `002_create_batches.down.sql`
3. `003_create_batch_errors.up.sql` / `003_create_batch_errors.down.sql`

## S2: Security Layer

### S2.1: API Key Authentication

```go
// internal/api/middleware/auth.go
func APIKeyAuth(keyStore KeyStore) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            apiKey := r.Header.Get("X-API-Key")
            if apiKey == "" {
                http.Error(w, `{"error":{"code":"UNAUTHORIZED","message":"Missing API key"}}`, 401)
                return
            }

            owner, err := keyStore.ValidateKey(r.Context(), apiKey)
            if err != nil {
                http.Error(w, `{"error":{"code":"UNAUTHORIZED","message":"Invalid API key"}}`, 401)
                return
            }

            ctx := context.WithValue(r.Context(), OwnerIDKey, owner.ID)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}
```

### S2.2: Input Validation

```go
// internal/api/dto/pipeline.go
type CreatePipelineRequest struct {
    Name   string         `json:"name" validate:"required,min=1,max=255"`
    Config PipelineConfig `json:"config" validate:"required"`
}

type PipelineConfig struct {
    Source      SourceConfig      `json:"source" validate:"required"`
    Processors  []ProcessorConfig `json:"processors" validate:"dive"`
    Destination DestinationConfig `json:"destination" validate:"required"`
}

func (r *CreatePipelineRequest) Validate() error {
    validate := validator.New()
    return validate.Struct(r)
}
```

## S3: Service Layer

### S3.1: API Endpoints

```go
// internal/api/router.go
func NewRouter(svc *pipeline.Service, logger *slog.Logger) chi.Router {
    r := chi.NewRouter()

    r.Use(middleware.RequestID)
    r.Use(middleware.RealIP)
    r.Use(LoggerMiddleware(logger))
    r.Use(middleware.Recoverer)

    r.Route("/api/v1", func(r chi.Router) {
        r.Use(APIKeyAuth(svc.KeyStore()))

        r.Route("/pipelines", func(r chi.Router) {
            r.Get("/", ListPipelines(svc))
            r.Post("/", CreatePipeline(svc))

            r.Route("/{pipelineID}", func(r chi.Router) {
                r.Get("/", GetPipeline(svc))
                r.Put("/", UpdatePipeline(svc))
                r.Delete("/", DeletePipeline(svc))
                r.Post("/start", StartPipeline(svc))
                r.Post("/stop", StopPipeline(svc))

                r.Route("/batches", func(r chi.Router) {
                    r.Get("/", ListBatches(svc))
                    r.Post("/", SubmitBatch(svc))
                    r.Get("/{batchID}", GetBatch(svc))
                })
            })
        })
    })

    return r
}
```

### S3.2: Pipeline Service

```go
// internal/pipeline/service.go
type Service struct {
    repo   Repository
    cache  Cache
    engine *ProcessorEngine
    logger *slog.Logger
}

func (s *Service) CreatePipeline(ctx context.Context, ownerID uuid.UUID, req CreateRequest) (*Pipeline, error) {
    // Validate configuration
    if err := s.validateConfig(req.Config); err != nil {
        return nil, fmt.Errorf("invalid config: %w", err)
    }

    pipeline := &Pipeline{
        ID:        uuid.New(),
        OwnerID:   ownerID,
        Name:      req.Name,
        Config:    req.Config,
        Status:    StatusInactive,
        CreatedAt: time.Now(),
        UpdatedAt: time.Now(),
    }

    if err := s.repo.Create(ctx, pipeline); err != nil {
        return nil, fmt.Errorf("failed to create pipeline: %w", err)
    }

    s.logger.Info("pipeline created",
        slog.String("pipeline_id", pipeline.ID.String()),
        slog.String("owner_id", ownerID.String()),
    )

    return pipeline, nil
}

func (s *Service) ProcessBatch(ctx context.Context, pipelineID uuid.UUID, records []Record) (*Batch, error) {
    pipeline, err := s.repo.GetByID(ctx, pipelineID)
    if err != nil {
        return nil, fmt.Errorf("pipeline not found: %w", err)
    }

    if pipeline.Status != StatusActive {
        return nil, ErrPipelineNotActive
    }

    batch := &Batch{
        ID:          uuid.New(),
        PipelineID:  pipelineID,
        Status:      BatchStatusPending,
        RecordCount: len(records),
        CreatedAt:   time.Now(),
    }

    if err := s.repo.CreateBatch(ctx, batch); err != nil {
        return nil, fmt.Errorf("failed to create batch: %w", err)
    }

    // Process asynchronously
    go s.processBatchAsync(context.Background(), batch, pipeline, records)

    return batch, nil
}

func (s *Service) processBatchAsync(ctx context.Context, batch *Batch, pipeline *Pipeline, records []Record) {
    batch.Status = BatchStatusProcessing
    batch.StartedAt = ptr(time.Now())
    s.repo.UpdateBatch(ctx, batch)

    var errors []BatchError
    processed := 0

    for i, record := range records {
        result, err := s.engine.Process(ctx, pipeline.Config.Processors, record)
        if err != nil {
            errors = append(errors, BatchError{
                BatchID:      batch.ID,
                RecordIndex:  i,
                ErrorCode:    "PROCESSING_ERROR",
                ErrorMessage: err.Error(),
                RecordData:   record.Data,
            })
            continue
        }

        if err := s.writeToDestination(ctx, pipeline.Config.Destination, result); err != nil {
            errors = append(errors, BatchError{
                BatchID:      batch.ID,
                RecordIndex:  i,
                ErrorCode:    "DESTINATION_ERROR",
                ErrorMessage: err.Error(),
            })
            continue
        }

        processed++
    }

    batch.Status = BatchStatusCompleted
    batch.ProcessedCount = processed
    batch.FailedCount = len(errors)
    batch.CompletedAt = ptr(time.Now())
    s.repo.UpdateBatch(ctx, batch)

    if len(errors) > 0 {
        s.repo.CreateBatchErrors(ctx, errors)
    }
}
```

### S3.3: Logging

```go
// internal/api/middleware/logger.go
func LoggerMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()
            ww := middleware.NewWrapResponseWriter(w, r.ProtoMajor)

            defer func() {
                logger.Info("request",
                    slog.String("request_id", middleware.GetReqID(r.Context())),
                    slog.String("method", r.Method),
                    slog.String("path", r.URL.Path),
                    slog.Int("status", ww.Status()),
                    slog.Duration("duration", time.Since(start)),
                    slog.String("remote_addr", r.RemoteAddr),
                )
            }()

            next.ServeHTTP(ww, r)
        })
    }
}
```

## S4: Testing Strategy

### S4.1: Test Structure

```
tests/
├── unit/
│   ├── pipeline_service_test.go
│   ├── processor_engine_test.go
│   └── validators_test.go
├── integration/
│   ├── api_test.go
│   └── repository_test.go
└── e2e/
    └── pipeline_flow_test.go
```

### S4.2: API Documentation

OpenAPI 3.0 spec generated with swaggo/swag:
- All endpoints documented with annotations
- Request/response schemas
- Error responses
- Authentication requirements

## Guardrail Mapping

| Guardrail | Implementation | Section |
|-----------|---------------|---------|
| 1. Testing Coverage | Unit + Integration + E2E tests | S4.1 |
| 2. Security Basics | API key auth, input validation | S2 |
| 3. Error Handling | Typed errors, consistent format | S3.2 |
| 4. Logging & Observability | Structured logging with slog | S3.3 |
| 5. API Design | Chi router, RESTful design | S3.1 |
| 6. Data Validation | go-validator structs | S2.2 |
| 7. Database Migrations | golang-migrate | S1.2 |
| 8. Documentation | swaggo/swag annotations | S4.2 |

## Dependencies

```
require (
    github.com/go-chi/chi/v5 v5.0.10
    github.com/go-playground/validator/v10 v10.16.0
    github.com/google/uuid v1.4.0
    github.com/jmoiron/sqlx v1.3.5
    github.com/lib/pq v1.10.9
    github.com/redis/go-redis/v9 v9.3.0
    github.com/stretchr/testify v1.8.4
    github.com/golang-migrate/migrate/v4 v4.16.2
)
```
