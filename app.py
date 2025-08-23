import os
import streamlit as st

from utils.pdf_loader import extract_text_from_pdf
from utils.text_preprocess import chunk_text_with_sources
from utils.vector_store import build_vectorstore, load_vectorstore, index_exists
from utils.chat_engine import produce_summary, answer_question
from ui import render_start_page, render_tools_page


st.set_page_config(page_title="PDF AI Platform", layout="wide")


def summarize_page():
	st.header("Smart Summarize")
	st.write("Upload your PDF to get a summary below:")

	uploaded_file = st.file_uploader("Select a PDF for summarization", type=["pdf"], key="summarize_upload")
	if uploaded_file is not None:
		# Optional: Save the uploaded file locally if you need filesystem access
		os.makedirs("/workspace/data", exist_ok=True)
		safe_name = os.path.basename(uploaded_file.name).replace(" ", "_")
		pdf_path = os.path.join("/workspace/data", safe_name)
		with open(pdf_path, "wb") as f:
			f.write(uploaded_file.getbuffer())

		with st.spinner("Extracting text..."):
			full_text, _ = extract_text_from_pdf(pdf_path)

		if not full_text.strip():
			st.error("No textual content extracted from PDF.")
		else:
			with st.spinner("Summarizing document..."):
				summary = produce_summary(full_text)
			st.subheader("📋 Summary")
			st.markdown(summary)

	if st.button("← Back to Tools", key="back_to_tools_summarize"):
		st.session_state.page = "tools"
		st.rerun()


def chat_page():
	st.header("Intelligent Q&A")
	st.write("Upload your PDF to ask questions below:")
	uploaded_file = st.file_uploader("Select a PDF for Q&A", type=["pdf"], key="chat_upload")
	if uploaded_file:
		os.makedirs("/workspace/data", exist_ok=True)
		safe_name = os.path.basename(uploaded_file.name).replace(" ", "_")
		pdf_path = os.path.join("/workspace/data", safe_name)
		with open(pdf_path, "wb") as f:
			f.write(uploaded_file.getbuffer())

		full_text, pages = extract_text_from_pdf(pdf_path)
		if not full_text.strip():
			st.error("No textual content extracted from PDF.")
		else:
			chunks_with_sources = chunk_text_with_sources(pages, chunk_size=800, chunk_overlap=150)
			index_dir = os.path.join("/workspace/faiss_index", safe_name)
			if "chat_vdb" in st.session_state and st.session_state.get("chat_vdb_key") == index_dir:
				vectordb = st.session_state.chat_vdb
			elif index_exists(index_dir):
				vectordb = load_vectorstore(index_dir)
				st.session_state.chat_vdb = vectordb
				st.session_state.chat_vdb_key = index_dir
			else:
				vectordb = build_vectorstore(chunks_with_sources, persist_path=index_dir)
				st.session_state.chat_vdb = vectordb
				st.session_state.chat_vdb_key = index_dir

			question = st.text_input("Type your question about the PDF", key="chat_q_txt")
			if question:
				with st.spinner("Searching and generating answer..."):
					answer, _sources = answer_question(question, vectordb)
				st.subheader("✅ Answer")
				st.write(answer)
	if st.button("← Back to Tools", key="back_to_tools_chat"):
		st.session_state.page = "tools"
		st.rerun()


def edit_page():
	st.header("Smart Editor")
	st.info("Demo: This page would let users edit PDF content with AI in a real implementation.")
	# You can add real PDF editing logic and file download here
	uploaded_file = st.file_uploader("Select a PDF for editing", type=["pdf"], key="edit_upload")
	if uploaded_file:
		st.success("Editing feature coming soon!")
	if st.button("← Back to Tools", key="back_to_tools_edit"):
		st.session_state.page = "tools"
		st.rerun()


def main():
	if "page" not in st.session_state:
		st.session_state.page = "start"
	if st.session_state.page == "start":
		clicked = render_start_page()  # Returns True if button clicked
		if clicked:
			st.session_state.page = "tools"
			st.rerun()  # Refresh instantly to switch page

	elif st.session_state.page == "tools":
		render_tools_page()
	elif st.session_state.page == "summarize":
		summarize_page()
	elif st.session_state.page == "chat":
		chat_page()
	elif st.session_state.page == "edit":
		edit_page()


if __name__ == "__main__":
	main()

