# tours/utils/index_manager.py

import faiss
import pickle
import os
from tours.utils.embedder import (
    rebuild_tour_index, rebuild_faq_index,
    INDEX_PATH_TOUR, META_PATH_TOUR,
    INDEX_PATH_FAQ, META_PATH_FAQ
)


# تور
# -------------------------------
def load_tour_index():
    """لود ایندکس تور و شناسه‌ها، یا بازسازی در صورت نبودن فایل"""
    
    try:
        index = faiss.read_index(INDEX_PATH_TOUR)
        with open(META_PATH_TOUR, "rb") as f:
            ids = pickle.load(f)
        print("✅ ایندکس تور از فایل لود شد.")
        return index, ids
    except Exception:
        print("⚠️ ایندکس تور موجود نیست یا خطا در لود. در حال بازسازی...")
        rebuild_tour_index()
        return load_tour_index()


# FAQ
# -------------------------------
def load_faq_index():
    """لود ایندکس FAQ و شناسه‌ها، یا بازسازی در صورت نبودن فایل"""
    
    try:
        index = faiss.read_index(INDEX_PATH_FAQ)
        with open(META_PATH_FAQ, "rb") as f:
            ids = pickle.load(f)
        print("✅ ایندکس FAQ از فایل لود شد.")
        return index, ids
    except Exception:
        print("⚠️ ایندکس FAQ موجود نیست یا خطا در لود. در حال بازسازی...")
        rebuild_faq_index()
        return load_faq_index()
