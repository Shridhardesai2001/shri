import fitz  # PyMuPDF
from typing import List, Tuple


def extract_text_from_pdf(path: str) -> (str, List[Tuple[str, int]]):
    """
    Returns:
      full_text: concatenated text of the PDF
      pages: list of tuples (page_text, page_number)
    """
    doc = fitz.open(path)
    pages = []
    all_text_parts = []
    for i, page in enumerate(doc, start=1):
        try:
            txt = page.get_text("text") or ""
        except Exception:
            txt = ""
        txt = txt.strip()
        if txt:
            pages.append((txt, i))
            all_text_parts.append(txt)
    doc.close()
    full_text = "\n\n".join(all_text_parts)
    return full_text, pages