import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")

import django
django.setup()

import jdatetime
import datetime
import json
import re
import openai
from tours.models import Tour, Chunk

# --------------------- تنظیم OpenAI --------------------- #
openai.api_key = "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"  # <<-- کلیدت اینجا
openai.api_base = "https://openrouter.ai/api/v1"


# model = "qwen/qwen3-235b-a22b:free"  # محشرهههه
# model = "openrouter/horizon-beta" # اینم عالیه
# model = "deepseek/deepseek-r1-0528:free"
# model = "z-ai/glm-4.5-air:free"
# model = "google/gemma-3n-e4b-it:free"
# model = "mistralai/mistral-7b-instruct"
# model = "moonshotai/kimi-vl-a3b-thinking:free"

model = "moonshotai/kimi-k2:free" #اصلی
# --------------------- پرامپت --------------------- #
def build_prompt(user_query: str) -> str:
    prompt = """
شما یک سیستم NLP هستید که وظیفه دارد از سوالات کاربر درباره تورهای مسافرتی، فیلترهای ساختاریافته استخراج کند.
فقط خروجی را به صورت JSON معتبر ارائه بده. هیچ توضیح اضافه‌ای ننویس.
ساختار فیلترها به صورت زیر است:

{
  "intent": "find_tour_with_conditions",
  "filters": {
    "price": {"low": ..., "high": ...},
    "duration_days": {"low": ..., "high": ...},
    "departure_date": {"start": "...", "end": "..." , "special": "nearest"  // یا "farthest" یا // null},
    "insurance_included": true | false | null,
    "services": [ ... ],
    "destination": "...",
    "destination_type" : "داخلی | null | خارجی"
  }
}

قوانین:
- فقط شهر های رسمی به عنوان مقصد
- اگر داخلی یا خارجی اشاره نشده بود null = destination_type
- تاریخ شمسی را فقط به صورت متن همان‌طور که گفته شده به این فرمت (yyyy-mm-dd) بازگردان (مثلاً "1404-06-20") و تبدیل به میلادی نکن. و هر قسمتی از تاریخ که مشخص نبود را ماه و سال جاری شمسی1404  را برگردان. 
- برای "گرون‌ترین"، مقدار high را "max" و min را null
- برای "ارزان‌ترین"، مقدار low را "min" و max را null
- special را درصورتی مقدار بده که نزدیک ترین یا دیر ترین را گفته باشد در غیر این صورت null
"""
    prompt += f"\nسوال: {user_query}\n"
    return prompt

