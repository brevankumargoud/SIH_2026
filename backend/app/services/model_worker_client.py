import httpx
from typing import Dict, Any, Optional

class ModelWorkerClient:
    """Client for interacting with local model workers over HTTP."""
    
    def __init__(self, ip_address: str, port: int, protocol: str = "http", timeout: float = 10.0):
        self.base_url = f"{protocol}://{ip_address}:{port}"
        self.timeout = timeout
        
    def _get_client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def check_health(self) -> bool:
        """Call GET /health on the worker."""
        try:
            with self._get_client() as client:
                response = client.get("/health")
                response.raise_for_status()
                data = response.json()
                return data.get("status") == "ok"
        except Exception:
            return False

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Call GET /metadata on the worker."""
        try:
            with self._get_client() as client:
                response = client.get("/metadata")
                response.raise_for_status()
                return response.json()
        except Exception:
            return None
            
    def generate(self, model: str, messages: list, parameters: dict = None) -> Optional[Dict[str, Any]]:
        """Call POST /generate on the worker."""
        payload = {
            "model": model,
            "messages": messages,
            "parameters": parameters or {}
        }
        try:
            with self._get_client() as client:
                response = client.post("/generate", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception:
            return None
