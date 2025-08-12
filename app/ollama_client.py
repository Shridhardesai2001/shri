from typing import Optional, Dict, Any
import requests

OLLAMA_BASE_URL = "http://localhost:11434"


def generate_with_ollama(
    prompt: str,
    model: str = "tinyllama",
    options: Optional[Dict[str, Any]] = None,
) -> str:
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    if options:
        payload["options"] = options
    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()
    except Exception as e:
        return f"[Generation error: {e}]"