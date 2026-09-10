from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import httpx

app = FastAPI(title="Local Ollama Worker API")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
WORKER_NAME = os.getenv("WORKER_NAME", "ollama-local-worker")
WORKER_MODELS = os.getenv("WORKER_MODELS", "llama3")

class GenerateRequest(BaseModel):
    model: str
    messages: List[Dict[str, Any]]
    parameters: Dict[str, Any] = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metadata")
def metadata():
    models = []
    for m in WORKER_MODELS.split(","):
        models.append({
            "model_identifier": m.strip(),
            "name": m.strip(),
            "model_type": "llm",
            "modalities": ["text"],
            "capabilities": ["chat", "general"]
        })
    return {
        "name": WORKER_NAME,
        "hardware_info": {"engine": "ollama"},
        "models": models
    }

@app.post("/generate")
def generate(req: GenerateRequest):
    ollama_url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": req.model,
        "messages": req.messages,
        "stream": False
    }
    
    if req.parameters:
        payload["options"] = req.parameters
        
    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(ollama_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            return {
                "output": data.get("message", {}).get("content", ""),
                "model": data.get("model", req.model),
                "metadata": {
                    "total_duration": data.get("total_duration"),
                    "eval_count": data.get("eval_count")
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama request failed: {e}")
