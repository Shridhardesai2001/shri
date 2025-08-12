import os
import pickle
from typing import List, Tuple
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Configuration
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"  # SentenceTransformers small model

_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL_NAME)
    return _embedder


class SimpleVectorStore:
    def __init__(self, index: faiss.IndexFlatIP, metadatas: List[str], texts: List[str]):
        self.index = index
        self.metadatas = metadatas
        self.texts = texts

    def search(self, query: str, top_k: int = 5):
        emb = _get_embedder().encode([query], convert_to_numpy=True, show_progress_bar=False)
        faiss.normalize_L2(emb)
        D, I = self.index.search(emb, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1:
                continue
            results.append((idx, self.metadatas[idx], float(score)))
        return results


def index_exists(persist_path: str) -> bool:
    return os.path.isdir(persist_path) and Path(os.path.join(persist_path, "index.faiss")).exists() and Path(os.path.join(persist_path, "meta.pkl")).exists()


def build_vectorstore(chunks_with_sources: List[Tuple[str, str]], persist_path: str = None) -> SimpleVectorStore:
    texts = [c for c, s in chunks_with_sources]
    metadatas = [s for c, s in chunks_with_sources]
    embedder = _get_embedder()
    vectors = embedder.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    faiss.normalize_L2(vectors)
    d = vectors.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(vectors)

    if persist_path:
        os.makedirs(persist_path, exist_ok=True)
        faiss.write_index(index, os.path.join(persist_path, "index.faiss"))
        with open(os.path.join(persist_path, "meta.pkl"), "wb") as f:
            pickle.dump({"metadatas": metadatas, "texts": texts}, f)

    return SimpleVectorStore(index=index, metadatas=metadatas, texts=texts)


def load_vectorstore(persist_path: str) -> SimpleVectorStore:
    if not index_exists(persist_path):
        raise FileNotFoundError("Index not found at: " + persist_path)
    index = faiss.read_index(os.path.join(persist_path, "index.faiss"))
    with open(os.path.join(persist_path, "meta.pkl"), "rb") as f:
        meta = pickle.load(f)
    return SimpleVectorStore(index=index, metadatas=meta["metadatas"], texts=meta["texts"])