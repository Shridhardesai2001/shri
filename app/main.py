from __future__ import annotations
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Tuple
import uuid
import numpy as np
import faiss

from app.models import UploadResponse, AskRequest, AskResponse, Source
from app.chunking import extract_text_by_page, chunk_pages
from app.embedding import embed_texts, embed_query
from app.store import save_doc, load_index_and_chunks, load_summary, ensure_doc_dir
from app.ollama_client import generate_with_ollama


app = FastAPI(title="Talk with PDF - TinyLlama (Ollama)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index


def _summarization_prompt(document_text: str) -> str:
    return (
        "You are a precise summarization assistant. Read the document content below and produce a concise, self-contained summary as bullet points.\n"
        "- Focus on the most important ideas, facts, and conclusions.\n"
        "- Avoid redundancy.\n"
        "- Keep bullets short and clear.\n"
        "Return only bullet points, each starting with '- '.\n\n"
        "Document:\n" + document_text
    )


def _qa_prompt(question: str, context_blocks: List[Dict]) -> str:
    context_text = []
    for i, blk in enumerate(context_blocks, start=1):
        page = blk.get("page", "?")
        content = blk.get("content", "").strip()
        context_text.append(f"[Source {i} | p{page}]\n{content}")
    joined_context = "\n\n".join(context_text)
    return (
        "You are a grounded question-answering assistant. Answer the user's question using ONLY the information provided in the sources below.\n"
        "- If the answer is not contained in the sources, reply exactly: 'I cannot find that in the document.'\n"
        "- Be concise and accurate.\n"
        "- If relevant, cite source numbers like [1], [2].\n\n"
        f"Question: {question}\n\n"
        f"Sources:\n{joined_context}\n\n"
        "Answer:"
    )


@app.post("/upload_pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    pdf_bytes = await file.read()
    pages = extract_text_by_page(pdf_bytes)
    chunks = chunk_pages(pages, chunk_chars=1000, overlap_chars=200)
    if not chunks:
        raise HTTPException(status_code=400, detail="No extractable text found in PDF")

    texts = [c["content"] for c in chunks]
    embeddings = embed_texts(texts)

    index = _build_faiss_index(embeddings)

    # Build summarization input (trim to keep prompt reasonable)
    document_text = "\n\n".join(texts)
    if len(document_text) > 12000:
        document_text = document_text[:12000]
    summary_out = generate_with_ollama(
        _summarization_prompt(document_text),
        model="tinyllama",
        options={"temperature": 0.2, "num_predict": 600},
    )
    # Parse bullets
    bullets = []
    for line in summary_out.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped)
        elif stripped.startswith("*"):
            bullets.append("- " + stripped.lstrip("* "))
    if not bullets and summary_out.strip():
        bullets = ["- " + summary_out.strip()]

    doc_id = str(uuid.uuid4())
    ensure_doc_dir(doc_id)
    save_doc(doc_id, index, chunks, bullets)

    return UploadResponse(doc_id=doc_id, summary_bullets=bullets, num_chunks=len(chunks))


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    try:
        index, chunks = load_index_and_chunks(req.doc_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Unknown doc_id")

    query_vec = embed_query(req.question).astype(np.float32)
    query_vec = np.expand_dims(query_vec, axis=0)

    k = max(1, min(req.top_k, 10))
    sims, idxs = index.search(query_vec, k)
    sims = sims[0]
    idxs = idxs[0]

    retrieved: List[Dict] = []
    for rank, (i, s) in enumerate(zip(idxs, sims)):
        if i < 0 or i >= len(chunks):
            continue
        item = chunks[i]
        retrieved.append({"page": item.get("page", 0), "content": item.get("content", ""), "score": float(s)})

    # Confidence threshold: if top similarity too low, abstain
    if not retrieved or (retrieved and retrieved[0]["score"] < 0.2):
        return AskResponse(
            answer="I cannot find that in the document.",
            sources=[],
        )

    prompt = _qa_prompt(req.question, retrieved)
    answer = generate_with_ollama(
        prompt,
        model="tinyllama",
        options={"temperature": 0.2, "num_predict": 400},
    )

    sources = [Source(page=r["page"], score=r["score"], content=r["content"]) for r in retrieved]
    return AskResponse(answer=answer.strip(), sources=sources)


@app.get("/summary/{doc_id}", response_model=List[str])
async def get_summary(doc_id: str) -> List[str]:
    try:
        bullets = load_summary(doc_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Unknown doc_id")
    if not bullets:
        raise HTTPException(status_code=404, detail="Summary not found")
    return bullets