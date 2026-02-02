import stripe
from django.conf import settings
from django.db import transaction
from products.models import Product
from users.models import Address
from .models import Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order_with_payment(user, address_id, product_id, quantity=1):
        address = Address.objects.get(id=address_id, user=user)
        product = Product.objects.get(id=product_id)
        
        total_price = product.price * quantity

        order = Order.objects.create(
            user=user,
            address=address,
            total_price=total_price,
            status=Order.PENDING
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )

        intent = stripe.PaymentIntent.create(
            amount=order.amount_in_cents,
            currency='usd',
            metadata={'order_id': str(order.id)}
        )

        order.stripe_payment_intent = intent['id']
        order.save()

        return order, intent['client_secret']