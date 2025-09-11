import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelproj.settings")

import django
django.setup()


from sentence_transformers import SentenceTransformer

MODEL_PATH = r"C:\Users\Asus\Desktop\test t5\models\xmaniimaux-gte-persian-v3-fp16"

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_PATH, trust_remote_code=True)
    return _model