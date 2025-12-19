# ecommerce-api - Design

## Architecture Overview

```
┌─────────────┐     ┌──────────────────────────────────────┐
│   Client    │────▶│      Django REST Framework          │
└─────────────┘     │  ┌───────────┐   ┌──────────────┐   │
                    │  │ ViewSets  │──▶│  Serializers │   │
                    │  └───────────┘   └──────────────┘   │
                    │         │               │           │
                    │         ▼               ▼           │
                    │  ┌───────────────────────────────┐  │
                    │  │      Django ORM Models        │  │
                    │  └───────────────────────────────┘  │
                    │                │                    │
                    └────────────────│────────────────────┘
                                     ▼
                           ┌──────────────────┐
                           │   PostgreSQL     │
                           └──────────────────┘
```

## S1: Data Layer

### S1.1: Django Models

#### Product Model

```python
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(unique=True, max_length=250)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['vendor']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-created_at']),
        ]
        permissions = [
            ('can_approve_products', 'Can approve product listings'),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def in_stock(self):
        return self.stock_quantity > 0
```

#### Category Model

```python
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=120)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name
```

#### CartItem Model

```python
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = [['user', 'product']]
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s cart: {self.product.name} x{self.quantity}"
    
    @property
    def subtotal(self):
        return self.product.price * self.quantity
```

#### Order Model

```python
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=32, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"
```

#### OrderItem Model

```python
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
        indexes = [
            models.Index(fields=['order']),
        ]
    
    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity
```

## S2: Serializer Layer

### S2.1: Product Serializers

**Location:** `products/serializers.py`

```python
from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']

class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    vendor_name = serializers.CharField(source='vendor.username', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'stock_quantity', 
                  'category', 'vendor_name', 'in_stock', 'created_at']

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    vendor = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'slug', 'price', 
                  'stock_quantity', 'category', 'vendor', 'is_active', 
                  'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock_quantity', 'category']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative")
        return value
```

### S2.2: Cart Serializers

```python
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, 
                                             decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 
                  'quantity', 'subtotal', 'created_at']
        read_only_fields = ['subtotal']
    
    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity', 1)
        
        if quantity > product.stock_quantity:
            raise serializers.ValidationError(
                f"Only {product.stock_quantity} units available"
            )
        
        if not product.is_active:
            raise serializers.ValidationError("Product is not available")
        
        return data

class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
```

### S2.3: Order Serializers

```python
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 
                  'price_at_purchase', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'status', 'total_amount', 
                  'shipping_address', 'items', 'created_at', 'updated_at']
        read_only_fields = ['order_number', 'status', 'total_amount']

class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(max_length=500)
    payment_method = serializers.ChoiceField(choices=['card', 'paypal'])
```

## S3: ViewSet Layer

### S3.1: Product ViewSet

**Location:** `products/views.py`

```python
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category', 'vendor')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'vendor']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        return ProductDetailSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        return qs
    
    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)
```

### S3.2: Cart ViewSet

```python
class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get current cart"""
        items = CartItem.objects.filter(user=request.user).select_related('product')
        total = sum(item.subtotal for item in items)
        serializer = CartSerializer({
            'items': items,
            'total': total
        })
        return Response(serializer.data)
    
    def create(self, request):
        """Add item to cart"""
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if item already in cart
        product = serializer.validated_data['product']
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': serializer.validated_data['quantity']}
        )
        
        if not created:
            cart_item.quantity += serializer.validated_data['quantity']
            cart_item.save()
        
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Checkout cart"""
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Process checkout (see service layer)
        order = checkout_service.process_checkout(
            request.user,
            serializer.validated_data
        )
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
```

## S4: URL Configuration

**Location:** `urls.py`

```python
from rest_framework.routers import DefaultRouter
from products.views import ProductViewSet, CartViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include('rest_framework.urls')),
]
```

## S5: Business Logic (Service Layer)

### S5.1: Checkout Service

**Location:** `products/services.py`

```python
from django.db import transaction
from decimal import Decimal

class CheckoutService:
    @transaction.atomic
    def process_checkout(self, user, checkout_data):
        # Get cart items
        cart_items = CartItem.objects.filter(user=user).select_related('product')
        
        if not cart_items.exists():
            raise ValidationError("Cart is empty")
        
        # Validate stock
        for item in cart_items:
            if item.quantity > item.product.stock_quantity:
                raise ValidationError(f"Insufficient stock for {item.product.name}")
        
        # Calculate total
        total = sum(item.subtotal for item in cart_items)
        
        # Create order
        order = Order.objects.create(
            order_number=self._generate_order_number(),
            user=user,
            total_amount=total,
            shipping_address=checkout_data['shipping_address'],
            status='pending'
        )
        
        # Create order items and update stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )
            
            # Update stock
            item.product.stock_quantity -= item.quantity
            item.product.save()
        
        # Clear cart
        cart_items.delete()
        
        # Process payment (mocked)
        self._process_payment(order, checkout_data['payment_method'])
        
        return order
    
    def _generate_order_number(self):
        import uuid
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    def _process_payment(self, order, payment_method):
        # Mock payment processing
        # In production, integrate with Stripe/PayPal
        pass

checkout_service = CheckoutService()
```

## S6: Permissions

**Location:** `products/permissions.py`

```python
from rest_framework import permissions

class IsVendorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Vendor can only modify their own products
        return obj.vendor == request.user

class IsOrderOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
```

## S7: Testing Strategy

### S7.1: Model Tests

```python
from django.test import TestCase

class ProductModelTest(TestCase):
    def test_in_stock_property(self):
        product = Product(stock_quantity=5)
        self.assertTrue(product.in_stock)
        
        product.stock_quantity = 0
        self.assertFalse(product.in_stock)
```

### S7.2: API Tests

```python
from rest_framework.test import APITestCase

class ProductAPITest(APITestCase):
    def test_list_products(self):
        response = self.client.get('/api/v1/products/')
        self.assertEqual(response.status_code, 200)
    
    def test_create_product_authenticated(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.post('/api/v1/products/', data={...})
        self.assertEqual(response.status_code, 201)
```

## S8: Admin Configuration

**Location:** `products/admin.py`

```python
from django.contrib import admin

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'price', 'stock_quantity', 'is_active']
    list_filter = ['is_active', 'category', 'vendor']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
```
