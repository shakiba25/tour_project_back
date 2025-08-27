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
from tours.utils.index_manager import load_faiss_index
from tours.models import Chunk

model = SentenceTransformer(MODEL_PATH, trust_remote_code=True)

def search_tour_chunks(query, top_k=5):

    index, chunk_ids = load_faiss_index()

    query_vec = model.encode([query], convert_to_numpy=True)
    query_vec = query_vec / np.linalg.norm(query_vec, axis=1, keepdims=True)

    D, I = index.search(query_vec, top_k)  # D: similarity, I: index

    results = []
    for score, idx in zip(D[0], I[0]):
        chunk_id = chunk_ids[idx]
        chunk = Chunk.objects.get(id=chunk_id)
        results.append({
            "chunk": chunk,
            "similarity": float(score)
        })

    return results

if __name__ == "__main__":
    query = "تور ژاپن و معابد"
    results = search_tour_chunks(query)
    for r in results:
        print(f"{r['chunk'].text} (score: {r['similarity']:.4f})")
