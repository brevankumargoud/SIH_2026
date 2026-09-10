import httpx
from typing import Dict, Any, Optional

class ModelWorkerClient:
    """Client for interacting with local model workers over HTTP."""
    
    def __init__(self, ip_address: str, port: int, protocol: str = "http", timeout: float = 600.0, is_ollama: bool = False):
        self.base_url = f"{protocol}://{ip_address}:{port}"
        self.timeout = timeout
        self.is_ollama = is_ollama
        
    def _get_client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def check_health(self) -> bool:
        """Call GET /health on the worker, or / for Ollama."""
        try:
            with self._get_client() as client:
                if self.is_ollama:
                    response = client.get("/")
                    response.raise_for_status()
                    return "Ollama is running" in response.text
                else:
                    response = client.get("/health")
                    response.raise_for_status()
                    data = response.json()
                    return data.get("status") == "ok"
        except Exception:
            return False

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Call GET /metadata on the worker, or /api/tags for Ollama."""
        try:
            with self._get_client() as client:
                if self.is_ollama:
                    response = client.get("/api/tags")
                    response.raise_for_status()
                    return response.json()
                else:
                    response = client.get("/metadata")
                    response.raise_for_status()
                    return response.json()
        except Exception:
            return None
            
    def generate(self, model: str, messages: list, parameters: dict = None) -> Optional[Dict[str, Any]]:
        """Call POST /generate on the worker, or /api/chat for Ollama."""
        try:
            with self._get_client() as client:
                if self.is_ollama:
                    payload = {
                        "model": model,
                        "messages": messages,
                        "stream": False,
                        "options": parameters or {}
                    }
                    response = client.post("/api/chat", json=payload)
                    response.raise_for_status()
                    data = response.json()
                    return {
                        "output": data.get("message", {}).get("content", ""),
                        "model": data.get("model", model),
                        "metadata": {
                            "eval_count": data.get("eval_count"),
                            "eval_duration": data.get("eval_duration")
                        }
                    }
                else:
                    payload = {
                        "model": model,
                        "messages": messages,
                        "parameters": parameters or {}
                    }
                    response = client.post("/generate", json=payload)
                    response.raise_for_status()
                    return response.json()
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None
