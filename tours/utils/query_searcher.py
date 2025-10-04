# tours/utils/query_searcher.py
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")

import django
django.setup()


import numpy as np
from sentence_transformers import SentenceTransformer
from tours.utils.embedder import MODEL_PATH
from tours.utils.index_manager import load_tour_index , load_faq_index
from tours.models import Chunk, FAQChunk
# from model_embedder import get_model

# model = get_model()
model = SentenceTransformer(MODEL_PATH, trust_remote_code=True)

def search_tour_chunks(query, top_faq=2, top_tour=5):
    # لود ایندکس‌ها
    tour_index, tour_chunk_ids = load_tour_index()
    faq_index, faq_chunk_ids = load_faq_index()

    # بردار query
    query_vec = model.encode([query], convert_to_numpy=True)
    query_vec = query_vec / np.linalg.norm(query_vec, axis=1, keepdims=True)

    results = []

    # --- جستجو در FAQ (۲ تا) ---
    D_faq, I_faq = faq_index.search(query_vec, top_faq)
    for score, idx in zip(D_faq[0], I_faq[0]):
        if idx == -1:
            continue
        chunk_id = faq_chunk_ids[idx]
        chunk = FAQChunk.objects.get(id=chunk_id)
        results.append({
            "chunk": chunk,
            "similarity": float(score),
            "type": "faq"
        })

    # --- جستجو در تور (۵ تا) ---
    D_tour, I_tour = tour_index.search(query_vec, top_tour)
    for score, idx in zip(D_tour[0], I_tour[0]):
        if idx == -1:
            continue
        chunk_id = tour_chunk_ids[idx]
        chunk = Chunk.objects.get(id=chunk_id)
        results.append({
            "chunk": chunk,
            "similarity": float(score),
            "type": "tour"
        })

    return results

if __name__ == "__main__":
    query = "ی تور میخوام بازار گردی داشته باشه"
    results = search_tour_chunks(query)
    for r in results:
        print(f"{r['chunk'].text} (score: {r['similarity']:.4f}) (type: {r['type']})")


# نتایج

# ✅ ایندکس تور از فایل لود شد.
# ✅ ایندکس FAQ از فایل لود شد.
# سوال: چگونه می‌توانم تورهای آینده را پیگیری کنم؟
# پاسخ: جدیدترین تورها در صفحه تورهای ما لیست می‌شوند. می‌توانید با دنبال کردن وبسایت، از تورهای آینده مطلع شوید. (score: 0.5732) (type: fa aq)
# سوال: چگونه می‌توانم تورهای شما را مشاهده کنم؟
# پاسخ: تمام تورهای موجود در <a href='http://localhost:5173/tours'>صفحه تورها</a> لیست شده‌اند و می‌توانید با کلیک روی هر تور، اطلاعات کامل ل آن از جمله مقصد، مدت، هتل، پرواز و خدمات را مشاهده کنید. (score: 0.5607) (type: faq)
# برنامه سفر تور ۵ روزه استانبول (استانبول):
# روز اول: بازدید از مسجد آبی و ایاصوفیه
# روز دوم: کاخ توپکاپی و بازار بزرگ
# روز سوم: تنگه بسفر و برج گالاتا
# روز چهارم: پارک امیرگان و جزیره پرنسس
# روز پنجم: خرید در خیابان استقلال (score: 0.5244) (type: tour)
# برنامه سفر تور ۲ روزه مشهد (مشهد):
# روز اول: زیارت حرم امام رضا (ع)
# روز دوم: بازار رضا و پارک کوهسنگی (score: 0.5110) (type: tour)
# برنامه سفر تور ۴ روزه تبریز (تبریز):
# روز اول: بازدید از بازار بزرگ تبریز
# روز دوم: موزه قاجار و عمارت شهرداری
# روز سوم: پارک ائل گلی و باغ گلستان
# روز چهارم: کلیسای کاتولیک و خانه مشروطه (score: 0.5036) (type: tour)
# برنامه سفر تور ۳ روزه کیش (کیش):
# روز اول: بازدید از شهر تاریخی حریره
# روز دوم: ساحل مرجانی و کشتی یونانی
# روز سوم: بازارهای محلی و خرید (score: 0.4721) (type: tour)
# برنامه سفر تور ۲ روزه تهران گردی (تهران):
# روز اول: بازدید از کاخ گلستان و بازار تجریش
# روز دوم: برج میلاد و پارک آب و آتش (score: 0.4690) (type: tour)




# def search_tour_chunks(query, top_k=5):

#     index, chunk_ids = load_tour_index()

