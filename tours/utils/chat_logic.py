# tours/utils/chat_logic.py
import traceback
from tours.utils.query_searcher import search_tour_chunks
from tours.utils.query_filter import get_chunks_for_query
from tours.utils.rewrite_prompt import rewrite_query_with_context

import openai
# from django.conf import settings

# MODEL = "google/gemma-3-27b-it:free"  #خیلی  اینه اونی که اصلیه
# MODEL = "google/gemma-3n-e4b-it:free"


# MODEL = "qwen/qwen3-235b-a22b:free"  # یا هر مدلی که استفاده می‌کنید
# MODEL = "google/gemini-2.0-flash-exp:free"

# MODEL = "nvidia/llama-3.1-nemotron-ultra-253b-v1:free" #بد 
# MODEL = "moonshotai/kimi-dev-72b:free" #خوب
# MODEL = "nousresearch/deephermes-3-llama-3-8b-preview:free"
# MODEL = "google/gemma-3-27b-it:free"  #خیلی  اینه اونی که اصلیه
# MODEL = "tngtech/deepseek-r1t2-chimera:free"  #خوب
# MODEL = "microsoft/mai-ds-r1:free" # / خرراب / خیلی 
# MODEL = "meta-llama/llama-3.3-8b-instruct:free"
# MODEL = "qwen/qwen3-8b:free"


# openai.api_key = "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"
# openai.api_base = "https://openrouter.ai/api/v1" 

from openai import OpenAI

# --------------------- تنظیم کلاینت --------------------- #
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",  # کلید جدیدت رو اینجا بذار
    # api_key = "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", #zapas


)




def generate_assistant_response(chat_session, user_content):
    """
    chat_session: ChatSession instance
    user_content: متن پیام کاربر (string)
    
    باز می‌گرداند: متن پاسخ دستیار (string)
    """
    # تاریخچه گفتگو
    history = [f"{msg.role}: {msg.content}" for msg in chat_session.messages.all()]
    # print("\n history ------------------- \n ")
    # print(history)
    # print("\n \n ")
    # بازنویسی سوال فقط اگر هیستوری وجود داشته باشد
    # rewritten_query = user_content
    if len(history) > 1:
        rewritten_query = rewrite_query_with_context(
            user_content=user_content,
            history=history,
            use_model=True 
        )
    else:
        rewritten_query = user_content
    
# ============================================== user_content => rewritten_query
    print(f"\n \n $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ \n\n {rewritten_query} \n\n")

