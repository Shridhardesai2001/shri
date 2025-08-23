from langchain_community.llms import Ollama


# Use tinyllama model installed in Ollama
OLLAMA_MODEL = "tinyllama"
DEFAULT_TEMPERATURE = 0.0


def get_llm():
	return Ollama(model=OLLAMA_MODEL, temperature=DEFAULT_TEMPERATURE)


def run_ollama(prompt_text: str) -> str:
	"""Run Ollama with a simple text prompt and return its output."""
	llm = get_llm()
	try:
		return llm.invoke(prompt_text).strip()
	except Exception as e:
		raise RuntimeError(f"Ollama generation error: {e}")

