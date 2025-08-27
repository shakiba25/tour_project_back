import faiss
import pickle
from .embedder import rebuild_faiss_index, INDEX_PATH, META_PATH


def load_faiss_index():
    """لود ایندکس موجود، اگر نبود دوباره ساخته میشه."""
    try:
        index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "rb") as f:
            ids = pickle.load(f)
        print("✅ ایندکس از فایل لود شد.")
        return index, ids
    except Exception:
        print("⚠️ ایندکس موجود نیست. در حال بازسازی...")
        rebuild_faiss_index()
        return load_faiss_index()