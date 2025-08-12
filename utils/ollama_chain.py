from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Use tinyllama model installed in Ollama
OLLAMA_MODEL = "tinyllama"
DEFAULT_TEMPERATURE = 0.0


def get_llm():
    return Ollama(model=OLLAMA_MODEL, temperature=DEFAULT_TEMPERATURE)


def run_ollama(prompt_text: str) -> str:
    """
    Run Ollama via a simple LLMChain and return textual output.
    `prompt_text` should contain instruction and any context as needed.
    """
    llm = get_llm()
    # Simple two-field template; we pass instruction in 'instruction' to keep API simple
    template = "{instruction}\n\n{context}"
    prompt = PromptTemplate(input_variables=["instruction", "context"], template=template)
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        out = chain.run({"instruction": prompt_text, "context": ""})
        return out.strip()
    except Exception as e:
        # bubble up a short error string to caller
        raise RuntimeError(f"Ollama generation error: {e}")