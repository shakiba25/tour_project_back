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

from tours.models import Tour, Hotel, FlightInfo, Service, ItineraryItem, Image

# فایل JSON
json_file = os.path.join(os.path.dirname(__file__), "t.json")
with open(json_file, "r", encoding="utf-8") as f:
    tours_data = json.load(f)

# مسیر ذخیره تصاویر
MEDIA_DIR = os.path.join(BASE_DIR, "media", "tours", "images")
os.makedirs(MEDIA_DIR, exist_ok=True)

for t in tours_data:
    print(f"در حال اضافه کردن: {t['name']}")

    # ===== FlightInfo =====
    dep, _ = FlightInfo.objects.get_or_create(
        date=t["departure"]["date"],
        time=t["departure"]["time"],
        airline=t["departure"]["airline"],
    )
    ret, _ = FlightInfo.objects.get_or_create(
        date=t["return"]["date"],
        time=t["return"]["time"],
        airline=t["return"]["airline"],
    )

    # ===== Hotel =====
    hotel, _ = Hotel.objects.get_or_create(
        name=t["hotel"]["name"],
        star=int(t["hotel"]["star"])
    )

    # ===== Tour =====
    tour, created = Tour.objects.get_or_create(
        tour_id=t["tour_id"],
        defaults={
            "name": t["name"],
            "destination": t["destination"],
            "destination_type": t.get("destination_type", None),
            "duration_days": t["duration_days"],
            "price": t["price"],
            "departure": dep,
            "return_info": ret,
            "hotel": hotel,
            "insurance_included": t.get("insurance_included", False),
            "rich_text": t.get("rich_text", ""),
        }
    )

    if created:
        # ===== Services =====
        for s in t.get("services", []):
            service, _ = Service.objects.get_or_create(name=s.strip())
            tour.services.add(service)

        # ===== Itinerary =====
        for it in t.get("itinerary", []):
            item, _ = ItineraryItem.objects.get_or_create(description=it.strip())
            tour.itinerary.add(item)

        
        tour.save()
        print(f"{t['name']} با موفقیت اضافه شد.")
    else:
        print(f"{t['name']} قبلاً وجود داشت.")
