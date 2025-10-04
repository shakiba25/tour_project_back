# tours/utils/chunker.py

from ..models import Chunk ,FAQ, FAQChunk

def format_price(price):
    return f"{price:,} تومان"

def create_and_save_chunks(instance):

    Chunk.objects.filter(tour=instance).delete()

    tour = instance
    chunks = []

    combined_name = f"{tour.name} ({tour.destination})"
    
    # --- اطلاعات کلی ---
    general_text = (
        f"{combined_name} یک تور {tour.duration_days} روزه به مقصد {tour.destination}  است "
        f"صفحه ی مربط به این تور <a href='http://localhost:5173/tours/{tour.tour_id}'>{combined_name}</a>"
        f"که با قیمت {format_price(tour.price)}  ارائه می‌شود. "
        f"پرواز رفت در تاریخ {tour.departure.date_jalali.strftime('%d-%m-%Y')} ساعت {tour.departure.time} توسط ایرلاین  "
        f"{tour.departure.airline} انجام می‌شود و بازگشت در تاریخ {tour.return_info.date_jalali.strftime('%d-%m-%Y')} "
        f"ساعت {tour.return_info.time} توسط ایرلاین {tour.return_info.airline} خواهد بود. "
        f"اقامت در هتل {tour.hotel.name} ستاره{tour.hotel.star} می‌باشد."
    )
    chunks.append(("general_info", general_text))

    # --- خدمات ---
    services = tour.services.all()
    if services.exists():
        services_text = f"خدمات {combined_name} شامل:\n- " + "\n- ".join(s.name for s in services)
        chunks.append(("services", services_text))

    # --- برنامه سفر ---
    itinerary = tour.itinerary.all()
    if itinerary.exists():
        itinerary_text = f"برنامه سفر {combined_name}:\n" + "\n".join(i.description for i in itinerary)
        chunks.append(("itinerary", itinerary_text))

    # --- بیمه و توضیحات ---
    insurance_text = (
        f"{combined_name} شامل بیمه مسافرتی می‌باشد." if tour.insurance_included 
        else f"{combined_name} شامل بیمه مسافرتی نمی‌باشد."
    )
    if tour.rich_text:
        insurance_text += f"\نکات  {combined_name} شامل:{tour.rich_text}"
    chunks.append(("insurance_and_notes", insurance_text))

    # --- ذخیره‌سازی در دیتابیس ---
    for chunk_type, text in chunks:
        Chunk.objects.create(tour=tour, chunk_type=chunk_type, text=text)

    return chunks

def create_faq_chunks():

    chunks = []
    for faq in FAQ.objects.all():
        combined_text = f"سوال: {faq.question}\nپاسخ: {faq.answer}"
        chunk = FAQChunk.objects.create(faq=faq, text=combined_text)
        chunks.append(chunk)
    return chunks

