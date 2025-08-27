# tours/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Tour, Chunk, ChunkEmbedding
from .utils.chunker import create_and_save_chunks
from .utils import embedder

@receiver(post_save, sender=Tour)
def handle_tour_save(sender, instance, **kwargs):
    # حذف چانک‌ها و embedding‌های قبلی تور
    ChunkEmbedding.objects.filter(chunk__tour=instance).delete()
    Chunk.objects.filter(tour=instance).delete()

    # ایجاد چانک‌های جدید
    create_and_save_chunks(instance)

    # ساخت embedding‌ها و ایندکس جدید
    embedder.rebuild_index()


@receiver(post_delete, sender=Tour)
def handle_tour_delete(sender, instance, **kwargs):
    # حذف embedding‌های مرتبط (چانک‌ها خودبه‌خود حذف می‌شن)
    ChunkEmbedding.objects.filter(chunk__tour=instance).delete()

    # بازسازی ایندکس بعد از حذف
    embedder.rebuild_index()