def extract_json(text: str) -> dict:
    try:
        match = re.search(r'{.*}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {}
    except Exception as e:
        print("خطا در استخراج JSON:", e)
        return {}


#----------------------------------sfae answer
def safe_get_answer(response):
    """
    گرفتن متن جواب از خروجی مدل به صورت ایمن.
    هم با OpenAI و هم با OpenRouter سازگاره.
    """
    if isinstance(response, dict):  # بعضی وقتا JSON ساده میاد
        if "choices" in response:
            return response["choices"][0]["message"]["content"]
        elif "error" in response:
            return f"❌ خطا: {response['error'].get('message', 'Unknown')}"
        else:
            return f"⚠️ پاسخ غیرمنتظره: {response}"
    try:
        return response.choices[0].message["content"]
    except Exception as e:
        return f"⚠️ خطا در خواندن پاسخ: {str(e)}"


# --------------------- تابع اصلی --------------------- #
def get_chunks_for_query(user_query: str):
    # --- 1. استخراج فیلترها با NLP ---
    prompt_fa = build_prompt(user_query)
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt_fa}]
    )
    
    res_json_text = safe_get_answer(response)
    # res_json_text = response.choices[0].message["content"]
    parsed_json = extract_json(res_json_text)
    filters = parsed_json.get("filters", {})
    print(filters)

    # --- 2. اعمال فیلتر روی مدل‌های Django ---
    qs = Tour.objects.all()

    # مدت زمان
    duration_filter = filters.get("duration_days") or {}
    duration_low = duration_filter.get("low")
    duration_high = duration_filter.get("high")
    if duration_low is not None:
        qs = qs.filter(duration_days__gte=duration_low)
        print("🕒 بعد از duration_low:", qs.count(), list(qs.values_list("id", "name")))
    if duration_high is not None:
        qs = qs.filter(duration_days__lte=duration_high)
        print("🕒 بعد از duration_high:", qs.count(), list(qs.values_list("id", "name")))

    # بیمه
    insurance = filters.get("insurance_included")
    if insurance is not None:
        qs = qs.filter(insurance_included=insurance)
        print("🛡 بعد از فیلتر بیمه:", qs.count(), list(qs.values_list("id", "name")))

    # مقصد
    destination = filters.get("destination")
    if destination:
        qs = qs.filter(destination=destination)
        print("📍 بعد از فیلتر مقصد:", qs.count(), list(qs.values_list("id", "name")))


    # نوع مقصد
    dest_type = filters.get("destination_type")
    if dest_type:
        qs = qs.filter(destination_type=dest_type)
        print("🗺 بعد از فیلتر نوع مقصد:", qs.count(), list(qs.values_list("id", "name")))
    
    # تاریخ شمسی -> میلادی
    start_date_str = filters.get("departure_date", {}).get("start")
    end_date_str = filters.get("departure_date", {}).get("end")

    if start_date_str:
        try:
            jy, jm, jd = map(int, start_date_str.split("-"))
            start_date = jdatetime.date(jy, jm, jd).togregorian()
            qs = qs.filter(departure__date__gte=start_date)
        except Exception as e:
            print("❌ خطا در تبدیل تاریخ شمسی به میلادی (start):", e)

    if end_date_str:
        try:
            jy, jm, jd = map(int, end_date_str.split("-"))
            end_date = jdatetime.date(jy, jm, jd).togregorian()
            qs = qs.filter(departure__date__lte=end_date)
        except Exception as e:
            print("❌ خطا در تبدیل تاریخ شمسی به میلادی (end):", e)

    # قوانین نزدیک‌ترین / دورترین
    date_special = filters.get("departure_date", {}).get("special")  # new field: "nearest" | "farthest" | None

    if date_special == "nearest" and qs.exists():
        min_date = qs.order_by("departure__date").first().departure.date
        qs = qs.filter(departure__date=min_date)
    elif date_special == "farthest" and qs.exists():
        max_date = qs.order_by("-departure__date").first().departure.date
        qs = qs.filter(departure__date=max_date)
    else:
        pass        
    
    # گرون‌ترین / ارزان‌ترین
    price_filter = filters.get("price") or {}
    price_low = price_filter.get("low")
    price_high = price_filter.get("high")
    
    if price_low == "min" and price_high == "max":
        cheapest = qs.order_by("price").first()
        most_expensive = qs.order_by("-price").first()
        ids = []
        if cheapest:
            ids.append(cheapest.id)
        if most_expensive and most_expensive.id not in ids:
            ids.append(most_expensive.id)
        qs = qs.filter(id__in=ids)
        print("  و گران ترین از فیلتر ارزان ترین :", qs.count(), list(qs.values_list("id", "name")))

            
    elif price_high == "max":
        max_price = qs.order_by("-price").first().price if qs.exists() else None
        if max_price:
            qs = qs.filter(price=max_price)
            print(" بعد از فیلتر گران ترین :", qs.count(), list(qs.values_list("id", "name")))

    elif price_low == "min":
        min_price = qs.order_by("price").first().price if qs.exists() else None
        if min_price:
            qs = qs.filter(price=min_price)
            print(" بعد از فیلتر گران ترین :", qs.count(), list(qs.values_list("id", "name")))

    else:
        if price_low not in [None, "", "null"]:
            qs = qs.filter(price__gte=int(price_low))
            print(" بعد از فیلتر کم قیمت :", qs.count(), list(qs.values_list("id", "name")))


        if price_high not in [None, "", "null"]:
            qs = qs.filter(price__lte=int(price_high))
            print(" بعد از فیلتر  زیاد قیمت :", qs.count(), list(qs.values_list("id", "name")))
        
            
    filtered_tours = list(qs)
    filtered_tour_ids = [t.id for t in filtered_tours]

    # --- 3. گرفتن چانک‌های مرتبط ---
    filtered_chunks = Chunk.objects.filter(tour__id__in=filtered_tour_ids)
    
        # چک کنیم آیا همه‌ی تورهای دیتابیس برگشتن یا نه
    
    all_tour_ids = set(Tour.objects.values_list('id', flat=True))
    filtered_tour_ids = set(t.id for t in filtered_tours)

    if filtered_tour_ids == all_tour_ids:
        # همه تورها برگشتن، یعنی فیلتر معنا نداشته، پس خروجی خالی میدیم
        return [], []
    
    return filtered_tours, filtered_chunks




