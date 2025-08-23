#!/usr/bin/env bash
set -euo pipefail

# Start Ollama
if ! pgrep -x "ollama" >/dev/null 2>&1; then
	(ollama serve >/tmp/ollama.log 2>&1 &) 
fi

# Ensure model is present
ollama pull tinyllama | cat || true

# Activate venv if exists
if [ -d "/workspace/venv" ]; then
	source /workspace/venv/bin/activate
fi

exec streamlit run /workspace/app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
