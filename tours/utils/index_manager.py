# tours/utils/index_manager.py
import faiss
import pickle
import os
from tours.utils.embedder import rebuild_index, INDEX_PATH, META_PATH

def load_faiss_index():
    """
    لود ایندکس FAISS و شناسه‌های چانک‌ها از فایل.
    اگر فایل‌ها موجود نبود یا نیاز به بازسازی بود، ایندکس بازسازی می‌شود.
    """
    try:
        index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "rb") as f:
            ids = pickle.load(f)
        print("✅ ایندکس از فایل لود شد.")
        return index, ids
    except Exception:
        print("⚠️ ایندکس موجود نیست یا خطا در لود. در حال بازسازی...")
        rebuild_index()
        return load_faiss_index()
