from django.core.management.base import BaseCommand
from tours.models import Chunk, ChunkEmbedding

class Command(BaseCommand):
    help = "❌ حذف تمام چانک‌ها و امبدینگ‌ها"

    def handle(self, *args, **kwargs):
        ChunkEmbedding.objects.all().delete()
        Chunk.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✅ همه چانک‌ها و امبدینگ‌ها حذف شدند"))
