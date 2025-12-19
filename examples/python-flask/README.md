# Python/Flask Example

A complete LDF example using Python and Flask.

## Project Structure

```
python-flask/
├── .ldf/
│   ├── config.yaml
│   └── specs/
│       └── blog-api/
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
cd examples/python-flask
ldf lint blog-api
```

## Features Demonstrated

- Complete 3-phase spec (requirements, design, tasks)
- Guardrail coverage matrix
- Question-pack answers
- Flask-specific patterns (Blueprints, SQLAlchemy)

## Stack

- **Framework:** Flask 3.0+
- **Database:** PostgreSQL with SQLAlchemy
- **Auth:** JWT with Flask-JWT-Extended
- **Testing:** pytest with coverage
- **Validation:** Flask-Marshmallow
