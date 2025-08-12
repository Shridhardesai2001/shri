from typing import Tuple, List
from .ollama_chain import run_ollama
import re

# Strict, concise prompt — used only for summary now
SUMMARY_PROMPT = """
Summarize the document below into 6–10 concise bullet points. Each bullet should be short (one line) and focused.
Document:
{context}
"""

MAX_SUMMARY_CHARS = 30000  # safety limit for LLM input


def produce_summary(full_text: str) -> str:
    try:
        context = full_text if len(full_text) <= MAX_SUMMARY_CHARS else full_text[:MAX_SUMMARY_CHARS]
        prompt = SUMMARY_PROMPT.format(context=context)
        out = run_ollama(prompt)

        # Ensure bullet points
        if not out.strip().startswith("-"):
            lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
            if len(lines) > 1:
                out = "\n".join(f"- {ln}" for ln in lines)
            else:
                sents = re.split(r'(?<=[.!?]) +', out.strip())
                out = "\n".join(f"- {s}" for s in sents if s)
        return out
    except Exception as e:
        return f"Error generating summary: {str(e)}"


STOPWORDS = {
    "the","is","are","a","an","and","or","to","of","for","in","on","with","at","by","from","about",
    "what","which","who","whom","when","where","why","how","please","tell","give","me","define","provide",
}


def _extract_relevant_lines(question: str, texts: List[str], max_lines: int = 3) -> List[str]:
    # tokenize question
    tokens = [t for t in re.split(r"[^a-z0-9]+", question.lower()) if t and t not in STOPWORDS]
    token_set = set(tokens)
    if not token_set:
        return []

    candidate_lines: List[tuple[int, str]] = []  # (score, line)
    for chunk in texts:
        for raw_line in chunk.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            lt = [t for t in re.split(r"[^a-z0-9]+", line.lower()) if t]
            if not lt:
                continue
            overlap = len(token_set.intersection(lt))
            if overlap > 0:
                candidate_lines.append((overlap, line))

    if not candidate_lines:
        return []

    # sort by score desc, then length asc
    candidate_lines.sort(key=lambda x: (-x[0], len(x[1])))
    selected = []
    seen = set()
    for _score, line in candidate_lines:
        if line in seen:
            continue
        seen.add(line)
        selected.append(line)
        if len(selected) >= max_lines:
            break
    return selected


def answer_question(question: str, vectorstore) -> Tuple[str, List[str]]:
    try:
        top_k = 6
        hits = vectorstore.search(question, top_k=top_k)
        if not hits:
            return "I could not find the answer in the document.", []

        # Use only the matched chunks of the current vectorstore
        selected_texts: List[str] = []
        for idx, _src, _score in hits:
            if 0 <= idx < len(vectorstore.texts):
                selected_texts.append(vectorstore.texts[idx])

        # Extractive answer from lines
        lines = _extract_relevant_lines(question, selected_texts, max_lines=2)
        if lines:
            # Return a concise single line or two, joined with '; '
            answer = "; ".join(lines)
            # keep it short
            return answer[:500], []

        # If nothing matched, avoid hallucinations and say we could not find it
        return "I could not find the answer in the document.", []
    except Exception as e:
        return f"Error generating answer: {str(e)}", []