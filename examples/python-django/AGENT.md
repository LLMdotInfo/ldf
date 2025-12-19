# E-commerce API - Development Guide

## Project Overview

**Name:** E-commerce API Service
**Purpose:** Multi-vendor marketplace API with product catalog, cart, and checkout
**Stack:** Python 3.10+ with Django 5.0+, Django REST Framework, PostgreSQL

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
├── manage.py
├── config/                   # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── products/                 # Main app
│   ├── __init__.py
│   ├── models.py            # Django ORM models
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # ViewSets
│   ├── permissions.py       # Custom permissions
│   ├── services.py          # Business logic
│   ├── admin.py             # Django admin
│   └── urls.py
└── tests/
    ├── test_models.py
    ├── test_serializers.py
    ├── test_views.py
    └── test_services.py
```

### Django Model Pattern

```python
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['vendor']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def in_stock(self):
        return self.stock_quantity > 0
```

### DRF Serializer Pattern

```python
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.username', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'vendor_name', 'in_stock']
        read_only_fields = ['slug', 'created_at']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value
```

### ViewSet Pattern

```python
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'vendor']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        # Add business logic filtering
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs
    
    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)
    
    @action(detail=True, methods=['post'])
    def custom_action(self, request, pk=None):
        obj = self.get_object()
        # Custom logic
        return Response({'status': 'success'})
```

### Service Layer Pattern

```python
from django.db import transaction

class CheckoutService:
    @transaction.atomic
    def process_checkout(self, user, data):
        """
        Process cart checkout with stock validation and order creation.
        All operations are wrapped in a transaction.
        """
        cart_items = CartItem.objects.filter(user=user)
        
        # Validate stock
        for item in cart_items:
            if item.quantity > item.product.stock_quantity:
                raise ValidationError(f"Insufficient stock for {item.product.name}")
        
        # Create order
        order = Order.objects.create(...)
        
        # Create order items and update stock
        for item in cart_items:
            OrderItem.objects.create(...)
            item.product.stock_quantity -= item.quantity
            item.product.save()
        
        # Clear cart
        cart_items.delete()
        
        return order
```

### Custom Permissions

```python
from rest_framework import permissions

class IsVendorOrReadOnly(permissions.BasePermission):
    """
    Vendors can only modify their own products.
    Read access is public.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.vendor == request.user
```

## Testing Standards

### Coverage Requirements
- Overall: 85%
- Models: 90%
- ViewSets/Serializers: 90%
- Critical paths (checkout, inventory): 95%

### Test Structure

```python
from django.test import TestCase
from rest_framework.test import APITestCase
import pytest

# Model Tests
class ProductModelTest(TestCase):
    def test_in_stock_property(self):
        product = Product.objects.create(
            name="Test Product",
            price=10.00,
            stock_quantity=5
        )
        self.assertTrue(product.in_stock)

# API Tests
class ProductAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.com', 'password')
        self.client.force_authenticate(user=self.user)
    
    def test_list_products(self):
        response = self.client.get('/api/v1/products/')
        self.assertEqual(response.status_code, 200)
    
    def test_create_product(self):
        data = {'name': 'New Product', 'price': 20.00}
        response = self.client.post('/api/v1/products/', data)
        self.assertEqual(response.status_code, 201)

# Service Tests
@pytest.mark.django_db
class TestCheckoutService:
    def test_process_checkout_success(self, user, cart_item):
        service = CheckoutService()
        order = service.process_checkout(user, {'shipping_address': '123 Main St'})
        assert order.status == 'pending'
        assert CartItem.objects.filter(user=user).count() == 0
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Or with pytest
pytest

# Run with coverage
pytest --cov=products --cov-report=html

# Run specific test
pytest tests/test_models.py::ProductModelTest::test_in_stock
```

## Database Migrations

### Creating Migrations

```bash
# Create migrations for app
python manage.py makemigrations products

# Apply migrations
python manage.py migrate

# Show migration plan
python manage.py showmigrations

# Rollback to specific migration
python manage.py migrate products 0001

# Create empty migration for data migration
python manage.py makemigrations --empty products
```

### Migration Best Practices

```python
# migrations/0002_add_product_category.py
from django.db import migrations

def forward(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    Category = apps.get_model('products', 'Category')
    # Example: Set default category for existing products
    default_cat = Category.objects.create(name='Uncategorized', slug='uncategorized')
    Product.objects.filter(category__isnull=True).update(category=default_cat)

def backward(apps, schema_editor):
    # Rollback: Remove the default category and clear assignments
    Category = apps.get_model('products', 'Category')
    Category.objects.filter(slug='uncategorized').delete()
    # Products will have NULL category after this (if nullable)

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(forward, backward),
    ]
```

## Django Admin

### Admin Registration

```python
from django.contrib import admin

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'price', 'stock_quantity', 'is_active']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Vendors only see their products
            qs = qs.filter(vendor=request.user)
        return qs
```

## URL Configuration

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import ProductViewSet, CartViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include('rest_framework.urls')),
]
```

## Settings Configuration

```python
# config/settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.CursorPagination',
    'PAGE_SIZE': 24,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

## Commit Message Format

```
type(scope): brief description

- Detailed change 1
- Detailed change 2

Related spec: .ldf/specs/{feature}/tasks.md [Task X.Y]
```

**Types:** feat, fix, refactor, test, docs, chore

## Technology Stack

- **Python 3.10+** - Language
- **Django 5.0+** - Web framework
- **Django REST Framework 3.14+** - API framework
- **PostgreSQL 14+** - Database
- **djangorestframework-simplejwt** - JWT authentication
- **django-filter** - API filtering
- **pytest-django** - Testing
- **drf-spectacular** - OpenAPI documentation

## When to Ask Clarification

**ALWAYS ask before:**
- Writing code without approved spec
- Making architectural decisions not in design.md
- Changing API contracts
- Modifying database schema
- Adding new dependencies

**Can proceed without asking:**
- Following Django/DRF patterns
- Implementing approved tasks
- Writing tests for new code
- Standard Django admin configuration
