# Python/FastAPI Example

A complete LDF example using Python and FastAPI.

## Project Structure

```
python-fastapi/
├── .ldf/
│   ├── config.yaml
│   └── specs/
│       └── user-auth/
│           ├── requirements.md
│           ├── design.md
│           └── tasks.md
├── AGENT.md
├── src/
│   └── (implementation would go here)
└── tests/
    └── (tests would go here)
```

## Quick Start

```bash
cd examples/python-fastapi
ldf lint user-auth
```

## Features Demonstrated

- Complete 3-phase spec (requirements, design, tasks)
- Guardrail coverage matrix
- Question-pack answers
- FastAPI-specific patterns

## Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL with SQLAlchemy
- **Auth:** JWT with bcrypt
- **Testing:** pytest with coverage
