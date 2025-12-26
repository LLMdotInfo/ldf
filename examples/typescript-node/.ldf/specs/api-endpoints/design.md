# api-endpoints - Design

## Architecture Overview

```
┌─────────────┐     ┌──────────────────────────────────────┐
│   Client    │────▶│          Express Application         │
└─────────────┘     │  ┌──────────┐    ┌───────────────┐   │
                    │  │  Router  │───▶│  TaskService  │   │
                    │  └──────────┘    └───────────────┘   │
                    │       │                 │            │
                    │       ▼                 ▼            │
                    │  ┌──────────┐    ┌───────────────┐   │
                    │  │   Auth   │    │    Prisma     │   │
                    │  │Middleware│    │    Client     │   │
                    │  └──────────┘    └───────────────┘   │
                    └─────────────────────────│────────────┘
                                              ▼
                                    ┌───────────────┐
                                    │  PostgreSQL   │
                                    └───────────────┘
```

## S1: Data Layer

### S1.1: Prisma Schema

```prisma
model Task {
  id          String    @id @default(uuid())
  userId      String    @map("user_id")
  title       String    @db.VarChar(200)
  description String?   @db.VarChar(2000)
  status      TaskStatus @default(PENDING)
  dueDate     DateTime? @map("due_date")
  createdAt   DateTime  @default(now()) @map("created_at")
  updatedAt   DateTime  @updatedAt @map("updated_at")

  @@index([userId, status])
  @@index([userId, dueDate])
  @@map("tasks")
}

enum TaskStatus {
  PENDING
  COMPLETED
  ARCHIVED
}
```

### S1.2: Migrations

Prisma migrations in `prisma/migrations/`:
- `001_init` - Create tasks table with indexes

## S2: Security Layer

### S2.1: Auth Middleware

```typescript
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

export interface AuthRequest extends Request {
  userId: string;
}

export const authMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const token = req.headers.authorization?.replace('Bearer ', '');

  if (!token) {
    return res.status(401).json({
      error: { code: 'UNAUTHORIZED', message: 'Missing token' }
    });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { sub: string };
    (req as AuthRequest).userId = decoded.sub;
    next();
  } catch {
    return res.status(401).json({
      error: { code: 'UNAUTHORIZED', message: 'Invalid token' }
    });
  }
};
```

### S2.2: Input Validation

```typescript
import { z } from 'zod';

export const createTaskSchema = z.object({
  title: z.string().min(1).max(200),
  description: z.string().max(2000).optional(),
  dueDate: z.string().datetime().optional().refine(
    (date) => !date || new Date(date) > new Date(),
    { message: 'Due date must be in the future' }
  ),
});

export const updateTaskSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  description: z.string().max(2000).optional(),
  status: z.enum(['PENDING', 'COMPLETED', 'ARCHIVED']).optional(),
  dueDate: z.string().datetime().nullable().optional(),
});

export const listTasksSchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  pageSize: z.coerce.number().int().min(1).max(100).default(20),
  status: z.enum(['PENDING', 'COMPLETED', 'ARCHIVED']).optional(),
  dueBefore: z.string().datetime().optional(),
  dueAfter: z.string().datetime().optional(),
});
```

## S3: Service Layer

### S3.1: API Routes

```typescript
import { Router } from 'express';
import { TaskService } from './task.service';
import { authMiddleware, AuthRequest } from './auth.middleware';
import { validate } from './validate.middleware';
import { createTaskSchema, updateTaskSchema, listTasksSchema } from './schemas';

const router = Router();
const taskService = new TaskService();

router.use(authMiddleware);

router.get('/', validate(listTasksSchema, 'query'), async (req: AuthRequest, res) => {
  const { page, pageSize, status, dueBefore, dueAfter } = req.query;
  const result = await taskService.list(req.userId, {
    page: Number(page),
    pageSize: Number(pageSize),
    status: status as string,
    dueBefore: dueBefore as string,
    dueAfter: dueAfter as string,
  });
  res.json(result);
});

router.post('/', validate(createTaskSchema, 'body'), async (req: AuthRequest, res) => {
  const task = await taskService.create(req.userId, req.body);
  res.status(201).json(task);
});

router.put('/:id', validate(updateTaskSchema, 'body'), async (req: AuthRequest, res) => {
  const task = await taskService.update(req.userId, req.params.id, req.body);
  res.json(task);
});

router.delete('/:id', async (req: AuthRequest, res) => {
  await taskService.delete(req.userId, req.params.id);
  res.status(204).send();
});

export { router as taskRouter };
```