#     query_vec = model.encode([query], convert_to_numpy=True)
#     query_vec = query_vec / np.linalg.norm(query_vec, axis=1, keepdims=True)

#     D, I = index.search(query_vec, top_k)  # D: similarity, I: index

#     results = []
#     for score, idx in zip(D[0], I[0]):
#         chunk_id = chunk_ids[idx]
#         chunk = Chunk.objects.get(id=chunk_id)
#         results.append({
#             "chunk": chunk,
#             "similarity": float(score)
#         })

#     return results

# if __name__ == "__main__":
#     query = "تور ژاپن و معابد"
#     results = search_tour_chunks(query)
#     for r in results:
#         print(f"{r['chunk'].text} (score: {r['similarity']:.4f})")










# الان دیگه اینجوری خطای ایندکس نمیدیم؟

# from django.core.management.base import BaseCommand
# from tours.utils.chunker import create_and_save_chunks, create_faq_chunks
# from tours.utils.embedder import rebuild_tour_index, rebuild_faq_index
# from tours.models import Chunk, ChunkEmbedding, FAQChunk, FAQChunkEmbedding, Tour, FAQ

# class Command(BaseCommand):
#     help = "بازسازی ایندکس‌ها: تور و FAQ"

#     def add_arguments(self, parser):
#         parser.add_argument(
#             "--tour", action="store_true", help="بازسازی ایندکس تور"
#         )
#         parser.add_argument(
#             "--faq", action="store_true", help="بازسازی ایندکس FAQ"
#         )

#     def handle(self, *args, **options):
#         if options["tour"]:
#             rebuild_tour_index()
#         if options["faq"]:
#             rebuild_faq_index()
#         if not options["tour"] and not options["faq"]:
#             self.stdout.write("⚠️ هیچ گزینه‌ای مشخص نشده، لطفا --tour یا --faq را اضافه کنید.")

# # tours/utils/embedder.py

# # import sys
# # import os

# # BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# # sys.path.append(BASE_DIR)
# # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")

# # import django
# # # django.setup()

# import os
# import pickle
# import numpy as np
# import faiss
# from sentence_transformers import SentenceTransformer
# from tours.models import FAQ, Chunk, ChunkEmbedding , FAQChunk, FAQChunkEmbedding, Tour
# from tours.utils.chunker import create_and_save_chunks, create_faq_chunks
# # -------------------------------
# # مسیر مدل و ایندکس‌ها
# # -------------------------------
# MODEL_PATH = r"C:\Users\Asus\Desktop\test t5\models\xmaniimaux-gte-persian-v3-fp16"

# INDEX_PATH_TOUR = "tour_chunks_xmaniimaux_v3.faiss"
# META_PATH_TOUR = "tour_chunks_metadata.pkl"

# INDEX_PATH_FAQ = "faq_chunks_xmaniimaux_v3.faiss"
# META_PATH_FAQ = "faq_chunks_metadata.pkl"

# # -------------------------------
# # بارگذاری مدل
# # -------------------------------
# model = SentenceTransformer(MODEL_PATH, trust_remote_code=True)

# # -------------------------------
# # توابع مشترک
# # -------------------------------

# def safe_remove(path):
#     """اگر فایل وجود داشت پاک کن"""
#     if os.path.exists(path):
#         os.remove(path)
        
        
# def embed_chunks(chunks):
#     """ایجاد embedding برای لیست چانک‌ها و بازگشت numpy array و شناسه‌ها"""
#     texts = [chunk.text for chunk in chunks]
#     embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
#     faiss.normalize_L2(embeddings)
#     ids = [chunk.id for chunk in chunks]
#     return embeddings, ids

# def save_embeddings_to_db(chunks, embeddings, is_faq=False):
#     """ذخیره embeddingها در DB"""
#     ModelClass = FAQChunkEmbedding if is_faq else ChunkEmbedding
#     for chunk, vector in zip(chunks, embeddings):
#         ModelClass.objects.update_or_create(
#             chunk=chunk,
#             defaults={"vector": vector.tobytes()}
#         )

# def save_metadata(ids, meta_path):
#     with open(meta_path, "wb") as f:
#         pickle.dump(ids, f)

# def build_faiss_index(embeddings, ids, index_path):
#     dim = embeddings.shape[1]
#     index = faiss.IndexIDMap(faiss.IndexFlatIP(dim))  # برای remove_ids
#     index.add_with_ids(embeddings, np.array(ids))
#     faiss.write_index(index , index_path)
#     return index

