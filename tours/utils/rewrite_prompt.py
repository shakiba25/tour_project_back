import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")

import django
django.setup()


import openai


# --------------------- تنظیم OpenAI --------------------- #
openai.api_key = "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"  # <<-- کلیدت اینجا
openai.api_base = "https://openrouter.ai/api/v1"


model = "qwen/qwen3-235b-a22b:free"  # محشرهههه
# model = "openrouter/horizon-beta" # اینم عالیه
# model = "deepseek/deepseek-r1-0528:free"
# model = "z-ai/glm-4.5-air:free"
# model = "google/gemma-3n-e4b-it:free"
# model = "mistralai/mistral-7b-instruct"

# model = "moonshotai/kimi-k2:free"

def rewrite_query_with_context(user_content, history, use_model=True):
    """
    سوال کاربر رو با توجه به تاریخچه گفتگو بازنویسی می‌کنه.
    
    - history: لیست پیام‌های قبلی گفتگو (مثل ["user: ...", "assistant: ..."])
    - use_model: اگر True باشه بازنویسی با مدل LLM انجام می‌شه
    """
    if not use_model:
        return user_content

    history_str = "\n".join(history[-4:])

    prompt = f"""کاربر در یک گفتگوی سفر است. سوال آخرش را بازنویسی کن به طوری که مستقل و واضح باشد و نیازی به سوالات قبلی نداشته باشد.

🕑 تاریخچه گفتگو:
{history_str}

❓ سوال آخر:
{user_content}

🔁 بازنویسی واضح:"""

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("⚠️ خطا در بازنویسی با مدل:", e)
        return user_content  # fallback




# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch

# # بارگذاری مدل و توکنایزر از مسیر محلی
# model_path = r"C:\Users\Asus\Desktop\test t5\models\bloomz-1b1"
# tokenizer = AutoTokenizer.from_pretrained(model_path)
# model = AutoModelForCausalLM.from_pretrained(model_path)
# model.eval()  # حالت ارزیابی

# def rewrite_query_with_context(user_content, history, use_model=True):
#     """
#     سوال کاربر رو با توجه به تاریخچه گفتگو بازنویسی می‌کنه.
    
#     - history: لیست پیام‌های قبلی گفتگو (مثل ["user: ...", "assistant: ..."])
#     - use_model: اگر True باشه بازنویسی با مدل LLM انجام می‌شه
#     """
#     if not use_model:
#         return user_content

#     history_str = "\n".join(history[-4:])

#     prompt = f"""کاربر در یک گفتگوی سفر است. سوال آخرش را بازنویسی کن به طوری که مستقل و واضح باشد و نیازی به سوالات قبلی نداشته باشد.

# 🕑 تاریخچه گفتگو:
# {history_str}

# ❓ سوال آخر:
# {user_content}

# 🔁 بازنویسی واضح:"""

#     # توکنایز و تبدیل به tensor
#     inputs = tokenizer(prompt, return_tensors="pt")
    
#     # خروجی مدل (تولید متن)
#     with torch.no_grad():
#         outputs = model.generate(
#             **inputs,
#             max_new_tokens=100,
#             do_sample=True,
#             temperature=0.3,
#             top_p=0.9,
#             eos_token_id=tokenizer.eos_token_id,
#             pad_token_id=tokenizer.pad_token_id
#         )
    
#     # دیکد کردن پاسخ
#     generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
#     # جدا کردن پاسخ از prompt (ممکنه بخوای دقیق‌تر جدا کنی)
#     answer = generated_text[len(prompt):].strip()

#     return answer


# # ----------mt5--------------------------------------------------------------------------


# from transformers import MT5Tokenizer, TFMT5ForConditionalGeneration
# import tensorflow as tf

# # مسیر مدل
# model_path = r"C:\Users\Asus\Desktop\test t5\models\mt5-large"

# # بارگذاری توکنایزر و مدل (TensorFlow)
# tokenizer = MT5Tokenizer.from_pretrained(model_path)
# model = TFMT5ForConditionalGeneration.from_pretrained(model_path)

# def rewrite_query_with_context(user_content, history, use_model=True):
#     """
#     بازنویسی سوال با توجه به تاریخچه گفتگو توسط مدل MT5 (TensorFlow)

#     پارامترها:
#     - user_content (str): سوال کاربر
#     - history (list of str): تاریخچه پیام‌ها (مثل ["user: ...", "assistant: ..."])
#     - use_model (bool): اگر False باشه همون سوال اصلی رو برمی‌گردونه

#     خروجی:
#     - str: سوال بازنویسی‌شده یا سوال اصلی
#     """
#     if not use_model:
#         return user_content

#     # ترکیب تاریخچه و سوال برای ساخت پرامپت
#     history_str = "\n".join(history[-4:])  # آخرین ۴ پیام
#     prompt = f"rewrite this user query independently based on the following chat history.\n\nhistory:\n{history_str}\n\nquestion:\n{user_content}\n\nrewritten question:"

#     # تبدیل به توکن‌ها (max length رعایت شود)
#     inputs = tokenizer(prompt, return_tensors="tf", max_length=512, truncation=True, padding="max_length")

#     # تولید پاسخ
#     outputs = model.generate(
#         input_ids=inputs["input_ids"],
#         attention_mask=inputs["attention_mask"],
#         max_length=100,
#         num_beams=4,
#         no_repeat_ngram_size=2,
#         early_stopping=True
#     )

#     # دیکد کردن پاسخ
#     rewritten = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
#     return rewritten


# # ----------flan--------------------------------------------------------------------------


# from transformers import T5ForConditionalGeneration, T5Tokenizer
# import torch

# # مسیر مدل
# model_path = r"C:\Users\Asus\Desktop\project-final\medical\models\flan-t5-base"

# # بارگذاری مدل و توکنایزر
# tokenizer = T5Tokenizer.from_pretrained(model_path)
# model = T5ForConditionalGeneration.from_pretrained(model_path)

# # انتقال به GPU اگر موجود باشد
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = model.to(device)
# model.eval()

# def rewrite_query_with_context3(user_content, history, use_model=True):
#     """
#     سوال کاربر رو با توجه به تاریخچه گفتگو بازنویسی می‌کنه.
    
#     پارامترها:
#         user_content (str): سوال آخر کاربر
#         history (list of str): تاریخچه گفتگو (مثلا ["user: ...", "assistant: ..."])
#         use_model (bool): اگر True باشه، از مدل FLAN-T5 استفاده می‌کنه وگرنه سوال رو بدون تغییر برمی‌گردونه
    
#     خروجی:
#         str: سوال بازنویسی شده یا اصلی
#     """

#     if not use_model:
#         return user_content

#     # فقط ۴ پیام آخر تاریخچه
#     history_str = "\n".join(history[-4:])

#     prompt = f"""Rewrite the user's last question clearly and independently, so it doesn't need previous context.
# Conversation history:
# {history_str}

# Last question:
# {user_content}

# Clear rewritten question:"""

#     # توکنایز کردن ورودی
#     inputs = tokenizer(
#         prompt,
#         return_tensors="pt",
#         max_length=512,
#         truncation=True,
#         padding="max_length"
#     ).to(device)

#     # تولید پاسخ با beam search
#     with torch.no_grad():
#         outputs = model.generate(
#             input_ids=inputs["input_ids"],
#             attention_mask=inputs["attention_mask"],
#             max_length=100,
#             num_beams=4,
#             no_repeat_ngram_size=2,
#             early_stopping=True
#         )

#     rewritten_question = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
#     return rewritten_question