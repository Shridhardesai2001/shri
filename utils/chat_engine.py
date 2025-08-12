from typing import Tuple, List
from .ollama_chain import run_ollama

# Strict, concise prompt — instruct LLM to answer ONLY from context and be short.
QA_PROMPT = """
You are an assistant that MUST answer questions using ONLY the provided context.
Context:
{context}

Question:
{question}

Instructions:
- Answer in one short sentence or a short comma-separated list (no extra biography).
- If the exact answer is not present in the context, reply exactly: "I could not find the answer in the document."
- Do NOT invent facts.
"""

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
                import re
                sents = re.split(r'(?<=[.!?]) +', out.strip())
                out = "\n".join(f"- {s}" for s in sents if s)
        return out
    except Exception as e:
        return f"Error generating summary: {str(e)}"


def answer_question(question: str, vectorstore) -> Tuple[str, List[str]]:
    try:
        top_k = 5
        hits = vectorstore.search(question, top_k=top_k)
        if not hits:
            return "I could not find the answer in the document.", []

        # Build context solely from the matched chunks of the current vectorstore
        selected_texts: List[str] = []
        used_sources: List[str] = []
        for idx, src, _score in hits:
            # guard against bad indices
            if 0 <= idx < len(vectorstore.texts):
                selected_texts.append(vectorstore.texts[idx])
                used_sources.append(src)

        # Deduplicate by source while preserving order
        seen = set()
        uniq_texts: List[str] = []
        for text, src in zip(selected_texts, used_sources):
            if src in seen:
                continue
            seen.add(src)
            uniq_texts.append(text)

        if not uniq_texts:
            return "I could not find the answer in the document.", []

        CONTEXT_CHAR_LIMIT = 15000
        joined = "\n\n".join(uniq_texts)
        context = joined if len(joined) <= CONTEXT_CHAR_LIMIT else joined[:CONTEXT_CHAR_LIMIT]

        prompt = QA_PROMPT.format(context=context, question=question)
        answer = run_ollama(prompt)

        # Post-filter for the strict instruction to avoid biographies.
        answer = answer.strip()
        if not answer:
            return "I could not find the answer in the document.", []
        # Keep the first sentence or first line only to ensure concise output
        if "\n" in answer:
            answer = answer.splitlines()[0].strip()
        if ". " in answer:
            answer = answer.split(". ")[0].strip()
        return answer, []
    except Exception as e:
        return f"Error generating answer: {str(e)}", []