# # -------------------------------
# # بازسازی ایندکس تور
# # -------------------------------
# def rebuild_tour_index():
#     # حذف فایل‌های قدیمی
#     safe_remove(INDEX_PATH_TOUR)
#     safe_remove(META_PATH_TOUR)

#     # حذف embedding و چانک‌های قدیمی
#     ChunkEmbedding.objects.all().delete()
#     Chunk.objects.all().delete()

#     # ساخت چانک‌ها
#     tours = Tour.objects.all()
#     for tour in tours:
#         create_and_save_chunks(tour)

#     # ساخت embeddings و ایندکس FAISS
#     chunks = Chunk.objects.all()
#     embeddings, ids = embed_chunks(chunks)
#     save_embeddings_to_db(chunks, embeddings)
#     build_faiss_index(embeddings, ids, INDEX_PATH_TOUR)
#     save_metadata(ids, META_PATH_TOUR)
#     print("✅ ایندکس تور بازسازی شد.")

# # -------------------------------
# # بازسازی ایندکس FAQ
# # -------------------------------
# def rebuild_faq_index():
    
#     safe_remove(INDEX_PATH_FAQ)
#     safe_remove(META_PATH_FAQ)
    
#     # حذف embedding و چانک‌های قدیمی
#     FAQChunkEmbedding.objects.all().delete()
#     FAQChunk.objects.all().delete()

#     # ساخت چانک‌ها
#     fqas = FAQ.objects.all()
#     for fqa in fqas:
#         create_faq_chunks(fqa)
    
    
#     chunks = FAQChunk.objects.all()
#     if not chunks.exists():
#         print("⚠️ چانکی برای FAQ یافت نشد.")
#         return
#     embeddings, ids = embed_chunks(chunks)
#     save_embeddings_to_db(chunks, embeddings, is_faq=True)
#     build_faiss_index(embeddings, ids, INDEX_PATH_FAQ)
#     save_metadata(ids, META_PATH_FAQ)
#     print("✅ ایندکس FAQ بازسازی شد.")

# # -------------------------------
# # اجرای مستقیم
# # -------------------------------
# if __name__ == "__main__":
#     print("شروع بازسازی ایندکس‌ها...")
#     rebuild_tour_index()
#     rebuild_faq_index()
#     print("✅ همه ایندکس‌ها ساخته شدند.")

# # tours/utils/query_searcher.py
# import sys
# import os

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(BASE_DIR)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")

# import django
# django.setup()


# import numpy as np
# from sentence_transformers import SentenceTransformer
# from tours.utils.embedder import MODEL_PATH
# from tours.utils.index_manager import load_tour_index , load_faq_index
# from tours.models import Chunk
# # from model_embedder import get_model

# # model = get_model()
# model = SentenceTransformer(MODEL_PATH, trust_remote_code=True)

# def search_tour_chunks(query, top_k=5):
#     """
#     جستجو در هر دو ایندکس: تور و FAQ
#     برگرداندن top_k نتیجه مشابه‌ترین چانک‌ها
#     """
#     # --- لود ایندکس تور ---
#     tour_index, tour_chunk_ids = load_tour_index()
#     # --- لود ایندکس FAQ ---
#     faq_index, faq_chunk_ids = load_faq_index()

#     # --- بردار query ---
#     query_vec = model.encode([query], convert_to_numpy=True)
#     query_vec = query_vec / np.linalg.norm(query_vec, axis=1, keepdims=True)

#     results = []

#     # --- جستجو در ایندکس تور ---
#     D_tour, I_tour = tour_index.search(query_vec, top_k)
#     for score, idx in zip(D_tour[0], I_tour[0]):
#         chunk = Chunk.objects.get(id=tour_chunk_ids[idx])
#         results.append({
#             "chunk": chunk,
#             "similarity": float(score),
#             "type": "tour"
#         })

#     # --- جستجو در ایندکس FAQ ---
#     D_faq, I_faq = faq_index.search(query_vec, top_k)
#     for score, idx in zip(D_faq[0], I_faq[0]):
#         chunk = Chunk.objects.get(id=faq_chunk_ids[idx])
#         results.append({
#             "chunk": chunk,
#             "similarity": float(score),
#             "type": "faq"
#         })

#     # --- مرتب‌سازی بر اساس شباهت و گرفتن top_k کل ---
#     results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_k]

#     return results

# if __name__ == "__main__":
#     query = "تور برای کودکان میخوام"
#     results = search_tour_chunks(query)
#     for r in results:
#         print(f"{r['chunk'].text} (score: {r['similarity']:.4f}) (type: {r['type']})")






