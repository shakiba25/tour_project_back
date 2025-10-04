# tours/management/commands/populate_FAQ.py
import os
import sys
import django
import json
import requests

# مسیر پروژه
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# تنظیمات Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")
django.setup()


import json
from django.core.management.base import BaseCommand
from tours.models import FAQ, FAQChunk


class Command(BaseCommand):
    help = "Import FAQs from a JSON file and create FAQ and FAQChunk entries"



    def handle(self, *args, **options):
        file_path =file_path = r"C:\Users\Asus\Desktop\tour_project\back\tours\FAQ.json"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                faqs = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"خطا در باز کردن فایل JSON: {e}"))
            return

        count = 0
        for item in faqs:
            question = item.get("question")
            answer = item.get("answer")
            if not question or not answer:
                continue

            # ایجاد یا بروزرسانی FAQ
            faq_obj, created = FAQ.objects.update_or_create(
                question=question,
                defaults={"answer": answer}
            )

            count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ {count} FAQ  با موفقیت وارد شدند."))