### S3.2: TaskService

```typescript
import { PrismaClient, TaskStatus } from '@prisma/client';

interface ListOptions {
  page: number;
  pageSize: number;
  status?: string;
  dueBefore?: string;
  dueAfter?: string;
}

export class TaskService {
  constructor(private prisma = new PrismaClient()) {}

  async list(userId: string, options: ListOptions) {
    const { page, pageSize, status, dueBefore, dueAfter } = options;
    const skip = (page - 1) * pageSize;

    const where = {
      userId,
      ...(status && { status: status as TaskStatus }),
      ...(dueBefore && { dueDate: { lte: new Date(dueBefore) } }),
      ...(dueAfter && { dueDate: { gte: new Date(dueAfter) } }),
    };

    const [tasks, total] = await Promise.all([
      this.prisma.task.findMany({
        where,
        skip,
        take: pageSize,
        orderBy: { createdAt: 'desc' },
      }),
      this.prisma.task.count({ where }),
    ]);

    return {
      data: tasks,
      pagination: {
        page,
        pageSize,
        total,
        totalPages: Math.ceil(total / pageSize),
      },
    };
  }

  async create(userId: string, data: { title: string; description?: string; dueDate?: string }) {
    return this.prisma.task.create({
      data: {
        userId,
        title: data.title,
        description: data.description,
        dueDate: data.dueDate ? new Date(data.dueDate) : null,
      },
    });
  }

  async update(userId: string, id: string, data: Partial<{ title: string; description: string; status: TaskStatus; dueDate: string | null }>) {
    const task = await this.prisma.task.findFirst({ where: { id, userId } });
    if (!task) throw new NotFoundError('Task not found');

    return this.prisma.task.update({
      where: { id },
      data: {
        ...data,
        dueDate: data.dueDate === null ? null : data.dueDate ? new Date(data.dueDate) : undefined,
      },
    });
  }

  async delete(userId: string, id: string) {
    const task = await this.prisma.task.findFirst({ where: { id, userId } });
    if (!task) throw new NotFoundError('Task not found');

    await this.prisma.task.delete({ where: { id } });
  }
}
```

### S3.3: Logging

```typescript
import winston from 'winston';

export const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
  ],
});

// Request logging middleware
export const requestLogger = (req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  res.on('finish', () => {
    logger.info({
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration: Date.now() - start,
      userId: (req as AuthRequest).userId,
    });
  });
  next();
};
```

## S4: Testing Strategy

### S4.1: Test Structure

```
tests/
├── unit/
│   └── task.service.test.ts
├── integration/
│   └── task.routes.test.ts
└── setup.ts
```

### S4.2: API Documentation

OpenAPI spec generated with `swagger-jsdoc`:
- All endpoints documented
- Request/response schemas
- Error responses

## Guardrail Mapping

| Guardrail | Implementation | Section |
|-----------|---------------|---------|
| 1. Testing | Unit + Integration tests | S4.1 |
| 2. Security | JWT auth, ownership check | S2.1 |
| 3. Error Handling | Custom errors, consistent format | S3.2 |
| 4. Logging | Winston structured logging | S3.3 |
| 5. API Design | RESTful, pagination | S3.1 |
| 6. Data Validation | Zod schemas | S2.2 |
| 7. Database Migrations | Prisma migrations | S1.2 |
| 8. Documentation | OpenAPI/Swagger | S4.2 |