# --------------------- تابع دوم --------------------- #
def get_chunks_for_query2():

    filters = {'price': {'low': 'min', 'high': 'max'}, 'duration_days': {'low': None, 'high': None}, 'departure_date': {'start': None, 'end': None, 'special': None}, 'insurance_included': None, 'services': [], 'destination': None, 'destination_type': 'خارجی'}
    print(filters)

    # --- 2. اعمال فیلتر روی مدل‌های Django ---
    qs = Tour.objects.all()

    # مدت زمان
    duration_filter = filters.get("duration_days") or {}
    duration_low = duration_filter.get("low")
    duration_high = duration_filter.get("high")
    if duration_low is not None:
        qs = qs.filter(duration_days__gte=duration_low)
        print("🕒 بعد از duration_low:", qs.count(), list(qs.values_list("id", "name" , "price")))
    if duration_high is not None:
        qs = qs.filter(duration_days__lte=duration_high)
        print("🕒 بعد از duration_high:", qs.count(), list(qs.values_list("id", "name", "price")))

    # بیمه
    insurance = filters.get("insurance_included")
    if insurance is not None:
        qs = qs.filter(insurance_included=insurance)
        print("🛡 بعد از فیلتر بیمه:", qs.count(), list(qs.values_list("id", "name", "price")))

    # مقصد
    destination = filters.get("destination")
    if destination:
        qs = qs.filter(destination=destination)
        print("📍 بعد از فیلتر مقصد:", qs.count(), list(qs.values_list("id", "name", "price")))


    # نوع مقصد
    dest_type = filters.get("destination_type")
    if dest_type:
        qs = qs.filter(destination_type=dest_type)
        print("🗺 بعد از فیلتر نوع مقصد:", qs.count(), list(qs.values_list("id", "name", "price")))
    
    # تاریخ شمسی -> میلادی
    start_date_str = filters.get("departure_date", {}).get("start")
    end_date_str = filters.get("departure_date", {}).get("end")

    if start_date_str:
        try:
            jy, jm, jd = map(int, start_date_str.split("-"))
            start_date = jdatetime.date(jy, jm, jd).togregorian()
            qs = qs.filter(departure__date__gte=start_date)
        except Exception as e:
            print("❌ خطا در تبدیل تاریخ شمسی به میلادی (start):", e)

    if end_date_str:
        try:
            jy, jm, jd = map(int, end_date_str.split("-"))
            end_date = jdatetime.date(jy, jm, jd).togregorian()
            qs = qs.filter(departure__date__lte=end_date)
        except Exception as e:
            print("❌ خطا در تبدیل تاریخ شمسی به میلادی (end):", e)

    # قوانین نزدیک‌ترین / دورترین
    date_special = filters.get("departure_date", {}).get("special")  # new field: "nearest" | "farthest" | None

    if date_special == "nearest" and qs.exists():
        min_date = qs.order_by("departure__date").first().departure.date
        qs = qs.filter(departure__date=min_date)
    elif date_special == "farthest" and qs.exists():
        max_date = qs.order_by("-departure__date").first().departure.date
        qs = qs.filter(departure__date=max_date)
    else:
        pass        
    
    # گرون‌ترین / ارزان‌ترین
    price_filter = filters.get("price") or {}
    price_low = price_filter.get("low")
    price_high = price_filter.get("high")
    
    if price_low == "min" and price_high == "max":
        cheapest = qs.order_by("price").first()
        most_expensive = qs.order_by("-price").first()
        ids = []
        if cheapest:
            ids.append(cheapest.id)
        if most_expensive and most_expensive.id not in ids:
            ids.append(most_expensive.id)
        qs = qs.filter(id__in=ids)
        print("  و گران ترین از فیلتر ارزان ترین :", qs.count(), list(qs.values_list("id", "name", "price")))

            
    elif price_high == "max":
        max_price = qs.order_by("-price").first().price if qs.exists() else None
        if max_price:
            qs = qs.filter(price=max_price)
            print(" بعد از فیلتر گران ترین :", qs.count(), list(qs.values_list("id", "name", "price")))

    elif price_low == "min":
        min_price = qs.order_by("price").first().price if qs.exists() else None
        if min_price:
            qs = qs.filter(price=min_price)
            print(" بعد از فیلتر گران ترین :", qs.count(), list(qs.values_list("id", "name" , "price")))

    else:
        if price_low not in [None, "", "null"]:
            qs = qs.filter(price__gte=int(price_low))
            print(" بعد از فیلتر کم قیمت :", qs.count(), list(qs.values_list("id", "name" , "price")))


        if price_high not in [None, "", "null"]:
            qs = qs.filter(price__lte=int(price_high))
            print(" بعد از فیلتر  زیاد قیمت :", qs.count(), list(qs.values_list("id", "name" , "price")))
        
            
    filtered_tours = list(qs)
    filtered_tour_ids = [t.id for t in filtered_tours]

    # --- 3. گرفتن چانک‌های مرتبط ---
    filtered_chunks = Chunk.objects.filter(tour__id__in=filtered_tour_ids)
    
        # چک کنیم آیا همه‌ی تورهای دیتابیس برگشتن یا نه
    
    all_tour_ids = set(Tour.objects.values_list('id', flat=True))
    filtered_tour_ids = set(t.id for t in filtered_tours)

    if filtered_tour_ids == all_tour_ids:
        # همه تورها برگشتن، یعنی فیلتر معنا نداشته، پس خروجی خالی میدیم
        return [], []
    
    return filtered_tours, filtered_chunks






# --------------------- مثال استفاده --------------------- #
if __name__ == "__main__":
    # query = "  از 9 آذر تا 20 آذر ی تور میخوام  قیمتش بالای 2300 باشه و بین6 تا 7 شب هم باشه بیمه هم داشته باشه یا نداشته باشه مهم نیست ولی حتما خارجی باشه"
    # query = "گرون ترین  تور دبی"
    # query = " تور دبی"
    # query = " تور رو بده بهم"
    query = "گرون ترین تور و ارزون ترین که داری کجاست؟"
    tours, chunks = get_chunks_for_query(query)
    # tours, chunks = get_chunks_for_query2()
    print("🏷 تورهای فیلتر شده:")
    for t in tours:
        print("-", t.name)

    print("\n📝 چانک‌های مرتبط:")
    for c in chunks:
        print("-", c.text)
