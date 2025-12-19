# LDF Example Template Recommendations

## Executive Summary

This document proposes 5 additional example templates to expand the LDF framework examples from 5 to 10 total. The recommendations prioritize:

1. **Language Diversity** - Covering popular languages in modern development
2. **Use Case Variety** - Different domains and architectural patterns
3. **Framework Popularity** - Widely-adopted frameworks with strong communities
4. **Complementary Coverage** - Filling gaps not covered by existing examples

## Current Examples (5)

| # | Language | Framework | Use Case | Key Features |
|---|----------|-----------|----------|--------------|
| 1 | Python | FastAPI | User Authentication | JWT, MFA, async |
| 2 | Python | Flask | Blog API | REST, SQLAlchemy, Blueprints |
| 3 | Python | Django | E-commerce API | DRF, multi-tenancy, marketplace |
| 4 | TypeScript | Express/Node | REST API | Prisma, validation, middleware |
| 5 | Go | Chi Router | Data Pipeline | Service layer, concurrent processing |

## Recommended Additional Examples (5)

### 1. Rust with Actix-Web - Real-time WebSocket Service

**Rationale:**
- **Language Gap:** Rust is increasingly popular for systems programming and high-performance services
- **Framework:** Actix-Web is the most popular Rust web framework (async, high performance)
- **Use Case:** Real-time chat/notification service showcases Rust's strengths
- **Unique Features:** WebSocket support, async/await, zero-cost abstractions, memory safety

**Spec Focus:**
- Real-time WebSocket connections
- Message broadcasting and rooms
- Connection pooling and state management
- Performance optimization patterns

**Complexity:** Medium-High
**Target Audience:** Developers building high-performance, concurrent systems

---

### 2. Java with Spring Boot - Microservices API

**Rationale:**
- **Language Gap:** Java is widely used in enterprise environments
- **Framework:** Spring Boot is the de facto standard for Java web services
- **Use Case:** Microservice with service discovery, circuit breakers, and distributed tracing
- **Unique Features:** Dependency injection, Spring Data JPA, actuator health checks

**Spec Focus:**
- RESTful microservice with Spring Data
- Service-to-service communication
- Health checks and metrics (Actuator)
- Database migrations with Flyway/Liquibase
- Testing with JUnit 5 and MockMvc

**Complexity:** Medium-High
**Target Audience:** Enterprise developers, microservices architects

---

### 3. Ruby with Rails - Content Management System (CMS)

**Rationale:**
- **Language Gap:** Ruby on Rails pioneered many web development patterns
- **Framework:** Rails is still widely used, especially for rapid prototyping
- **Use Case:** CMS with admin panel, content versioning, and media management
- **Unique Features:** Active Record ORM, Rails generators, convention over configuration

**Spec Focus:**
- CRUD operations with Active Record
- Admin interface with Active Admin or Rails Admin
- File uploads with Active Storage
- Background jobs with Sidekiq
- Content versioning with PaperTrail

**Complexity:** Medium
**Target Audience:** Full-stack developers, startups building MVPs

---

### 4. C# with ASP.NET Core - GraphQL API

**Rationale:**
- **Language Gap:** C# and .NET are major players in enterprise development
- **Framework:** ASP.NET Core is modern, cross-platform, and performant
- **Use Case:** GraphQL API showcases modern API design beyond REST
- **Unique Features:** Strong typing, Entity Framework Core, LINQ queries

**Spec Focus:**
- GraphQL schema design with Hot Chocolate
- Query optimization and DataLoader
- Entity Framework Core with migrations
- Authentication with IdentityServer
- Unit testing with xUnit

**Complexity:** Medium-High
**Target Audience:** .NET developers, teams moving from REST to GraphQL

---

### 5. PHP with Laravel - Multi-tenant SaaS Application

**Rationale:**
- **Language Gap:** PHP powers a significant portion of the web (WordPress, etc.)
- **Framework:** Laravel is the most popular modern PHP framework
- **Use Case:** Multi-tenant SaaS with subscription billing and tenant isolation
- **Unique Features:** Eloquent ORM, artisan CLI, queue workers, Laravel Cashier

**Spec Focus:**
- Multi-tenancy with tenant databases
- Subscription billing with Laravel Cashier (Stripe)
- Queue jobs with Laravel Queues
- API authentication with Laravel Sanctum
- Testing with PHPUnit and Laravel Dusk

**Complexity:** High
**Target Audience:** SaaS developers, teams building B2B platforms

---

## Alternative Considerations

