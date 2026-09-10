from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid

class MessagePayload(BaseModel):
    role: str
    content: str
    images: Optional[List[str]] = None

class InferenceRequest(BaseModel):
    messages: List[MessagePayload]
    required_capabilities: List[str] = []
    required_modalities: List[str] = []
    preferred_model: Optional[str] = None
    min_context_length: Optional[int] = None
    parameters: Dict[str, Any] = {}

class InferenceResponse(BaseModel):
    output: str
    model: str
    worker_id: uuid.UUID
    metadata: Dict[str, Any] = {}
    latency_ms: int
