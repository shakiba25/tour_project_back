# import sys
# import os
# import django
# import openai
# import tkinter as tk
# from tkinter import scrolledtext

# # ---------------- Django Setup ----------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(BASE_DIR)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")
# django.setup()

# # ---------------- OpenAI Config ----------------
# openai.api_key = "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"
# openai.api_base = "https://openrouter.ai/api/v1"
# MODEL = "qwen/qwen3-235b-a22b:free"
# # MODEL = "openai/gpt-oss-20b:free"
# # MODEL = "tngtech/deepseek-r1t2-chimera:free"
# # MODEL = "deepseek/deepseek-r1-0528:free"
# # MODEL = "z-ai/glm-4.5-air:free"
# # MODEL = "moonshotai/kimi-vl-a3b-thinking:free"
# MODEL = "google/gemini-2.0-flash-exp:free"
# from tours.utils.query_searcher import search_tour_chunks
# from tours.utils.query_filter import get_chunks_for_query

# def build_and_answer(user_query, filtered_chunks, retrieved, history):
#     prompt = "📌 لیست تورهای مرتبط موجود است. از اطلاعات زیر استفاده کن:\n\n"
#     prompt += "✅ نتایج فیلتر:\n"
#     for i, c in enumerate(filtered_chunks, 1):
#         if hasattr(c, "text"):
#             prompt += f"{i}. {c.text}\n"
#         elif isinstance(c, dict) and "chunk" in c:
#             prompt += f"{i}. {c['chunk'].text}\n"
#         else:
#             prompt += f"{i}. {str(c)}\n"
#     prompt += "\n🔎 نتایج مشابهت:\n"
#     for i, r in enumerate(retrieved, 1):
#         chunk = r["chunk"] if isinstance(r, dict) else r
#         prompt += f"{i}. {chunk.text}\n"
#     prompt += "\n🕑 تاریخچه گفتگو:\n"
#     for turn in history:
#         prompt += f"- {turn}\n"
#     prompt += f"\n❓ سوال جدید کاربر: {user_query}\n"
#     prompt += "به صورت طبیعی و روان جواب بده، مثل یک دستیار سفر. جواب رو کوتاه و ساده نگه دار. اگر تور خاصی هست اسمشو بیار."

#     # اینجا درخواست به مدل می‌فرستیم
#     try:
#         response = openai.ChatCompletion.create(
#             model=MODEL,
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=500,
#             temperature=0.7,
#             top_p=1,
#             n=1,
#             stop=None,
#         )
#         answer = response.choices[0].message.content.strip()
#     except Exception as e:
#         answer = f"خطا در دریافت پاسخ از مدل: {str(e)}"

#     return answer

# class ChatApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("چت بات تور")
#         self.history = []

#         # Text box برای نمایش گفتگو
#         self.chat_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
#         self.chat_log.pack(padx=10, pady=10)
#         self.chat_log.config(state=tk.DISABLED)

#         # ورودی سوال
#         self.entry = tk.Entry(root, width=80)
#         self.entry.pack(padx=10, pady=(0,10))
#         self.entry.bind("<Return>", self.send_query)

#         # دکمه ارسال
#         self.send_button = tk.Button(root, text="ارسال", command=self.send_query)
#         self.send_button.pack(padx=10, pady=(0,10))

#         self.write_chat("🤖 چت بات آماده است! سوال خود را وارد کنید. برای خروج 'exit' بنویسید.\n")

#     def write_chat(self, text):
#         self.chat_log.config(state=tk.NORMAL)
#         self.chat_log.insert(tk.END, text + "\n")
#         self.chat_log.see(tk.END)
#         self.chat_log.config(state=tk.DISABLED)

#     def send_query(self, event=None):
#         query = self.entry.get().strip()
#         if not query:
#             return
#         self.entry.delete(0, tk.END)

#         if query.lower() in ["exit", "quit"]:
#             self.write_chat("👋 پایان گفتگو.")
#             self.root.after(2000, self.root.destroy)
#             return

#         self.write_chat(f"❓ پرسش: {query}")
#         print(query)
#         filtered_tours, filtered_chunks = get_chunks_for_query(query)
#         retrieved = search_tour_chunks(query, top_k=5)
#         answer = build_and_answer(query, filtered_chunks, retrieved, self.history)

