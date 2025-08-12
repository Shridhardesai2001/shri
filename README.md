## Talk with PDF — TinyLlama (Ollama)

- **Model**: TinyLlama via Ollama (`ollama run tinyllama`)
- **PDF Parsing**: PyMuPDF
- **Embeddings**: Sentence-BERT (`sentence-transformers/all-MiniLM-L6-v2`)
- **Vector Store**: FAISS (cosine similarity via inner product on normalized vectors)
- **Backend**: FastAPI
- **Frontend**: Streamlit

### Features
- Static bullet-point summarization of the uploaded PDF
- Grounded Q&A using semantic search over FAISS index
- Strict non-hallucination policy: answers must come from retrieved context

### Prerequisites
- Python 3.10+
- Ollama installed and running locally (`http://localhost:11434`)
- Pull TinyLlama model: `ollama pull tinyllama`

### Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run backend (FastAPI)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Run frontend (Streamlit)
```bash
export API_URL=http://localhost:8000
streamlit run streamlit_app.py
```

### API
- `POST /upload_pdf` → multipart `file` (PDF). Returns `{ doc_id, summary_bullets[], num_chunks }`.
- `POST /ask` → JSON `{ doc_id, question, top_k }`. Returns `{ answer, sources[] }`.
- `GET /summary/{doc_id}` → Returns saved bullet summary array.

### Notes
- Summarization may truncate very large documents to keep prompts within reasonable limits. For higher fidelity, implement a map-reduce summarization strategy.
- FAISS index and metadata are stored under `/workspace/data/{doc_id}`.
- To change the embedding model, edit `app/embedding.py` `get_embedding_model()`.