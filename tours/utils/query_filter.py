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

model = "moonshotai/kimi-k2:free"
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
- تاریخ شمسی را فقط به صورت متن همان‌طور که گفته شده به این فرمت (yyyy-mm-dd) بازگردان (مثلاً "1404-06-20") و تبدیل به میلادی نکن. و هر قسمتی از تاریخ که مشخص نبود را ماه و سال جاری شمسی1404  را برگردان. 
- برای "گرون‌ترین"، مقدار high را "max"
- برای "ارزان‌ترین"، مقدار low را "min"
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
    if duration_high is not None:
        qs = qs.filter(duration_days__lte=duration_high)

    # بیمه
    insurance = filters.get("insurance_included")
    if insurance is not None:
        qs = qs.filter(insurance_included=insurance)

    # مقصد
    destination = filters.get("destination")
    if destination:
        qs = qs.filter(destination=destination)

    # نوع مقصد
    dest_type = filters.get("destination_type")
    if dest_type:
        qs = qs.filter(destination_type=dest_type)

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
    if price_low == "min":
        min_price = qs.order_by("price").first().price if qs.exists() else None
        if min_price:
            qs = qs.filter(price=min_price)
    elif price_high == "max":
        max_price = qs.order_by("-price").first().price if qs.exists() else None
        if max_price:
            qs = qs.filter(price=max_price)
    else:
        if price_low not in [None, "", "null"]:
            qs = qs.filter(price__gte=int(price_low))

        if price_high not in [None, "", "null"]:
            qs = qs.filter(price__lte=int(price_high))
    filtered_tours = list(qs)
    filtered_tour_ids = [t.id for t in filtered_tours]

    # --- 3. گرفتن چانک‌های مرتبط ---
    filtered_chunks = Chunk.objects.filter(tour__id__in=filtered_tour_ids)

    return filtered_tours, filtered_chunks

# --------------------- مثال استفاده --------------------- #
if __name__ == "__main__":
    query = "  از 9 آذر تا 20 آدر ی تور میخوام  قیمتش بالای 2300 باشه و بین6 تا 7 شب هم باشه بیمه هم داشته باشه یا نداشته باشه مهم نیست ولی حتما خارجی باشه"
    # query = "گرون ترین  تور دبی"
    # query = " تور دبی"
    # query = "نزدیک ترین تاریخ تور رو بده بهم"
    tours, chunks = get_chunks_for_query(query)

    print("🏷 تورهای فیلتر شده:")
    for t in tours:
        print("-", t.name)

    print("\n📝 چانک‌های مرتبط:")
    for c in chunks:
        print("-", c.text)
