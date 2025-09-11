# tours/utils/embedder.py

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")

import django
django.setup()

import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from tours.models import Chunk, ChunkEmbedding
# from load_model import model

MODEL_PATH = r"C:\Users\Asus\Desktop\test t5\models\xmaniimaux-gte-persian-v3-fp16"
INDEX_PATH = "tour_chunks_xmaniimaux_v3.faiss"
META_PATH = "tour_chunks_metadata.pkl"

model = SentenceTransformer(MODEL_PATH, trust_remote_code=True)


def embed_chunks(chunks):
    """ایجاد embedding برای لیست چانک‌ها و بازگشت numpy array و شناسه‌ها"""
    texts = [chunk.text for chunk in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    faiss.normalize_L2(embeddings)
    ids = [chunk.id for chunk in chunks]
    return embeddings, ids


def save_embeddings_to_db(chunks, embeddings):
    """ذخیره embeddingها در مدل ChunkEmbedding"""
    for chunk, vector in zip(chunks, embeddings):
        ChunkEmbedding.objects.update_or_create(
            chunk=chunk,
            defaults={"vector": vector.tobytes()}
        )


def build_faiss_index(chunks, embeddings):
    """ساخت ایندکس FAISS و ذخیره در فایل"""
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)
    return index


def save_metadata(ids):
    """ذخیره شناسه چانک‌ها"""
    with open(META_PATH, "wb") as f:
        pickle.dump(ids, f)


def rebuild_index():
    """کل فرایند: گرفتن چانک‌ها، ساخت embedding، ذخیره در DB و ساخت FAISS"""
    chunks = Chunk.objects.all()
    embeddings, ids = embed_chunks(chunks)
    save_embeddings_to_db(chunks, embeddings)
    build_faiss_index(chunks, embeddings)
    save_metadata(ids)
    print("✅ ایندکس بازسازی شد و ذخیره شد.")


def rebuild_index_if_needed():
    """
    اگر فایل FAISS یا metadata وجود نداشت یا تعداد چانک‌ها تغییر کرده بود، بازسازی کن.
    """
    chunks = Chunk.objects.all()
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        rebuild_index()
        return

    # بررسی تغییر تعداد چانک‌ها
    with open(META_PATH, "rb") as f:
        old_ids = pickle.load(f)
    new_ids = [chunk.id for chunk in chunks]
    if old_ids != new_ids:
        rebuild_index()


# --- تست مستقیم ---
if __name__ == "__main__":
    rebuild_index()
