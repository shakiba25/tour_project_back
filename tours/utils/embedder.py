# tours/utils/embedder.py

# import sys
# import os

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(BASE_DIR)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")

# import django
# # django.setup()

import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from tours.models import FAQ, Chunk, ChunkEmbedding , FAQChunk, FAQChunkEmbedding, Tour
from tours.utils.chunker import create_and_save_chunks, create_faq_chunks


# مسیر مدل و ایندکس‌ها
# -------------------------------
MODEL_PATH = r"C:\Users\Asus\Desktop\test t5\models\xmaniimaux-gte-persian-v3-fp16"

INDEX_PATH_TOUR = "tour_chunks_xmaniimaux_v3.faiss"
META_PATH_TOUR = "tour_chunks_metadata.pkl"

INDEX_PATH_FAQ = "faq_chunks_xmaniimaux_v3.faiss"
META_PATH_FAQ = "faq_chunks_metadata.pkl"


# بارگذاری مدل
# -------------------------------
model = SentenceTransformer(MODEL_PATH, trust_remote_code=True)


# توابع مشترک
# -------------------------------

def safe_remove(path):
    """اگر فایل چنین مسیری وجود داشت پاک میشود"""
    
    if os.path.exists(path):
        os.remove(path)
        
        
def embed_chunks(chunks):
    """ایجاد embedding برای لیست چانک‌ها و بازگشت numpy array و شناسه‌ها"""
    
    texts = [chunk.text for chunk in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    faiss.normalize_L2(embeddings)
    ids = [chunk.id for chunk in chunks]
    return embeddings, ids


def save_embeddings_to_db(chunks, embeddings, is_faq=False):
    """ذخیره embeddingها در DB"""
    ModelClass = FAQChunkEmbedding if is_faq else ChunkEmbedding
    for chunk, vector in zip(chunks, embeddings):
        ModelClass.objects.update_or_create(
            chunk=chunk,
            defaults={"vector": vector.tobytes()}
        )

def build_faiss_index(embeddings, index_path):
    dim = embeddings.shape[1] #768
    index = faiss.IndexFlatIP(dim)   # ساده و بدون id
    index.add(embeddings)
    faiss.write_index(index, index_path)
    return index

def save_metadata(ids, meta_path):
    with open(meta_path, "wb") as f:
        pickle.dump(ids, f)


# بازسازی ایندکس تور
# -------------------------------
def rebuild_tour_index():
    # حذف فایل‌های قدیمی
    safe_remove(INDEX_PATH_TOUR)
    safe_remove(META_PATH_TOUR)

    # حذف embedding و چانک‌های قدیمی
    ChunkEmbedding.objects.all().delete()
    Chunk.objects.all().delete()

    # ساخت چانک‌ها
    tours = Tour.objects.all()
    for tour in tours:
        create_and_save_chunks(tour)

    # ساخت embeddings و ایندکس FAISS
    chunks = Chunk.objects.all()
    embeddings, ids = embed_chunks(chunks)
    save_embeddings_to_db(chunks, embeddings)
    build_faiss_index(embeddings, INDEX_PATH_TOUR)
    save_metadata(ids, META_PATH_TOUR)
    print("✅ ایندکس تور بازسازی شد.")


# بازسازی ایندکس FAQ
# -------------------------------
def rebuild_faq_index():
    
    safe_remove(INDEX_PATH_FAQ)
    safe_remove(META_PATH_FAQ)
    
    # حذف embedding و چانک‌های قدیمی
    FAQChunkEmbedding.objects.all().delete()
    FAQChunk.objects.all().delete()

    # ساخت چانک‌ها
    create_faq_chunks()
    
    
    chunks = FAQChunk.objects.all()
    if not chunks.exists():
        print(" چانکی برای FAQ یافت نشد.")
        return
    embeddings, ids = embed_chunks(chunks)
    save_embeddings_to_db(chunks, embeddings, is_faq=True)
    build_faiss_index(embeddings, INDEX_PATH_FAQ)
    save_metadata(ids, META_PATH_FAQ)
    print("✅ ایندکس FAQ بازسازی شد.")


# اجرای مستقیم
# -------------------------------
if __name__ == "__main__":
    print("شروع بازسازی ایندکس‌ها...")
    rebuild_tour_index()
    rebuild_faq_index()
    print("✅ همه ایندکس‌ها ساخته شدند.")




# # from load_model import model

# MODEL_PATH = r"C:\Users\Asus\Desktop\test t5\models\xmaniimaux-gte-persian-v3-fp16"
# INDEX_PATH = "tour_chunks_xmaniimaux_v3.faiss"
# META_PATH = "tour_chunks_metadata.pkl"
# INDEX_PATH_FAQ = "faq_chunks.faiss"
# META_PATH_FAQ = "faq_chunks_meta.pkl"

# model = SentenceTransformer(MODEL_PATH, trust_remote_code=True)




# def embed_chunks(chunks):
#     """ایجاد embedding برای لیست چانک‌ها و بازگشت numpy array و شناسه‌ها"""
#     texts = [chunk.text for chunk in chunks]
#     embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
#     faiss.normalize_L2(embeddings)
#     ids = [chunk.id for chunk in chunks]
#     return embeddings, ids



# def save_embeddings_to_db(chunks, embeddings):
#     """ذخیره embeddingها در مدل ChunkEmbedding"""
#     for chunk, vector in zip(chunks, embeddings):
#         ChunkEmbedding.objects.update_or_create(
#             chunk=chunk,
#             defaults={"vector": vector.tobytes()}
#         )


# def build_faiss_index(chunks, embeddings):
#     """ساخت ایندکس FAISS و ذخیره در فایل"""
#     dim = embeddings.shape[1]
#     index = faiss.IndexFlatIP(dim)
#     index.add(embeddings)
#     faiss.write_index(index, INDEX_PATH)
#     return index


# def save_metadata(ids):
#     """ذخیره شناسه چانک‌ها"""
#     with open(META_PATH, "wb") as f:
#         pickle.dump(ids, f)


# def rebuild_index():
#     """کل فرایند: گرفتن چانک‌ها، ساخت embedding، ذخیره در DB و ساخت FAISS"""
#     chunks = Chunk.objects.all()
#     embeddings, ids = embed_chunks(chunks)
#     save_embeddings_to_db(chunks, embeddings)
#     build_faiss_index(chunks, embeddings)
#     save_metadata(ids)
#     print("✅ ایندکس بازسازی شد و ذخیره شد.")


# def rebuild_index_if_needed():
#     """
#     اگر فایل FAISS یا metadata وجود نداشت یا تعداد چانک‌ها تغییر کرده بود، بازسازی کن.
#     """
#     chunks = Chunk.objects.all()
#     if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
#         rebuild_index()
#         return

#     # بررسی تغییر تعداد چانک‌ها
#     with open(META_PATH, "rb") as f:
#         old_ids = pickle.load(f)
#     new_ids = [chunk.id for chunk in chunks]
#     if old_ids != new_ids:
#         rebuild_index()



# # --- تست مستقیم ---
# if __name__ == "__main__":
#     rebuild_index()


