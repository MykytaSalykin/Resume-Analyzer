from sentence_transformers import SentenceTransformer
from functools import lru_cache
import os


@lru_cache(maxsize=1)
def get_embedder():
    model_name = os.getenv("EMBED_MODEL", "multi-qa-mpnet-base-dot-v1")
    return SentenceTransformer(model_name)


def embed_texts(texts: list[str]):
    model = get_embedder()
    return model.encode(texts, normalize_embeddings=True)
