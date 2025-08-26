from django.core.management.base import BaseCommand
from tours.models import Tour
from tours.utils.chunker import create_and_save_chunks

class Command(BaseCommand):
    help = "Rebuild chunks for all tours"

    def handle(self, *args, **kwargs):
        for tour in Tour.objects.all():
            create_and_save_chunks(tour)
        self.stdout.write(self.style.SUCCESS("✅ All chunks rebuilt successfully"))
