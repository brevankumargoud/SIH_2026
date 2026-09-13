# Local Ollama Worker

This is an independent Model Worker process for the Sovereign On-Premise Agentic AI Workbench.
It translates the central backend's generic model worker protocol into Ollama API requests.

## Setup

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Start Ollama and pull your desired models:
   ```bash
   ollama serve
   ollama pull llama3
   ```
3. Run the worker:
   ```bash
   WORKER_MODELS="llama3,mistral" WORKER_NAME="my-laptop-gpu" uvicorn app.main:app --host 0.0.0.1 --port 8005
   ```

## Configuration

* `OLLAMA_BASE_URL`: URL to your Ollama runtime (default: `http://127.0.0.1:11434`)
* `WORKER_NAME`: Identity of this worker (default: `ollama-local-worker`)
* `WORKER_MODELS`: Comma-separated list of models this worker hosts (default: `llama3`)
