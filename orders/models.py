import uuid
from django.db import models
from django.conf import settings
from products.models import Product
from users.models import Address

class Order(models.Model):
    PENDING = 'P'
    COMPLETED = 'C'  # سنستخدمها عند نجاح الدفع
    SHIPPED = 'S'
    CANCELLED = 'X'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (SHIPPED, 'Shipped'),
        (CANCELLED, 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    stripe_payment_intent = models.CharField(max_length=200, blank=True, null=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"

    @property
    def amount_in_cents(self):
        return int(self.total_price * 100)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"