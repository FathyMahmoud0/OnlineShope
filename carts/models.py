import uuid
from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.email}"

    @property
    def total_price(self):
        return sum(item.cost for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = [['cart', 'product']] # يمنع تكرار المنتج في نفس السلة
        ordering = ['id']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def cost(self):
        price = self.product.discount_price if self.product.discount_price else self.product.price
        return price * self.quantity