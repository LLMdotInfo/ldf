# TypeScript/Node Example

A complete LDF example using TypeScript and Express.

## Project Structure

```
typescript-node/
├── .ldf/
│   ├── config.yaml
│   └── specs/
│       └── api-endpoints/
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
cd examples/typescript-node
ldf lint api-endpoints
```

## Features Demonstrated

- Complete 3-phase spec for REST API
- Guardrail coverage matrix
- Question-pack answers
- Express/TypeScript patterns

## Stack

- **Runtime:** Node.js 18+
- **Language:** TypeScript 5.0+
- **Framework:** Express
- **Database:** PostgreSQL with Prisma
- **Testing:** Jest with coverage
