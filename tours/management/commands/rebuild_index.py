# tours/management/command/rebuild_index.py


from django.core.management.base import BaseCommand
from tours.utils.chunker import create_and_save_chunks, create_faq_chunks
from tours.utils.embedder import rebuild_tour_index, rebuild_faq_index
from tours.models import Chunk, ChunkEmbedding, FAQChunk, FAQChunkEmbedding, Tour, FAQ

class Command(BaseCommand):
    help = "بازسازی ایندکس‌ها: تور و FAQ"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tour", action="store_true", help="بازسازی ایندکس تور"
        )
        parser.add_argument(
            "--faq", action="store_true", help="بازسازی ایندکس FAQ"
        )

    def handle(self, *args, **options):
        if options["tour"]:
            rebuild_tour_index()
        if options["faq"]:
            rebuild_faq_index()
        if not options["tour"] and not options["faq"]:
            self.stdout.write("⚠️ هیچ گزینه‌ای مشخص نشده، لطفا --tour یا --faq را اضافه کنید.")


# نحوه استفاده

# # بازسازی ایندکس تور
# python manage.py rebuild_index --tour

# # بازسازی ایندکس FAQ
# python manage.py rebuild_index --faq

# # بازسازی هر دو
# python manage.py rebuild_index --tour --faq