The following were considered but not selected for the initial 10:

### Honorable Mentions

1. **Elixir with Phoenix** - Excellent for real-time features, but smaller community
2. **Kotlin with Ktor** - Growing in Android space, but less web adoption
3. **Swift with Vapor** - iOS-centric, smaller server-side adoption
4. **Scala with Play Framework** - Powerful but niche audience
5. **Haskell with Servant** - Type-safe APIs, but steep learning curve

### Why Not Included (Yet)

- **Node.js with NestJS:** Too similar to existing Express example
- **Python with Tornado:** Async support now in FastAPI
- **Go with Gin:** Similar to existing Chi example
- **React/Vue/Angular:** Frontend frameworks - LDF focuses on backend specs

---

## Implementation Priority

### Phase 1 (High Priority)
1. **Java with Spring Boot** - Largest enterprise audience
2. **Ruby with Rails** - Rapid prototyping use case

### Phase 2 (Medium Priority)
3. **C# with ASP.NET Core** - GraphQL pattern coverage
4. **Rust with Actix-Web** - Performance-critical systems

### Phase 3 (Lower Priority)
5. **PHP with Laravel** - SaaS-specific patterns

---

## Template Structure for Each Example

Each example will follow the established pattern:

```
{language}-{framework}/
├── .ldf/
│   ├── config.yaml           # LDF configuration with appropriate preset
│   └── specs/
│       └── {feature-name}/
│           ├── requirements.md  # User stories, question-pack answers
│           ├── design.md        # Architecture, data models, APIs
│           └── tasks.md         # Implementation checklist
├── AGENT.md                  # AI assistant development guide
└── README.md                 # Quick start and stack overview
```

---

## Success Metrics

### Coverage Goals
- **Languages:** 7 different languages (Python, TypeScript, Go, Rust, Java, Ruby, C#, PHP)
- **Use Cases:** 10 distinct use cases (auth, blog, e-commerce, pipelines, websockets, microservices, CMS, GraphQL, SaaS)
- **Complexity Range:** Simple (3), Medium (4), High (3)
- **Architecture Patterns:** Monolith, Microservices, Real-time, Multi-tenant

### Quality Standards
All examples must:
- Include complete 3-phase specs (requirements → design → tasks)
- Follow guardrail coverage matrix
- Include AGENT.md with framework-specific patterns
- Pass `ldf lint` validation
- Demonstrate best practices for the framework

---

## Implementation Effort Estimate

### Per Example (Average)
- Research and planning: 2 hours
- Requirements document: 2 hours
- Design document: 3 hours
- Tasks document: 2 hours
- AGENT.md: 1.5 hours
- README and config: 0.5 hours
- **Total per example: ~11 hours**

### Total for 5 Examples
- **Estimated effort: 55 hours**
- **Timeline: 2-3 weeks** (with review cycles)

---

## Community Contribution Path

To scale beyond 10 examples:

1. **Template Generator Tool**
   - CLI command: `ldf init-example --language rust --framework actix`
   - Generates skeleton with prompts for use case details

2. **Community Guidelines**
   - Document contribution process in CONTRIBUTING.md
   - Example submission checklist
   - Review criteria for acceptance

3. **Example Gallery**
   - Website showcasing all examples
   - Filter by language, framework, use case, complexity
   - Direct links to specs and AGENT.md files

---

## Recommendation Summary

The 5 recommended examples provide:

✅ **Language Diversity** - Adds Rust, Java, Ruby, C#, PHP to existing Python/TypeScript/Go
✅ **Enterprise Coverage** - Java Spring Boot and C# ASP.NET for enterprise developers
✅ **Modern Patterns** - GraphQL, WebSockets, microservices, multi-tenancy
✅ **Framework Popularity** - All top-tier frameworks with large communities
✅ **Use Case Variety** - Real-time, CMS, SaaS, microservices complement existing REST/CRUD examples

**Next Step:** Review and approve recommendations before implementation begins.

---

## Questions for Review

1. **Priority Order:** Does the Phase 1/2/3 prioritization align with user needs?
2. **Use Cases:** Are the chosen use cases appropriate for each framework?
3. **Missing Languages:** Any critical languages/frameworks we should include instead?
4. **Complexity Balance:** Is the mix of simple/medium/high complexity appropriate?
5. **Enterprise Focus:** Should we prioritize more enterprise-focused examples (Java, C#)?

---

*Document Version: 1.0*
*Last Updated: 2025-12-19*
*Status: Pending Review*
