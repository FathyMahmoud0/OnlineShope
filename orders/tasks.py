from celery import shared_task
from .models import Order

@shared_task
def confirm_order_payment(order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.status = Order.COMPLETED
        order.save()
        return f"Order {order.id} set to COMPLETED"
    except Order.DoesNotExist:
        return f"Order {order_id} not found"