from typing import Tuple, List
from .ollama_chain import run_ollama


# Prompts
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


MAX_SUMMARY_CHARS = 30000


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
		hits = vectorstore.search(question, top_k=5)
		if not hits:
			return "I could not find the answer in the document.", []

		selected_texts = [t for t, s, sc in hits]
		used_sources = [s for t, s, sc in hits]

		# Deduplicate sources
		seen = set()
		uniq_sources, uniq_texts = [], []
		for text, src in zip(selected_texts, used_sources):
			if src not in seen:
				seen.add(src)
				uniq_sources.append(src)
				uniq_texts.append(text)

		if not uniq_texts:
			return "I could not find the answer in the document.", []

		joined = "\n\n".join(uniq_texts)
		CONTEXT_CHAR_LIMIT = 15000
		context = joined if len(joined) <= CONTEXT_CHAR_LIMIT else joined[:CONTEXT_CHAR_LIMIT]

		prompt = QA_PROMPT.format(context=context, question=question)
		answer = run_ollama(prompt)
		return answer.strip(), uniq_sources
	except Exception as e:
		return f"Error generating answer: {str(e)}", []

