# ecommerce-api - Tasks

**Status:** Ready for Implementation
**Total Tasks:** 16
**Completed:** 0

## Per-Task Guardrail Checklist

**Reference:** `.ldf/guardrails.yaml`

Before implementing each task, verify applicable guardrails:

- [ ] **1. Testing Coverage:** Unit tests for business logic; integration tests for APIs; coverage ≥85%
- [ ] **2. Security Basics:** Input validation; parameterized queries; auth/authz checks; no secrets in code
- [ ] **3. Error Handling:** Consistent error responses; proper exception hierarchy; user-friendly messages
- [ ] **4. Logging & Observability:** Structured logging; correlation IDs; appropriate log levels
- [ ] **5. API Design:** Versioned endpoints (/v1/); pagination; consistent error format
- [ ] **6. Data Validation:** Request schema validation; business rule validation; output sanitization
- [ ] **7. Database Migrations:** Reversible migrations; rollback tested; backfills separate from schema
- [ ] **8. Documentation:** API docs updated; inline comments for complex logic; README current
- [ ] **9. Multi-tenancy:** Vendor isolation enforced at query level
- [ ] **10. Audit Logs:** Order access logged; vendor actions logged

**Mark N/A if not applicable to the task.**

---

## Phase 1: Project Setup

### Task 1.1: Create Django project structure
**Guardrail Checklist:**
- [ ] Testing: pytest-django configured
- [ ] Documentation: README with setup instructions

**Subtasks:**
- [ ] Create Django project with `django-admin startproject`
- [ ] Create `products` app
- [ ] Configure settings (database, JWT, DRF)
- [ ] Set up pytest-django
- [ ] Create `.env.example` for environment variables

### Task 1.2: Configure Django REST Framework
**Guardrail Checklist:**
- [ ] API Design: Pagination configured
- [ ] Security: JWT authentication configured

**Subtasks:**
- [ ] Add DRF to INSTALLED_APPS
- [ ] Configure REST_FRAMEWORK settings
- [ ] Install and configure djangorestframework-simplejwt
- [ ] Configure pagination (cursor-based)
- [ ] Configure authentication classes

### Task 1.3: Create database migrations
**Guardrail Checklist:**
- [ ] Database Migrations: All migrations reversible
- [ ] Database Migrations: Tested rollback

**Subtasks:**
- [ ] Create models (Product, Category, CartItem, Order, OrderItem)
- [ ] Run `makemigrations`
- [ ] Test `migrate` and `migrate --fake-initial`
- [ ] Test `migrate <app> zero` (rollback)

---

## Phase 2: Models and Admin

### Task 2.1: Implement Product and Category models
**Guardrail Checklist:**
- [ ] Testing: Model tests (90% coverage)
- [ ] Data Validation: Field constraints

**Subtasks:**
- [ ] Create Product model with all fields
- [ ] Create Category model
- [ ] Add model methods and properties
- [ ] Write model tests

### Task 2.2: Implement Cart and Order models
**Guardrail Checklist:**
- [ ] Testing: Model tests (90% coverage)
- [ ] Data Validation: Constraints and validators

**Subtasks:**
- [ ] Create CartItem model
- [ ] Create Order and OrderItem models
- [ ] Add computed properties (subtotal)
- [ ] Write model tests

### Task 2.3: Configure Django Admin
**Guardrail Checklist:**
- [ ] Documentation: Admin inline help text

**Subtasks:**
- [ ] Register all models in admin
- [ ] Customize admin list displays
- [ ] Add search and filter options
- [ ] Configure prepopulated fields

---

## Phase 3: Serializers

### Task 3.1: Implement Product serializers
**Guardrail Checklist:**
- [ ] Data Validation: All fields validated
- [ ] Testing: Serializer validation tests

**Subtasks:**
- [ ] Create ProductListSerializer
- [ ] Create ProductDetailSerializer
- [ ] Create ProductCreateSerializer
- [ ] Add custom validators
- [ ] Write serializer tests

### Task 3.2: Implement Cart and Order serializers
**Guardrail Checklist:**
- [ ] Data Validation: Stock validation
- [ ] Testing: Serializer tests

**Subtasks:**
- [ ] Create CartItemSerializer with stock validation
- [ ] Create CartSerializer
- [ ] Create OrderSerializer and CheckoutSerializer
- [ ] Write serializer tests

---

## Phase 4: ViewSets and APIs

### Task 4.1: Implement Product ViewSet
**Guardrail Checklist:**
- [ ] Testing: API tests (90% coverage)
- [ ] Security: Authentication on protected routes
- [ ] API Design: Filtering, search, ordering
- [ ] Multi-tenancy: Vendor can only see their products

