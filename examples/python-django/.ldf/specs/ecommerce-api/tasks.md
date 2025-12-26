# ecommerce-api - Tasks

**Status:** Ready for Implementation

## Per-Task Guardrail Checklist

**Reference:** `.ldf/guardrails.yaml`

Before implementing each task, verify applicable guardrails:

- [ ] **1. Testing Coverage:** Unit tests for business logic; integration tests for APIs; coverage ≥85%
- [ ] **2. Security Basics:** Input validation; parameterized queries; auth/authz checks
- [ ] **3. Error Handling:** Consistent error responses; proper exception hierarchy
- [ ] **4. Logging & Observability:** Structured logging; correlation IDs
- [ ] **5. API Design:** Versioned endpoints (/v1/); pagination; consistent error format
- [ ] **6. Data Validation:** Request schema validation; business rule validation
- [ ] **7. Database Migrations:** Reversible migrations; rollback tested
- [ ] **8. Documentation:** API docs updated; README current
- [ ] **9. Multi-tenancy:** Vendor isolation enforced at query level
- [ ] **10. Audit Logs:** Order access logged; vendor actions logged

---

## Phase 1: Project Setup

- [ ] **Task 1.1:** Create Django project structure
  - [ ] Create Django project with `django-admin startproject`
  - [ ] Create `products` app
  - [ ] Configure settings (database, JWT, DRF)
  - [ ] Set up pytest-django

- [ ] **Task 1.2:** Configure Django REST Framework
  - [ ] Add DRF to INSTALLED_APPS
  - [ ] Configure JWT authentication
  - [ ] Configure cursor-based pagination

- [ ] **Task 1.3:** Create database migrations
  - [ ] Create models (Product, Category, CartItem, Order, OrderItem)
  - [ ] Run `makemigrations`
  - [ ] Test migrate and rollback

## Phase 2: Models and Admin

- [ ] **Task 2.1:** Implement Product and Category models
  - [ ] Create Product model with all fields
  - [ ] Create Category model
  - [ ] Write model tests (90% coverage)

- [ ] **Task 2.2:** Implement Cart and Order models
  - [ ] Create CartItem model
  - [ ] Create Order and OrderItem models
  - [ ] Write model tests

- [ ] **Task 2.3:** Configure Django Admin
  - [ ] Register all models in admin
  - [ ] Customize admin list displays
  - [ ] Add search and filter options

## Phase 3: Serializers

- [ ] **Task 3.1:** Implement Product serializers
  - [ ] Create ProductListSerializer, ProductDetailSerializer
  - [ ] Create ProductCreateSerializer with validators
  - [ ] Write serializer tests

- [ ] **Task 3.2:** Implement Cart and Order serializers
  - [ ] Create CartItemSerializer with stock validation
  - [ ] Create OrderSerializer and CheckoutSerializer
  - [ ] Write serializer tests

## Phase 4: ViewSets and APIs

- [ ] **Task 4.1:** Implement Product ViewSet
  - [ ] Create ProductViewSet with CRUD operations
  - [ ] Add filtering, search, ordering
  - [ ] Enforce vendor isolation
  - [ ] Write API tests (90% coverage)

- [ ] **Task 4.2:** Implement Cart ViewSet
  - [ ] Create CartViewSet with add/update/remove
  - [ ] User can only access their cart
  - [ ] Write API tests

- [ ] **Task 4.3:** Implement Order ViewSet
  - [ ] Create OrderViewSet with list/retrieve
  - [ ] User can only see their orders
  - [ ] Log order access
  - [ ] Write API tests

## Phase 5: Business Logic

- [ ] **Task 5.1:** Implement Checkout Service
  - [ ] Create CheckoutService class
  - [ ] Implement `process_checkout()` with transaction
  - [ ] Validate stock, create order, update quantities
  - [ ] Write service tests (95% coverage)

- [ ] **Task 5.2:** Add checkout endpoint
  - [ ] Add `@action` for checkout in CartViewSet
  - [ ] Handle checkout errors
  - [ ] Write E2E tests

## Phase 6: Permissions and Security

- [ ] **Task 6.1:** Implement custom permissions
  - [ ] Create IsVendorOrReadOnly permission
  - [ ] Create IsOrderOwner permission
  - [ ] Write permission tests

- [ ] **Task 6.2:** Add rate limiting
  - [ ] Install django-ratelimit
  - [ ] Add rate limiting to checkout and product creation
  - [ ] Write rate limit tests

## Phase 7: Documentation and Polish

- [ ] **Task 7.1:** Generate API documentation
  - [ ] Install drf-spectacular
  - [ ] Configure OpenAPI schema
  - [ ] Generate Swagger/ReDoc UI

- [ ] **Task 7.2:** Write comprehensive tests
  - [ ] Achieve overall coverage ≥85%
  - [ ] Add E2E workflow tests

- [ ] **Task 7.3:** Update documentation
  - [ ] Update README with setup instructions
  - [ ] Document environment variables

## Completion Checklist

- [ ] All tasks completed
- [ ] All tests passing
- [ ] Coverage meets thresholds
- [ ] Documentation complete
- [ ] Vendor isolation verified
- [ ] Code reviewed
