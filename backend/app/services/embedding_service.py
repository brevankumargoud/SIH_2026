import os
import logging
import httpx
from typing import List

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.provider = os.getenv("EMBEDDING_PROVIDER", "mock")
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    def generate_embedding(self, text: str) -> List[float]:
        if self.provider == "ollama":
            logger.info(f"Generating embedding with provider={self.provider} model={self.model} target={self.ollama_url}")
            response = httpx.post(f"{self.ollama_url}/api/embeddings", json={
                "model": self.model,
                "prompt": text
            }, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data["embedding"]
        else:
            logger.info(f"Generating embedding with provider={self.provider} model={self.model}")
            # Deterministic mock vector of 768 elements
            val = float(len(text) % 100) / 100.0
            return [val] * 768
