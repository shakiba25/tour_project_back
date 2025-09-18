# tours/utils/chat_logic.py
import traceback
from tours.utils.query_searcher import search_tour_chunks
from tours.utils.query_filter import get_chunks_for_query, safe_get_answer
from tours.utils.rewrite_prompt import rewrite_query_with_context

import openai
# from django.conf import settings

MODEL = "google/gemma-3-27b-it:free"  #خیلی  اینه اونی که اصلیه
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


openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1" 

def generate_assistant_response(chat_session, user_content):
    """
    chat_session: ChatSession instance
    user_content: متن پیام کاربر (string)
    
    باز می‌گرداند: متن پاسخ دستیار (string)
    """
    # تاریخچه گفتگو
    history = [f"{msg.role}: {msg.content}" for msg in chat_session.messages.all()]

    # بازنویسی سوال فقط اگر هیستوری وجود داشته باشد
    # rewritten_query = user_content
    if history:
        rewritten_query = rewrite_query_with_context(
            user_content=user_content,
            history=history,
            use_model=True  # اگه می‌خوای بدون GPT باشه بذار False
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
    
    retrieved = search_tour_chunks(rewritten_query, top_k=5)      # اینجا

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
    prompt += " به صورت طبیعی و روان جواب بده، مثل یک دستیار سفر. جواب رو کوتاه و ساده نگه دار تا به محدودیت توکن نخوری. اگر تور خاصی هست اسمشو بیار."
    # prompt += " اگر درباره ی جزییات یک تور پرسید تو تمام جزییات آن را(قیمت-هزینه-تاریخ و ساعت رفت و برگشت) بگو اگر اطلاعاتی نداشتی نگو اسم آن اطلاعات را "
    prompt += " اگر درباره ی جزییات یک تور پرسید تو تمام جزییات آن را(قیمت-هزینه-تاریخ و ساعت رفت و برگشت) بگو  "
    # prompt += " در تبدیل ماه تاریخ ها دقت کن ، ماه ها شمسی هستند مثلا YYYY/06/DD یعنی شهریور"
    prompt += " لطفا تاریخ‌ها را دقیقاً مثل این قالب (YYYY/MM/DD) نمایش بده و تبدیل به متن نکن."  
    print("------------------------------prompt---------------------------")    
    print(prompt)    
    
    # درخواست به LLM
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
            top_p=1,
        )
        answer = safe_get_answer(response)
    except Exception as e:
        traceback.print_exc()
        answer = f"❌ خطا در دریافت پاسخ از مدل: {str(e)}"
    
    print("------------------------------prompt---------------------------")    

    print(answer)
    return answer





#shakina jadida
# openai.api_key = "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"