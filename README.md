# PDF AI Platform

Run a Streamlit app that can summarize PDFs and do Q&A using a local Ollama model with embeddings + FAISS.

## Quickstart

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Start Ollama and ensure the model is available
```bash
ollama serve | cat
ollama pull tinyllama | cat
```

3. Run the app
```bash
streamlit run app.py
```

Uploads are saved under `data/` and vector indexes under `faiss_index/`.