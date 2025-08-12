from typing import List, Dict
import fitz  # PyMuPDF


def extract_text_by_page(pdf_bytes: bytes) -> List[Dict]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages: List[Dict] = []
    try:
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            text = page.get_text("text")
            pages.append({"page": page_index + 1, "text": text})
    finally:
        doc.close()
    return pages


def _split_into_paragraphs(text: str) -> List[str]:
    blocks = [b.strip() for b in text.split("\n\n")]
    return [b for b in blocks if b]


def chunk_pages(
    pages: List[Dict],
    chunk_chars: int = 1000,
    overlap_chars: int = 200,
) -> List[Dict]:
    chunks: List[Dict] = []
    for page_item in pages:
        page_num = page_item["page"]
        text = page_item["text"] or ""
        paragraphs = _split_into_paragraphs(text) if text else []
        if not paragraphs:
            continue
        buffer: List[str] = []
        current_len = 0
        for para in paragraphs:
            if current_len + len(para) + 1 <= chunk_chars:
                buffer.append(para)
                current_len += len(para) + 1
            else:
                if buffer:
                    chunk_text = "\n".join(buffer).strip()
                    if chunk_text:
                        chunks.append({"page": page_num, "content": chunk_text})
                # start new buffer with overlap from previous buffer
                if overlap_chars > 0 and buffer:
                    joined = "\n".join(buffer)
                    overlap = joined[-overlap_chars:]
                    buffer = [overlap, para]
                    current_len = len(overlap) + len(para) + 1
                else:
                    buffer = [para]
                    current_len = len(para) + 1
        if buffer:
            chunk_text = "\n".join(buffer).strip()
            if chunk_text:
                chunks.append({"page": page_num, "content": chunk_text})
    return chunks