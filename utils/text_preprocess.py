from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Tuple


def chunk_text_with_sources(pages: List[Tuple[str, int]], chunk_size=800, chunk_overlap=150):
    """
    Convert page-level text into overlapping chunks with source ids.
    Returns list of (chunk_text, source_id) tuples.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = []
    for page_text, page_no in pages:
        splits = splitter.split_text(page_text)
        for idx, s in enumerate(splits):
            source = f"Page_{page_no}_Chunk_{idx+1}"
            chunks.append((s, source))
    return chunks