#         self.write_chat(f"💬 پاسخ:\n{answer}")
#         print(f"💬 پاسخ:\n{answer}")
#         self.write_chat("-" * 50)

#         self.history.append(f"کاربر: {query}")
#         self.history.append(f"دستیار: {answer}")

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = ChatApp(root)
#     root.mainloop()

import sys
import os
import django
import openai
import tkinter as tk
from tkinter import scrolledtext

# ---------------- Django Setup ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")
django.setup()

# ---------------- OpenAI Config ----------------
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"
MODEL = "qwen/qwen3-235b-a22b:free"
# MODEL = "openai/gpt-oss-20b:free"
# MODEL = "tngtech/deepseek-r1t2-chimera:free"
# MODEL = "deepseek/deepseek-r1-0528:free"
# MODEL = "z-ai/glm-4.5-air:free"
# MODEL = "moonshotai/kimi-vl-a3b-thinking:free"
# MODEL = "google/gemini-2.0-flash-exp:free"
from tours.utils.query_searcher import search_tour_chunks
from tours.utils.query_filter import get_chunks_for_query , safe_get_answer

def build_and_answer(user_query, filtered_chunks, retrieved, history):
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
    prompt += f"\n❓ سوال جدید کاربر: {user_query}\n"
    prompt += "به صورت طبیعی و روان جواب بده، مثل یک دستیار سفر. جواب رو کوتاه و ساده نگه دار. اگر تور خاصی هست اسمشو بیار."

    # اینجا درخواست به مدل می‌فرستیم
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
            top_p=1,
            n=1,
            stop=None,
        )
        answer = safe_get_answer(response)
        # answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"خطا در دریافت پاسخ از مدل: {str(e)}"

    return answer


from tours.models import ChatSession, ChatMessage
from django.contrib.auth.models import User

class ChatApp:
    def __init__(self, root, user=None):
        self.root = root
        self.root.title("چت بات تور")

        # 🟢 پیدا کردن یا ساخت سشن فعال
        if user:
            self.session, created = ChatSession.objects.get_or_create(user=user, is_active=True)
        else:
            self.session = ChatSession.objects.create(user=None, is_active=True)

        # بارگذاری تاریخچه از دیتابیس
        self.history = [f"{msg.role}: {msg.content}" for msg in self.session.messages.all()]

        # UI
        self.chat_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
        self.chat_log.pack(padx=10, pady=10)
        self.chat_log.config(state=tk.DISABLED)

        self.entry = tk.Entry(root, width=80)
        self.entry.pack(padx=10, pady=(0,10))
        self.entry.bind("<Return>", self.send_query)

        self.send_button = tk.Button(root, text="ارسال", command=self.send_query)
        self.send_button.pack(padx=10, pady=(0,10))

        self.write_chat("🤖 چت بات آماده است! سوال خود را وارد کنید. برای خروج 'exit' بنویسید.\n")

    def write_chat(self, text):
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, text + "\n")
        self.chat_log.see(tk.END)
        self.chat_log.config(state=tk.DISABLED)

    def send_query(self, event=None):
        query = self.entry.get().strip()
        if not query:
            return
        self.entry.delete(0, tk.END)

        if query.lower() in ["exit", "quit"]:
            self.write_chat("👋 پایان گفتگو.")
            self.session.is_active = False
            self.session.save()
            self.root.after(2000, self.root.destroy)
            return

        # 🟢 ذخیره پرسش کاربر
        ChatMessage.objects.create(session=self.session, role="user", content=query)
        self.write_chat(f"❓ پرسش: {query}")

        # پاسخ
        filtered_tours, filtered_chunks = get_chunks_for_query(query)
        retrieved = search_tour_chunks(query, top_k=5)
        answer = build_and_answer(query, filtered_chunks, retrieved, self.history)

        # 🟢 ذخیره پاسخ دستیار
        ChatMessage.objects.create(session=self.session, role="assistant", content=answer)

        self.write_chat(f"💬 پاسخ:\n{answer}")
        self.write_chat("-" * 50)

        self.history.append(f"کاربر: {query}")
        self.history.append(f"دستیار: {answer}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()