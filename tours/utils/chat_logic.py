# tours/utils/chat_logic.py
import traceback
from tours.utils.query_searcher import search_tour_chunks
from tours.utils.query_filter import get_chunks_for_query, safe_get_answer
import openai
# from django.conf import settings


# MODEL = "qwen/qwen3-235b-a22b:free"  # یا هر مدلی که استفاده می‌کنید
# MODEL = "google/gemini-2.0-flash-exp:free"
MODEL = "microsoft/mai-ds-r1:free" #خیلی 
# MODEL = "nvidia/llama-3.1-nemotron-ultra-253b-v1:free" #بد 
MODEL = "moonshotai/kimi-dev-72b:free" #خوب
# MODEL = "nousresearch/deephermes-3-llama-3-8b-preview:free"
MODEL = "google/gemma-3-27b-it:free"  #خیلی 

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

    # فیلتر و جستجوی تورها
    filtered_chunks = get_chunks_for_query(user_content)
    # filtered_chunks = []

    print("------------------------------filtered_chunks---------------------------")    
    print(filtered_chunks)    
    
    retrieved = search_tour_chunks(user_content, top_k=5)

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
    # prompt += " </think> را حذف کن از پاسخت و فارسی پاسخ بده"
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