**Subtasks:**
- [ ] Create ProductViewSet
- [ ] Implement list, retrieve, create, update, destroy
- [ ] Add filtering (category, vendor, price range)
- [ ] Add search (name, description)
- [ ] Add ordering (price, date, name)
- [ ] Write API tests

### Task 4.2: Implement Cart ViewSet
**Guardrail Checklist:**
- [ ] Testing: API tests (90% coverage)
- [ ] Security: User can only access their cart
- [ ] Error Handling: Stock validation errors

**Subtasks:**
- [ ] Create CartViewSet
- [ ] Implement list (get cart)
- [ ] Implement create (add to cart)
- [ ] Implement update (update quantity)
- [ ] Implement destroy (remove from cart)
- [ ] Write API tests

### Task 4.3: Implement Order ViewSet
**Guardrail Checklist:**
- [ ] Testing: API tests (90% coverage)
- [ ] Security: User can only see their orders
- [ ] Audit Logs: Log order access

**Subtasks:**
- [ ] Create OrderViewSet
- [ ] Implement list (order history)
- [ ] Implement retrieve (order details)
- [ ] Add order status filtering
- [ ] Write API tests

---

## Phase 5: Business Logic

### Task 5.1: Implement Checkout Service
**Guardrail Checklist:**
- [ ] Testing: Service tests (95% coverage)
- [ ] Security: Stock validation
- [ ] Error Handling: Transaction rollback on failure
- [ ] Audit Logs: Log checkout attempts

**Subtasks:**
- [ ] Create CheckoutService class
- [ ] Implement `process_checkout()` with transaction
- [ ] Validate stock availability
- [ ] Create order and order items
- [ ] Update product stock quantities
- [ ] Clear cart after successful checkout
- [ ] Write comprehensive service tests

### Task 5.2: Add checkout endpoint
**Guardrail Checklist:**
- [ ] Testing: E2E checkout tests (95% coverage)
- [ ] Security: Authentication required
- [ ] Error Handling: Clear error messages

**Subtasks:**
- [ ] Add `@action` for checkout in CartViewSet
- [ ] Integrate CheckoutService
- [ ] Handle checkout errors
- [ ] Write E2E tests (browse → add to cart → checkout)

---

## Phase 6: Permissions and Security

### Task 6.1: Implement custom permissions
**Guardrail Checklist:**
- [ ] Security: Vendor can only modify their products
- [ ] Security: Users can only access their orders
- [ ] Testing: Permission tests

**Subtasks:**
- [ ] Create IsVendorOrReadOnly permission
- [ ] Create IsOrderOwner permission
- [ ] Apply permissions to viewsets
- [ ] Write permission tests

### Task 6.2: Add rate limiting
**Guardrail Checklist:**
- [ ] Security: Rate limits on write operations
- [ ] Testing: Rate limit tests

**Subtasks:**
- [ ] Install django-ratelimit
- [ ] Add rate limiting to checkout
- [ ] Add rate limiting to product creation
- [ ] Write rate limit tests

---

## Phase 7: Documentation and Polish

### Task 7.1: Generate API documentation
**Guardrail Checklist:**
- [ ] Documentation: All endpoints documented
- [ ] Documentation: Request/response examples

**Subtasks:**
- [ ] Install drf-spectacular
- [ ] Configure OpenAPI schema
- [ ] Add docstrings to viewsets
- [ ] Generate Swagger/ReDoc UI
- [ ] Add authentication examples

### Task 7.2: Write comprehensive tests
**Guardrail Checklist:**
- [ ] Testing: Overall coverage ≥85%
- [ ] Testing: Models coverage ≥90%
- [ ] Testing: API coverage ≥90%
- [ ] Testing: Critical paths ≥95%

**Subtasks:**
- [ ] Review and fill coverage gaps
- [ ] Add edge case tests
- [ ] Add E2E workflow tests
- [ ] Run coverage report

### Task 7.3: Update documentation
**Guardrail Checklist:**
- [ ] Documentation: Setup instructions complete
- [ ] Documentation: API usage examples

**Subtasks:**
- [ ] Update README with installation
- [ ] Add database setup instructions
- [ ] Add development server instructions
- [ ] Add testing instructions
- [ ] Document environment variables

---

## Phase 8: Final Validation

### Task 8.1: Manual testing
**Subtasks:**
- [ ] Test browse → add to cart → checkout flow
- [ ] Test vendor product management
- [ ] Test permission enforcement
- [ ] Test error responses

### Task 8.2: Security review
**Guardrail Checklist:**
- [ ] Security: All auth/authz tested
- [ ] Security: Input validation verified
- [ ] Multi-tenancy: Vendor isolation verified
- [ ] Audit Logs: Critical actions logged

**Subtasks:**
- [ ] Review all authentication points
- [ ] Review all permission checks
- [ ] Verify vendor isolation
- [ ] Test audit logging
- [ ] Check for secrets in code
