from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Tour
from .utils.chunker import create_and_save_chunks

@receiver(post_save, sender=Tour)
def handle_tour_save(sender, instance, **kwargs):
    create_and_save_chunks(instance)

@receiver(post_delete, sender=Tour)
def handle_tour_delete(sender, instance, **kwargs):
    # وقتی تور پاک شد، چانک‌ها هم به خاطر ForeignKey پاک میشن
    pass
