from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


_embedding_model: SentenceTransformer | None = None


def get_embedding_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(model_name)
    return _embedding_model


def normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return embeddings / norms


def embed_texts(texts: List[str]) -> np.ndarray:
    model = get_embedding_model()
    embeddings = model.encode(texts, batch_size=64, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=False)
    embeddings = embeddings.astype(np.float32)
    return normalize_embeddings(embeddings)


def embed_query(text: str) -> np.ndarray:
    return embed_texts([text])[0]