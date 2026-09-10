from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Mock Model Worker")

class GenerateRequest(BaseModel):
    model: str
    messages: list
    parameters: dict = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metadata")
def metadata():
    return {
        "name": "mock-worker-1",
        "hostname": "localhost",
        "version": "1.0.0",
        "models": [
            {
                "model_identifier": "mock-llm-1",
                "name": "Mock LLM",
                "model_type": "text-generation",
                "capabilities": ["chat"]
            }
        ],
        "hardware_info": {"gpu": "mock-gpu"}
    }

@app.post("/generate")
def generate(req: GenerateRequest):
    return {
        "output": f"Mock response from {req.model}",
        "model": req.model,
        "metadata": {"usage": {"total_tokens": 42}}
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
