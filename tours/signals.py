# tours/signals.py
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Tour, Chunk, ChunkEmbedding , FAQ
from .utils.chunker import create_and_save_chunks, create_faq_chunks
from .utils.embedder import rebuild_faq_index , rebuild_tour_index

# @receiver(post_delete, sender=Tour)
# @receiver(post_save, sender=Tour)
# def tour_post_save(sender, instance, created, **kwargs):
#     create_and_save_chunks(instance)
#     rebuild_tour_index()

# @receiver(post_delete, sender=FAQ)
# @receiver(post_save, sender=FAQ)
# def faq_post_save(sender, instance, created, **kwargs):
#     create_faq_chunks()
#     rebuild_faq_index()