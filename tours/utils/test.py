import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")

import django
django.setup()


from tours.utils.rewrite_prompt import rewrite_query_with_context

# هیستوری گفتگو
history = [
    "user: تور ۳ روزه کیش داری؟",
    "assistant: بله، تور ۳ روزه کیش داریم با پرواز ماهان و اقامت در هتل ترنج.",
    "user: قیمتش چنده؟",
    "assistant: حدود ۲۰۰ دلار با پرواز رفت و برگشت و خدمات کامل."
]

# سوال جدید
user_content = "ساعت پرواز چنده؟"


# صدا زدن تابع
rewritten = rewrite_query_with_context(
    user_content=user_content,
    history=history,
    use_model=True  # استفاده از مدل
)

print("✅ سوال بازنویسی‌شده:\n", rewritten)
