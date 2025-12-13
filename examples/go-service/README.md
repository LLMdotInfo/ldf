# Go Service Example

A Go data pipeline service example demonstrating LDF spec-driven development.

## Overview

This example shows how to use LDF with a Go service that processes and transforms data streams.

**Stack:** Go 1.21+, Chi router, PostgreSQL, Redis

## Structure

```
.ldf/
├── config.yaml              # LDF configuration (api-only preset)
├── guardrails.yaml          # Custom guardrail overrides
└── specs/
    └── data-pipeline/
        ├── requirements.md  # User stories and acceptance criteria
        ├── design.md        # Architecture and components
        └── tasks.md         # Implementation checklist
```

## Features Demonstrated

- **API-only preset** - Guardrails optimized for API services
- **Custom guardrails** - Example of overriding default guardrails
- **Go-specific patterns** - Service layer, error handling, testing
- **AGENT.md** - AI assistant instructions for Go development

## Getting Started

1. Review the spec in `.ldf/specs/data-pipeline/`
2. See `AGENT.md` for development guidelines
3. Use `ldf lint data-pipeline` to validate the spec

## Related

- [Python FastAPI Example](../python-fastapi/)
- [TypeScript Node Example](../typescript-node/)
- [LDF Documentation](../../docs/)
