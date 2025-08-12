import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Talk with PDF - TinyLlama", page_icon="📄", layout="wide")

st.title("📄 Talk with PDF — TinyLlama (Ollama)")

with st.sidebar:
    st.markdown("**Backend API**")
    api_url = st.text_input("API URL", value=API_URL)

# Session state
if "doc_id" not in st.session_state:
    st.session_state.doc_id = None
if "summary" not in st.session_state:
    st.session_state.summary = []

st.header("1) Upload PDF and Generate Summary")
file = st.file_uploader("Upload a PDF", type=["pdf"], accept_multiple_files=False)
if file is not None and st.button("Process PDF"):
    with st.spinner("Processing PDF (extracting text, building index, summarizing)..."):
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        try:
            resp = requests.post(f"{api_url}/upload_pdf", files=files, timeout=600)
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.doc_id = data["doc_id"]
                st.session_state.summary = data.get("summary_bullets", [])
                st.success("PDF processed successfully!")
            else:
                st.error(f"Error: {resp.status_code} — {resp.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

if st.session_state.doc_id:
    st.subheader("Document Summary (static)")
    if st.session_state.summary:
        for b in st.session_state.summary:
            st.markdown(b)
    else:
        st.info("No summary available.")

st.header("2) Ask Questions About the PDF")
if not st.session_state.doc_id:
    st.info("Please upload and process a PDF first.")
else:
    question = st.text_input("Your question")
    top_k = st.slider("Top-K context chunks", min_value=3, max_value=10, value=5)
    if st.button("Ask") and question.strip():
        with st.spinner("Retrieving and answering..."):
            try:
                payload = {"doc_id": st.session_state.doc_id, "question": question, "top_k": top_k}
                resp = requests.post(f"{api_url}/ask", json=payload, timeout=300)
                if resp.status_code == 200:
                    data = resp.json()
                    st.markdown("**Answer**")
                    st.write(data.get("answer", ""))
                    sources = data.get("sources", [])
                    if sources:
                        st.markdown("**Sources**")
                        for i, s in enumerate(sources, start=1):
                            with st.expander(f"Source {i} (p{s.get('page')}) — score={s.get('score'):.3f}"):
                                st.write(s.get("content", ""))
                else:
                    st.error(f"Error: {resp.status_code} — {resp.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")