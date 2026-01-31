from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
from .tasks import rebuild_ai_index_task

@receiver(post_save, sender=Product)
def trigger_ai_update_on_save(sender, instance, created, **kwargs):
    if instance.is_active:
        rebuild_ai_index_task.delay()

@receiver(post_delete, sender=Product)
def trigger_ai_update_on_delete(sender, instance, **kwargs):
    rebuild_ai_index_task.delay()