# ==============================
    # فیلتر و جستجوی تورها
    filtered_tours , filtered_chunks = get_chunks_for_query(rewritten_query)  # اینجا
    # filtered_chunks = []

    print("------------------------------filtered_chunks---------------------------")    
    print(filtered_chunks)    
    
    retrieved = search_tour_chunks(rewritten_query, top_faq=2, top_tour=5)      # اینجا

    print("------------------------------retrieved---------------------------")    
    print(retrieved)    

    # ساخت پرامپت
    prompt = "📌 لیست تورهای مرتبط موجود است. از اطلاعات زیر استفاده کن:\n\n"
    prompt += "✅ نتایج فیلتر:\n"
    for i, c in enumerate(filtered_chunks, 1):
        if hasattr(c, "text"):
            prompt += f"{i}. {c.text}\n"
        elif isinstance(c, dict) and "chunk" in c:
            prompt += f"{i}. {c['chunk'].text}\n"
        else:
            prompt += f"{i}. {str(c)}\n"

    prompt += "\n🔎 نتایج مشابهت:\n"
    for i, r in enumerate(retrieved, 1):
        chunk = r["chunk"] if isinstance(r, dict) else r
        prompt += f"{i}. {chunk.text}\n"

    prompt += "\n🕑 تاریخچه گفتگو:\n"
    for turn in history:
        prompt += f"- {turn}\n"

    prompt += f"\n❓ سوال جدید کاربر: {user_content}\n"

    # prompt += " حداکثر پاسخی که میدهی 150 توکن باشد اگر بیشتر شد خلاصه کن و پاسخ بده"
    prompt += "لطفاً پاسخ را حداکثر در 150 توکن بنویس، خیلی خلاصه و مفید، فقط نکات کلیدی را بگو، اگر چندین تور بود فقط نام و قیمت‌شان را به صورت لیست کوتاه بیاور."

    prompt += " به صورت طبیعی و روان اما خلاصه و مفید و کوتاه جواب بده، مثل یک دستیار سفر. اگر تور خاصی هست اسمشو بیار."
    # prompt += " اگر درباره ی جزییات یک تور پرسید تو تمام جزییات آن را(قیمت-هزینه-تاریخ و ساعت رفت و برگشت) بگو اگر اطلاعاتی نداشتی نگو اسم آن اطلاعات را "
    # prompt += " اگر درباره ی جزییات یک تور پرسید تو تمام جزییات آن را(قیمت-هزینه-تاریخ و ساعت رفت و برگشت) بگو  "
    # prompt += " اگر سوال در مورد تور خاصی نبود اطلاعات یک تور را الکی تکرار نکن "
    prompt += " اگر چندین تور خواسته بود پاسخت شامل لیستی خیلی خلاصه و کوتاه از همه ی تور های نتایج فیلتر شده باشد  "
    # prompt += " اگر چندین تور بود به صورت لیست بگو  "
    # prompt += " در تبدیل ماه تاریخ ها دقت کن ، ماه ها شمسی هستند مثلا YYYY/06/DD یعنی شهریور"
    prompt += "شمسی لطفا تاریخ‌ها را دقیقاً مثل این قالب شمسی (YYYY/MM/DD) نمایش بده و تبدیل به متن نکن."  
    prompt += " لینک‌ها قبلاً در اطلاعات تورها وجود دارند، آنها را عیناً کپی کن."
    prompt += " مثال: اگر اطلاعات تور شامل '<a href='http://localhost:5173/tours/tour_001'>تور کیش</a>' باشد، دقیقاً همین را در پاسخ بیاور."
    prompt += "اگر لینکی نبود یا ناقص بود اصلا ننویس که لینک موجود در پاسخت"
    prompt += "از enter ها برای جداسازی بخش های جوابت برای مرتب تر شدن استفاده کن"  

    print("------------------------------prompt---------------------------")    
    print(prompt)    
    
    
    
    
    # درخواست به LLM
    try:
        completion = client.chat.completions.create(
            # model = "google/gemma-3n-e4b-it:free",  # مدل مورد نظر
            # model = "deepseek/deepseek-r1-0528-qwen3-8b:free",
            # model = "qwen/qwen3-235b-a22b:free",
            # model = "qwen/qwen3-4b:free",
            # model = "qwen/qwen3-8b:free",
            # model = "qwen/qwen3-14b:free",
            
            # model = "mistralai/mistral-7b-instruct:free",
            # model = "google/gemma-2-9b-it:free",  # اخری اینبود
            
            # model = "x-ai/grok-4-fast:free", # حیلی خوب بعد llm
            
            # model = "deepseek/deepseek-chat-v3.1:free", # بد نیست
            # model = "microsoft/mai-ds-r1:free", # بد طول ارور
            # model = "openai/gpt-oss-20b:free", #  خرابه جواب نصفه
            
            # model = "meta-llama/llama-3.3-8b-instruct:free", #بد 
            # model = "meta-llama/llama-4-maverick:free",
            model = "meta-llama/llama-3.3-70b-instruct:free", #  کاملا درست خیلی خوب
            
            # model ="mistralai/mistral-nemo:free",
            # model = "google/gemma-3-27b-it:free",
            # model = "google/gemma-3-12b-it:free" ,
            # model = "google/gemini-2.0-flash-exp:free",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.3,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        traceback.print_exc()
        answer = f"❌ خطا در دریافت پاسخ از مدل: {str(e)}"
    
    print("------------------------------prompt---------------------------")    

    print(answer)
    return answer





#shakina jadida
# openai.api_key = "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"
# opneai.api_key = "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"