import os
import streamlit as st

from utils.pdf_loader import extract_text_from_pdf
from utils.text_preprocess import chunk_text_with_sources
from utils.vector_store import build_vectorstore, load_vectorstore, index_exists
from utils.chat_engine import produce_summary, answer_question

st.set_page_config(page_title="Talk with PDF", layout="wide")
st.title("📄 Talk with PDF — TinyLlama (local)")

# initialize session state
for key in ("vectordb", "summary", "chunks", "pdf_name"):
    if key not in st.session_state:
        st.session_state[key] = None

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"]) 

if uploaded_file:
    # Save the uploaded file
    os.makedirs("data", exist_ok=True)
    pdf_path = os.path.join("data", uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state.pdf_name = uploaded_file.name

    # Extract text
    with st.spinner("Extracting text..."):
        full_text, pages = extract_text_from_pdf(pdf_path)
    if not full_text.strip():
        st.error("No textual content extracted from PDF (maybe scanned images).")
        st.stop()

    # Chunk the text
    with st.spinner("Chunking document..."):
        chunks_with_sources = chunk_text_with_sources(pages, chunk_size=800, chunk_overlap=150)
        st.session_state.chunks = chunks_with_sources

    # Build or load vectorstore (persist per-pdf)
    index_dir = os.path.join("faiss_index", st.session_state.pdf_name.replace(" ", "_"))
    if index_exists(index_dir):
        with st.spinner("Loading vector store..."):
            vectordb = load_vectorstore(index_dir)
    else:
        with st.spinner("Building vector store (this may take a minute)..."):
            vectordb = build_vectorstore(chunks_with_sources, persist_path=index_dir)
    st.session_state.vectordb = vectordb

    # Generate summary once and cache in session state
    if st.session_state.summary is None:
        with st.spinner("Generating summary..."):
            st.session_state.summary = produce_summary(full_text)

    # Display summary
    st.subheader("📝 Document Summary (bullet points)")
    st.markdown(st.session_state.summary)

    # Q&A UI
    st.subheader("❓ Ask a question about the uploaded PDF")
    user_question = st.text_input("Type your question and press Enter")

    if user_question:
        with st.spinner("Searching and generating answer..."):
            answer, _ = answer_question(user_question, st.session_state.vectordb)
        st.markdown("### ✅ Answer")
        st.write(answer)