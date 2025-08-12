from __future__ import annotations
import os
import json
from typing import List, Dict, Tuple
import numpy as np
import faiss

DOC_ROOT = "/workspace/data"


def _doc_dir(doc_id: str) -> str:
    return os.path.join(DOC_ROOT, doc_id)


def ensure_doc_dir(doc_id: str) -> str:
    path = _doc_dir(doc_id)
    os.makedirs(path, exist_ok=True)
    return path


def save_doc(
    doc_id: str,
    index: faiss.Index,
    chunks: List[Dict],
    summary_bullets: List[str],
) -> None:
    ensure_doc_dir(doc_id)
    index_path = os.path.join(_doc_dir(doc_id), "index.faiss")
    meta_path = os.path.join(_doc_dir(doc_id), "meta.json")
    summary_path = os.path.join(_doc_dir(doc_id), "summary.json")

    faiss.write_index(index, index_path)

    meta = {
        "num_chunks": len(chunks),
        "chunks": chunks,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({"summary_bullets": summary_bullets}, f)


def load_index_and_chunks(doc_id: str) -> Tuple[faiss.Index, List[Dict]]:
    index_path = os.path.join(_doc_dir(doc_id), "index.faiss")
    meta_path = os.path.join(_doc_dir(doc_id), "meta.json")

    if not (os.path.exists(index_path) and os.path.exists(meta_path)):
        raise FileNotFoundError(f"Index or metadata not found for doc_id={doc_id}")

    index = faiss.read_index(index_path)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    chunks: List[Dict] = meta.get("chunks", [])

    return index, chunks


def load_summary(doc_id: str) -> List[str]:
    summary_path = os.path.join(_doc_dir(doc_id), "summary.json")
    if not os.path.exists(summary_path):
        return []
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("summary_bullets", [])