# API Endpoints Service - Development Guide

## Project Overview

**Name:** API Endpoints Service
**Purpose:** RESTful API service with TypeScript and Express
**Stack:** Node.js 18+, TypeScript, Express, PostgreSQL, Prisma

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
├── src/
│   ├── index.ts              # App entry point
│   ├── routes/               # Express route handlers
│   ├── controllers/          # Request/response logic
│   ├── services/             # Business logic
│   ├── models/               # Prisma model types
│   ├── middleware/           # Express middleware
│   └── utils/                # Shared utilities
├── prisma/
│   ├── schema.prisma         # Database schema
│   └── migrations/           # Migration files
└── tests/                    # Test suite
```

### Service Layer Pattern

```typescript
// src/services/user.service.ts
export class UserService {
  constructor(private readonly prisma: PrismaClient) {}

  async findById(id: string): Promise<User | null> {
    return this.prisma.user.findUnique({ where: { id } });
  }

  async create(data: CreateUserDto): Promise<User> {
    return this.prisma.user.create({ data });
  }
}
```

### Error Handling

```typescript
// src/utils/errors.ts
export class AppError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public isOperational = true
  ) {
    super(message);
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string) {
    super(404, `${resource} not found`);
  }
}
```

### API Design

```typescript
// src/routes/users.ts
import { Router } from 'express';

const router = Router();

router.get('/', async (req, res, next) => {
  try {
    const users = await userService.findAll(req.query);
    res.json({ data: users });
  } catch (err) {
    next(err);
  }
});

router.post('/', validate(createUserSchema), async (req, res, next) => {
  try {
    const user = await userService.create(req.body);
    res.status(201).json({ data: user });
  } catch (err) {
    next(err);
  }
});

export default router;
```

## Testing Standards

### Coverage Requirements
- Minimum: 80% overall
- Services: 90%
- Controllers: 85%

### Test Structure

```typescript
// tests/services/user.service.test.ts
import { describe, it, expect, beforeEach } from '@jest/globals';
import { UserService } from '../../src/services/user.service';

describe('UserService', () => {
  let userService: UserService;

  beforeEach(() => {
    userService = new UserService(prismaMock);
  });

  describe('findById', () => {
    it('should return user when found', async () => {
      prismaMock.user.findUnique.mockResolvedValue(mockUser);

      const result = await userService.findById('123');

      expect(result).toEqual(mockUser);
    });

    it('should return null when not found', async () => {
      prismaMock.user.findUnique.mockResolvedValue(null);

      const result = await userService.findById('invalid');

      expect(result).toBeNull();
    });
  });
});
```

## Commit Message Format

```
type(scope): brief description

- Detailed change 1
- Detailed change 2

Related spec: .ldf/specs/{feature}/tasks.md [Task X.Y]
```

## Technology Stack

- **Node.js 18+** - Runtime
- **TypeScript 5.0+** - Language
- **Express** - Web framework
- **Prisma** - ORM
- **Zod** - Schema validation
- **Jest** - Testing
- **Winston** - Logging
- **dotenv** - Configuration

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
