import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")

import django
django.setup()

# filter key 
# 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


# کد با لنگ چین

import jdatetime
import datetime
from typing import Optional, List, Literal
from tours.models import Tour, Chunk

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import Union


# --------------------- تعریف مدل فیلترها (Pydantic) --------------------- #
class PriceFilter(BaseModel):
    low: Optional[Union[str, int]] = Field(None, description="حداقل قیمت یا 'min'")
    high: Optional[Union[str, int]] = Field(None, description="حداکثر قیمت یا 'max'")


class DurationFilter(BaseModel):
    low: Optional[int] = None
    high: Optional[int] = None


class DepartureDate(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    special: Optional[Literal["nearest", "farthest"]] = None


class Filters(BaseModel):
    price: PriceFilter = PriceFilter(low=None, high=None)
    duration_days: DurationFilter = DurationFilter(low=None, high=None)
    departure_date: DepartureDate = DepartureDate()
    insurance_included: Optional[bool] = None
    # services: List[str] = []
    services: Optional[List[str]] = []
    destination: Optional[str] = None
    destination_type: Optional[Literal["داخلی", "خارجی", None]] = None


class TourQuery(BaseModel):
    # intent: Literal["find_tour_with_conditions"]
    filters: Filters


# --------------------- LangChain تنظیم --------------------- #
parser = PydanticOutputParser(pydantic_object=TourQuery)

llm = ChatOpenAI(
    # model = "qwen/qwen2.5-vl-72b-instruct:free",
    # model="deepseek/deepseek-r1-0528-qwen3-8b:free",  # مدل پیشنهادی
    # model = "nousresearch/deephermes-3-llama-3-8b-preview:free",
    # model = "google/gemma-3-27b-it:free" ,
    # model = "moonshotai/kimi-k2:free",
    # model = "google/gemma-3-12b-it:free" , #اصلی اینه
    model = "meta-llama/llama-3.3-70b-instruct:free",
    # model = "google/gemma-3-4b-it:free" , # بد
    # model = "google/gemma-2-9b-it:free",# بد
    # model = "google/gemma-3n-e4b-it:free",
    # model = "google/gemma-3n-e2b-it:free",# بد دافون

    
    temperature=0,
    openai_api_key = "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", #zapas
    # openai_api_key="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",  # کلیدتو جایگزین کن
    openai_api_base="https://openrouter.ai/api/v1"

)

prompt_template = PromptTemplate(
    template="""
شما یک سیستم NLP هستید که باید از سوالات کاربر درباره تورهای مسافرتی فیلترهای ساختاریافته استخراج کنید.
فقط JSON معتبر بده، هیچ متن اضافی ننویس.

قوانین:
- فقط شهرهای رسمی به عنوان مقصد
- اگر داخلی/خارجی مشخص نبود → null

- اگر عدد مشخصی برای تعداد روز گفته شد (مثل "تور ۳ روزه") و هیچ عبارتی مثل "کمتر از"، "بیشتر از"، "بین"، "حداقل"، "حداکثر" در جمله نبود، مقدارهای low و high در duration_days را برابر همان عدد قرار بده.

- تمام تاریخ‌ها را به صورت شمسی و فرمت yyyy-mm-dd بازگردان. ماه و روز را دقیقاً همان‌طور که گفته شده پر کن.
-اگر تنها ماه را گفته بود و سال را نگفته بود yyyy = 1404 قرار بده
- برای اسفند ماه mm = 12 , بهمن mm=11 , دی mm=10 , آذر mm=09 , آبان mm=08 , مهر mm=07 , شهریور mm=06 , مرداد mm=05 , تیر mm=04 , خرداد mm=03 , ادبیهشت mm=02  
- اگر تنها بازه ی روز را گفته بود مثلا از 2 ام تا 20 ام mm=07 و yyyy=1404 را ماه و سال جاری شمسی قرار بده

- اگر گفت سال آینده یعنی yyyy=1405

- برای "گرون‌ترین": high="max", low=null
- برای "ارزان‌ترین": low="min", high=null

- کلمات بالاتر از ، بیشتر از ،گران تر از هم معنی هستند و اگر کاربر گفت "بالای X" → low=X
-کلمات پایین از ، کمتر از ارزان تر از هم معنی هستند و اگر کاربر گفت "کم‌تر از X" → high=X

- departure_date.special فقط وقتی مقدار بده که "نزدیک‌ترین" یا "دورترین" گفته شود، وگرنه null
- حتما تمام فیلدهای زیر را پر کن:
- اگر مقداری وجود ندارد، عددها را null و لیست‌ها را [] و رشته‌ها را null بگذار.
- به خصوص فیلد duration_days، departure_date و price باید همیشه به صورت dictionary بازگردانده شوند.


سوال: {query}
{format_instructions}
""",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# - اگر عدد مشخصی برای تعداد روز گفته شد (مثل "تور ۳ روزه") و هیچ عبارتی مثل "کمتر از"، "بیشتر از"، "بین"، "حداقل"، "حداکثر" در جمله نبود، مقدارهای low و high در duration_days را برابر همان عدد قرار بده.

# - اگر کاربر گفت "بالای X" → low=X و high=null
# - اگر کاربر گفت "کم‌تر از X" → low=null و high=X
# - اگر گفت "بین X و Y" → low=X و high=Y
# مثال:
# " بالای 2300" → {{ "price": {{ "low": 2300, "high": null }} }}
# " کم‌تر از 1500" → {{ "price": {{ "low": null, "high": 1500 }} }}
# " بین 1000 و 2000" → {{ "price": {{ "low": 1000, "high": 2000 }} }}


# --------------------- تابع اصلی --------------------- #
def get_chunks_for_query(user_query: str):
    # --- 1. استخراج فیلترها با NLP  ---
    prompt = prompt_template.format_prompt(query=user_query)
    output = llm.invoke(prompt.to_messages())
    
    try:
        parsed = parser.parse(output.content)
    except Exception as e:
        print("Error parsing output:", e)
        parsed = TourQuery(filters=Filters())  # یا هر مقدار پیش‌فرض مناسب
    
    # parsed = parser.parse(output.content)

    filters = parsed.filters.dict()
    print("🎯 فیلترهای استخراج‌شده:", filters)
    
    # filters = {'price': {'low': None, 'high': None}, 'duration_days': {'low': 3, 'high': 3}, 'departure_date': {'start': None, 'end': None, 'special': None}, 'insurance_included': None, 'services': [], 'destination': None, 'destination_type': 'داخلی'}
    # filters = {'price': {'low': None, 'high': None}, 'duration_days': {'low': None, 'high': None}, 'departure_date': {'start': None, 'end': None, 'special': None}, 'insurance_included': None, 'services': [], 'destination': None, 'destination_type': None}
    print("\n\n")

    # --- 2. اعمال فیلتر روی مدل‌های Django ---
    qs = Tour.objects.all()

    # مدت زمان
    duration_filter = filters.get("duration_days") or {}
    duration_low = duration_filter.get("low")
    duration_high = duration_filter.get("high")
    if duration_low is not None:
        qs = qs.filter(duration_days__gte=duration_low)
        print(" بعد از duration_low:", qs.count(), list(qs.values_list("id", "name" , "price")))
    if duration_high is not None:
        qs = qs.filter(duration_days__lte=duration_high)
        print(" بعد از duration_high:", qs.count(), list(qs.values_list("id", "name", "price")))

    # بیمه
    insurance = filters.get("insurance_included")
    if insurance is not None:
        qs = qs.filter(insurance_included=insurance)
        # print(" بعد از فیلتر بیمه:", qs.count(), list(qs.values_list("id", "name", "price")))

    # مقصد
    destination = filters.get("destination")
    if destination:
        qs = qs.filter(destination=destination)
        # print(" بعد از فیلتر مقصد:", qs.count(), list(qs.values_list("id", "name", "price")))


    # نوع مقصد
    dest_type = filters.get("destination_type")
    if dest_type:
        qs = qs.filter(destination_type=dest_type)
        # print(" بعد از فیلتر نوع مقصد:", qs.count(), list(qs.values_list("id", "name", "price")))
    
    # تاریخ شمسی -> میلادی
    start_date_str = filters.get("departure_date", {}).get("start")
    end_date_str = filters.get("departure_date", {}).get("end")

    if start_date_str:
        try:
            jy, jm, jd = map(int, start_date_str.split("-"))
            if jy < 1404:
                jy = 1404
            if jy > 1405:
                jy = 1404    
            if jd == 31:
                jd = 29
            start_date = jdatetime.date(jy, jm, jd).togregorian()
            print(start_date)
            qs = qs.filter(departure__date__gte=start_date)
        except Exception as e:
            print(" خطا در تبدیل تاریخ شمسی به میلادی (start):", e)

    if end_date_str:
        try:
            jy, jm, jd = map(int, end_date_str.split("-"))
            # تنظیم حداقل سال: اگر کمتر از 1404 بود، 1404 بکن
            if jy < 1404:
                jy = 1404
            if jy > 1405:
                jy = 1404 
            if jd == 31:
                jd = 29
            end_date = jdatetime.date(jy, jm, jd).togregorian()
            print(end_date)
            qs = qs.filter(departure__date__lte=end_date)
        except Exception as e:
            print(" خطا در تبدیل تاریخ شمسی به میلادی (end):", e)

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
        # print("  و گران ترین از فیلتر ارزان ترین :", qs.count(), list(qs.values_list("id", "name", "price")))

            
    elif price_high == "max":
        max_price = qs.order_by("-price").first().price if qs.exists() else None
        if max_price:
            qs = qs.filter(price=max_price)
            # print(" بعد از فیلتر گران ترین :", qs.count(), list(qs.values_list("id", "name", "price")))

    elif price_low == "min":
        min_price = qs.order_by("price").first().price if qs.exists() else None
        if min_price:
            qs = qs.filter(price=min_price)
            # print(" بعد از فیلتر گران ترین :", qs.count(), list(qs.values_list("id", "name" , "price")))

    else:
        if price_low not in [None, "", "null"]:
            qs = qs.filter(price__gte=int(price_low))
            # print(" بعد از فیلتر کم قیمت :", qs.count(), list(qs.values_list("id", "name" , "price")))


        if price_high not in [None, "", "null"]:
            qs = qs.filter(price__lte=int(price_high))
            # print(" بعد از فیلتر  زیاد قیمت :", qs.count(), list(qs.values_list("id", "name" , "price")))
        
            
    filtered_tours = list(qs)
    filtered_tours = list(qs.order_by("-departure__date")[:4]) #خلاصه کردن
    filtered_tour_ids = [t.id for t in filtered_tours]

    # --- 3. گرفتن چانک‌های مرتبط ---
    filtered_chunks = Chunk.objects.filter(tour__id__in=filtered_tour_ids)
    
    # چک کنیم آیا همه‌ی تورهای دیتابیس برگشتن یا نه
    
    all_tour_ids = set(Tour.objects.values_list('id', flat=True))
    filtered_tour_ids = set(t.id for t in filtered_tours)
    
    print(" تعداد تورهای نهایی:", len(filtered_tours))
    for t in filtered_tours:
        print(f"- {t.id} | {t.name} | {t.price} | {t.duration_days} روز | بیمه: {t.insurance_included}")

    if filtered_tour_ids == all_tour_ids:
        # همه تورها برگشتن، یعنی فیلتر معنا نداشته، پس خروجی خالی میدیم
        return [], []
    
    return filtered_tours, filtered_chunks


# --------------------- تست --------------------- #
def test_query():
    # user_query = "تور ارزون به استانبول برای 3 شب با بیمه"
    # query = "  از 9 آذر تا 20 آذر ی تور میخوام  قیمتش بیشتر از 2300 باشه و بین6 تا 7 شب هم باشه بیمه هم داشته باشه یا نداشته باشه مهم نیست ولی حتما خارجی باشه"
    # query = " ی تور برای اسفند ماه " 
    # query = " ی تور برای 20 مهر تا 20 آبان میخوام "  # ok
    # query = " ی تور برای سال آینده میخوام چیا داری" # 31 ام رو درست کنم   # ok
    # query = "گرون ترین  تور دبی"
    # query = " تور دبی"
    # query = " تور رو بده بهم"
    # query = "گرون ترین تور و ارزون ترین که داری کجاست؟"
    # query = "تور خارجی 6 شب بدون بیمه، قیمت بین 500 هزار تومن تا 3 تومن باشه 20 مهر تا 20 آبان هم باشه" 
    query = "تور خارجی میخوام قیمتش بین 5 تا 10 تومن باشه و بین 5 تا 7 شب باشه بیمه هم داشته باشه یا نداشته باشه مهم نیست . توی دی ماه هم باشه چیا داری؟"
    # query = "تور خارجی میخوام بیشتر از 15 تومن باشه توی مهر ماه هم باشه بیمه هم داشته باشه بیشتر از 5 روز هم باشه چه چیز هایی داری؟"

    filtered_tours, filtered_chunks = get_chunks_for_query(query)

    print("\n✅ تست با ورودی:", query)
    print("📊 تعداد تورهای نهایی:", len(filtered_tours))
    for t in filtered_tours:
        print(f"- {t.id} | {t.name} | {t.price} | {t.duration_days} روز | بیمه: {t.insurance_included}")


# اگر مستقیم فایل ران شد → تست بزن
if __name__ == "__main__":
    test_query()



# فیلترهای استخراج‌شده:
#     {'price': {'low': '500000', 'high': '3000000'}, 'duration_days': {'low': 6, 'high': 6},
#      'departure_date': {'start': '1402-07-20', 'end': '1402-08-20', 'special': None}, 'insurance_included': False, 
#      'services': [], 'destination': None, 'destination_type': 'خارجی'}    

# ✅ تست با ورودی: تور خارجی 6 شب بدون بیمه، قیمت بین 500 هزار تومن تا 3 تومن باشه 20 مهر تا 20 آبان هم باشه
# 📊 تعداد تورهای نهایی: 0










# import sys
# import os

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(BASE_DIR)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")

# import django
# django.setup()

# import jdatetime
# import datetime
# import json
# import re
# import openai
# from tours.models import Tour, Chunk

# # --------------------- تنظیم OpenAI --------------------- #
# # openai.api_key = "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"  # <<-- کلیدت اینجا

# openai.api_key = "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"
# openai.api_base = "https://openrouter.ai/api/v1"


# # model = "qwen/qwen3-235b-a22b:free"  # محشرهههه
# # model = "openrouter/horizon-beta" # اینم عالیه
# # model = "deepseek/deepseek-r1-0528:free"
# # model = "z-ai/glm-4.5-air:free"
# # model = "google/gemma-3n-e4b-it:free"
# # model = "mistralai/mistral-7b-instruct"
# # model = "moonshotai/kimi-vl-a3b-thinking:free"

# model = "moonshotai/kimi-k2:free" #اصلی
# # model = "moonshotai/kimi-dev-72b:free" بد

# model="deepseek/deepseek-r1-0528-qwen3-8b:free"  # خوبه کامل درست برای جزیی خراب
# # model = "qwen/qwen2.5-vl-72b-instruct:free"
# # --------------------- پرامپت --------------------- #
# def build_prompt(user_query: str) -> str:
#     prompt = """
# شما یک سیستم NLP هستید که وظیفه دارد از سوالات کاربر درباره تورهای مسافرتی، فیلترهای ساختاریافته استخراج کند.
# فقط خروجی را به صورت JSON معتبر ارائه بده. هیچ توضیح اضافه‌ای ننویس.
# ساختار فیلترها به صورت زیر است:

# {
#   "intent": "find_tour_with_conditions",
#   "filters": {
#     "price": {"low": ..., "high": ...},
#     "duration_days": {"low": ..., "high": ...},
#     "departure_date": {"start": "...", "end": "..." , "special": "nearest"  // یا "farthest" یا // null},
#     "insurance_included": true | false | null,
#     "services": [ ... ],
#     "destination": "...",
#     "destination_type" : "داخلی | null | خارجی"
#   }
# }

# قوانین:
# - فقط شهر های رسمی به عنوان مقصد
# - اگر داخلی یا خارجی اشاره نشده بود null = destination_type
# - تاریخ شمسی را فقط به صورت متن همان‌طور که گفته شده به این فرمت (yyyy-mm-dd) بازگردان (مثلاً "1404-06-20") و تبدیل به میلادی نکن. و هر قسمتی از تاریخ که مشخص نبود را ماه و سال جاری شمسی1404  را برگردان. 
# - برای "گرون‌ترین"، مقدار high را "max" و min را null
# - برای "ارزان‌ترین"، مقدار low را "min" و max را null
# - special را درصورتی مقدار بده که نزدیک ترین یا دیر ترین را گفته باشد در غیر این صورت null
# """
#     prompt += f"\nسوال: {user_query}\n"
#     return prompt

# def extract_json(text: str) -> dict:
#     try:
#         match = re.search(r'{.*}', text, re.DOTALL)
#         if match:
#             return json.loads(match.group(0))
#         return {}
#     except Exception as e:
#         print("خطا در استخراج JSON:", e)
#         return {}


# #----------------------------------sfae answer
# def safe_get_answer(response):
#     """
#     گرفتن متن جواب از خروجی مدل به صورت ایمن.
#     هم با OpenAI و هم با OpenRouter سازگاره.
#     """
#     if isinstance(response, dict):  # بعضی وقتا JSON ساده میاد
#         if "choices" in response:
#             return response["choices"][0]["message"]["content"]
#         elif "error" in response:
#             return f"❌ خطا: {response['error'].get('message', 'Unknown')}"
#         else:
#             return f"⚠️ پاسخ غیرمنتظره: {response}"
#     try:
#         return response.choices[0].message["content"]
#     except Exception as e:
#         return f"⚠️ خطا در خواندن پاسخ: {str(e)}"


# # --------------------- تابع اصلی --------------------- #
# def get_chunks_for_query(user_query: str):
#     # --- 1. استخراج فیلترها با NLP ---
#     prompt_fa = build_prompt(user_query)
#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=[{"role": "user", "content": prompt_fa}]
#     )
    
#     res_json_text = safe_get_answer(response)
#     # res_json_text = response.choices[0].message["content"]
#     parsed_json = extract_json(res_json_text)
#     filters = parsed_json.get("filters", {})
#     print(filters)

#     # --- 2. اعمال فیلتر روی مدل‌های Django ---
#     qs = Tour.objects.all()

#     # مدت زمان
#     duration_filter = filters.get("duration_days") or {}
#     duration_low = duration_filter.get("low")
#     duration_high = duration_filter.get("high")
#     if duration_low is not None:
#         qs = qs.filter(duration_days__gte=duration_low)
#         print("🕒 بعد از duration_low:", qs.count(), list(qs.values_list("id", "name")))
#     if duration_high is not None:
#         qs = qs.filter(duration_days__lte=duration_high)
#         print("🕒 بعد از duration_high:", qs.count(), list(qs.values_list("id", "name")))

#     # بیمه
#     insurance = filters.get("insurance_included")
#     if insurance is not None:
#         qs = qs.filter(insurance_included=insurance)
#         print("🛡 بعد از فیلتر بیمه:", qs.count(), list(qs.values_list("id", "name")))

#     # مقصد
#     destination = filters.get("destination")
#     if destination:
#         qs = qs.filter(destination=destination)
#         print("📍 بعد از فیلتر مقصد:", qs.count(), list(qs.values_list("id", "name")))


#     # نوع مقصد
#     dest_type = filters.get("destination_type")
#     if dest_type:
#         qs = qs.filter(destination_type=dest_type)
#         print("🗺 بعد از فیلتر نوع مقصد:", qs.count(), list(qs.values_list("id", "name")))
    
#     # تاریخ شمسی -> میلادی
#     start_date_str = filters.get("departure_date", {}).get("start")
#     end_date_str = filters.get("departure_date", {}).get("end")

#     if start_date_str:
#         try:
#             jy, jm, jd = map(int, start_date_str.split("-"))
#             start_date = jdatetime.date(jy, jm, jd).togregorian()
#             qs = qs.filter(departure__date__gte=start_date)
#         except Exception as e:
#             print("❌ خطا در تبدیل تاریخ شمسی به میلادی (start):", e)

#     if end_date_str:
#         try:
#             jy, jm, jd = map(int, end_date_str.split("-"))
#             end_date = jdatetime.date(jy, jm, jd).togregorian()
#             qs = qs.filter(departure__date__lte=end_date)
#         except Exception as e:
#             print("❌ خطا در تبدیل تاریخ شمسی به میلادی (end):", e)

#     # قوانین نزدیک‌ترین / دورترین
#     date_special = filters.get("departure_date", {}).get("special")  # new field: "nearest" | "farthest" | None

#     if date_special == "nearest" and qs.exists():
#         min_date = qs.order_by("departure__date").first().departure.date
#         qs = qs.filter(departure__date=min_date)
#     elif date_special == "farthest" and qs.exists():
#         max_date = qs.order_by("-departure__date").first().departure.date
#         qs = qs.filter(departure__date=max_date)
#     else:
#         pass        
    
#     # گرون‌ترین / ارزان‌ترین
#     price_filter = filters.get("price") or {}
#     price_low = price_filter.get("low")
#     price_high = price_filter.get("high")
    
#     if price_low == "min" and price_high == "max":
#         cheapest = qs.order_by("price").first()
#         most_expensive = qs.order_by("-price").first()
#         ids = []
#         if cheapest:
#             ids.append(cheapest.id)
#         if most_expensive and most_expensive.id not in ids:
#             ids.append(most_expensive.id)
#         qs = qs.filter(id__in=ids)
#         print("  و گران ترین از فیلتر ارزان ترین :", qs.count(), list(qs.values_list("id", "name")))

            
#     elif price_high == "max":
#         max_price = qs.order_by("-price").first().price if qs.exists() else None
#         if max_price:
#             qs = qs.filter(price=max_price)
#             print(" بعد از فیلتر گران ترین :", qs.count(), list(qs.values_list("id", "name")))

#     elif price_low == "min":
#         min_price = qs.order_by("price").first().price if qs.exists() else None
#         if min_price:
#             qs = qs.filter(price=min_price)
#             print(" بعد از فیلتر گران ترین :", qs.count(), list(qs.values_list("id", "name")))

#     else:
#         if price_low not in [None, "", "null"]:
#             qs = qs.filter(price__gte=int(price_low))
#             print(" بعد از فیلتر کم قیمت :", qs.count(), list(qs.values_list("id", "name")))


#         if price_high not in [None, "", "null"]:
#             qs = qs.filter(price__lte=int(price_high))
#             print(" بعد از فیلتر  زیاد قیمت :", qs.count(), list(qs.values_list("id", "name")))
        
            
#     filtered_tours = list(qs)
#     filtered_tour_ids = [t.id for t in filtered_tours]

#     # --- 3. گرفتن چانک‌های مرتبط ---
#     filtered_chunks = Chunk.objects.filter(tour__id__in=filtered_tour_ids)
    
#         # چک کنیم آیا همه‌ی تورهای دیتابیس برگشتن یا نه
    
#     all_tour_ids = set(Tour.objects.values_list('id', flat=True))
#     filtered_tour_ids = set(t.id for t in filtered_tours)

#     if filtered_tour_ids == all_tour_ids:
#         # همه تورها برگشتن، یعنی فیلتر معنا نداشته، پس خروجی خالی میدیم
#         return [], []
    
#     return filtered_tours, filtered_chunks




# # --------------------- تابع دوم --------------------- #
# def get_chunks_for_query2():

#     filters = {'price': {'low': 'min', 'high': 'max'}, 'duration_days': {'low': None, 'high': None}, 'departure_date': {'start': None, 'end': None, 'special': None}, 'insurance_included': None, 'services': [], 'destination': None, 'destination_type': 'خارجی'}
#     print(filters )
#     print("\n\n")

#     # --- 2. اعمال فیلتر روی مدل‌های Django ---
#     qs = Tour.objects.all()

#     # مدت زمان
#     duration_filter = filters.get("duration_days") or {}
#     duration_low = duration_filter.get("low")
#     duration_high = duration_filter.get("high")
#     if duration_low is not None:
#         qs = qs.filter(duration_days__gte=duration_low)
#         print("🕒 بعد از duration_low:", qs.count(), list(qs.values_list("id", "name" , "price")))
#     if duration_high is not None:
#         qs = qs.filter(duration_days__lte=duration_high)
#         print("🕒 بعد از duration_high:", qs.count(), list(qs.values_list("id", "name", "price")))

#     # بیمه
#     insurance = filters.get("insurance_included")
#     if insurance is not None:
#         qs = qs.filter(insurance_included=insurance)
#         print("🛡 بعد از فیلتر بیمه:", qs.count(), list(qs.values_list("id", "name", "price")))

#     # مقصد
#     destination = filters.get("destination")
#     if destination:
#         qs = qs.filter(destination=destination)
#         print("📍 بعد از فیلتر مقصد:", qs.count(), list(qs.values_list("id", "name", "price")))


#     # نوع مقصد
#     dest_type = filters.get("destination_type")
#     if dest_type:
#         qs = qs.filter(destination_type=dest_type)
#         print("🗺 بعد از فیلتر نوع مقصد:", qs.count(), list(qs.values_list("id", "name", "price")))
    
#     # تاریخ شمسی -> میلادی
#     start_date_str = filters.get("departure_date", {}).get("start")
#     end_date_str = filters.get("departure_date", {}).get("end")

#     if start_date_str:
#         try:
#             jy, jm, jd = map(int, start_date_str.split("-"))
#             start_date = jdatetime.date(jy, jm, jd).togregorian()
#             qs = qs.filter(departure__date__gte=start_date)
#         except Exception as e:
#             print("❌ خطا در تبدیل تاریخ شمسی به میلادی (start):", e)

#     if end_date_str:
#         try:
#             jy, jm, jd = map(int, end_date_str.split("-"))
#             end_date = jdatetime.date(jy, jm, jd).togregorian()
#             qs = qs.filter(departure__date__lte=end_date)
#         except Exception as e:
#             print("❌ خطا در تبدیل تاریخ شمسی به میلادی (end):", e)

#     # قوانین نزدیک‌ترین / دورترین
#     date_special = filters.get("departure_date", {}).get("special")  # new field: "nearest" | "farthest" | None

#     if date_special == "nearest" and qs.exists():
#         min_date = qs.order_by("departure__date").first().departure.date
#         qs = qs.filter(departure__date=min_date)
#     elif date_special == "farthest" and qs.exists():
#         max_date = qs.order_by("-departure__date").first().departure.date
#         qs = qs.filter(departure__date=max_date)
#     else:
#         pass        
    
#     # گرون‌ترین / ارزان‌ترین
#     price_filter = filters.get("price") or {}
#     price_low = price_filter.get("low")
#     price_high = price_filter.get("high")
    
#     if price_low == "min" and price_high == "max":
#         cheapest = qs.order_by("price").first()
#         most_expensive = qs.order_by("-price").first()
#         ids = []
#         if cheapest:
#             ids.append(cheapest.id)
#         if most_expensive and most_expensive.id not in ids:
#             ids.append(most_expensive.id)
#         qs = qs.filter(id__in=ids)
#         print("  و گران ترین از فیلتر ارزان ترین :", qs.count(), list(qs.values_list("id", "name", "price")))

            
#     elif price_high == "max":
#         max_price = qs.order_by("-price").first().price if qs.exists() else None
#         if max_price:
#             qs = qs.filter(price=max_price)
#             print(" بعد از فیلتر گران ترین :", qs.count(), list(qs.values_list("id", "name", "price")))

#     elif price_low == "min":
#         min_price = qs.order_by("price").first().price if qs.exists() else None
#         if min_price:
#             qs = qs.filter(price=min_price)
#             print(" بعد از فیلتر گران ترین :", qs.count(), list(qs.values_list("id", "name" , "price")))

#     else:
#         if price_low not in [None, "", "null"]:
#             qs = qs.filter(price__gte=int(price_low))
#             print(" بعد از فیلتر کم قیمت :", qs.count(), list(qs.values_list("id", "name" , "price")))


#         if price_high not in [None, "", "null"]:
#             qs = qs.filter(price__lte=int(price_high))
#             print(" بعد از فیلتر  زیاد قیمت :", qs.count(), list(qs.values_list("id", "name" , "price")))
        
            
#     filtered_tours = list(qs)
#     filtered_tour_ids = [t.id for t in filtered_tours]

#     # --- 3. گرفتن چانک‌های مرتبط ---
#     filtered_chunks = Chunk.objects.filter(tour__id__in=filtered_tour_ids)
    
#         # چک کنیم آیا همه‌ی تورهای دیتابیس برگشتن یا نه
    
#     all_tour_ids = set(Tour.objects.values_list('id', flat=True))
#     filtered_tour_ids = set(t.id for t in filtered_tours)

#     if filtered_tour_ids == all_tour_ids:
#         # همه تورها برگشتن، یعنی فیلتر معنا نداشته، پس خروجی خالی میدیم
#         return [], []
    
#     return filtered_tours, filtered_chunks




# # کد با لانگ چین




# # --------------------- مثال استفاده --------------------- #
# # if __name__ == "__main__":
# #     query = "  از 9 آذر تا 20 آذر ی تور میخوام  قیمتش بالای 2300 باشه و بین6 تا 7 شب هم باشه بیمه هم داشته باشه یا نداشته باشه مهم نیست ولی حتما خارجی باشه"
# #     # query = "گرون ترین  تور دبی"
# #     # query = " تور دبی"
# #     # query = " تور رو بده بهم"
# #     # query = "گرون ترین تور و ارزون ترین که داری کجاست؟"
# #     tours, chunks = get_chunks_for_query(query)
# #     # tours, chunks = get_chunks_for_query2()
# #     # print("🏷 تورهای فیلتر شده:")
# #     # for t in tours:
# #     #     print("-", t.name)

# #     # print("\n📝 چانک‌های مرتبط:")
# #     # for c in chunks:
# #     #     print("-", c.text)

