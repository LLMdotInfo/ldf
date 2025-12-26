# Python/Django Example

A complete LDF example using Python and Django REST Framework.

## Project Structure

```
python-django/
├── .ldf/
│   ├── config.yaml
│   └── specs/
│       └── ecommerce-api/
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
cd examples/python-django
ldf lint ecommerce-api
```

## Features Demonstrated

- Complete 3-phase spec (requirements, design, tasks)
- Guardrail coverage matrix
- Question-pack answers
- Django-specific patterns (Models, Views, Serializers, Admin)

## Stack

- **Framework:** Django 5.0+ with Django REST Framework
- **Database:** PostgreSQL with Django ORM
- **Auth:** Token authentication with django-rest-framework-simplejwt
- **Testing:** pytest-django with coverage
- **Validation:** DRF Serializers with custom validators
