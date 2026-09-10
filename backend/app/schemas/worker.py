from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class ModelMetadata(BaseModel):
    model_identifier: str
    name: str
    version: Optional[str] = None
    provider: Optional[str] = None
    model_type: str
    modalities: List[str] = []
    capabilities: List[str] = []
    context_length: Optional[int] = None

class WorkerRegistrationRequest(BaseModel):
    name: str
    hostname: Optional[str] = None
    ip_address: Any
    port: int = Field(gt=0, le=65535)
    protocol: str = "http"
    hardware_info: Dict[str, Any] = {}
    available_vram_mb: Optional[int] = None
    models: List[ModelMetadata] = []

class ModelResponse(BaseModel):
    id: uuid.UUID
    worker_id: uuid.UUID
    name: str
    model_identifier: str
    version: Optional[str]
    provider: Optional[str]
    model_type: str
    modalities: list
    capabilities: list
    context_length: Optional[int]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class WorkerResponse(BaseModel):
    id: uuid.UUID
    name: str
    hostname: Optional[str]
    ip_address: Any
    port: int
    protocol: str
    status: str
    hardware_info: Dict[str, Any]
    available_vram_mb: Optional[int]
    last_heartbeat: Optional[datetime]
    is_active: bool
    registered_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkerWithModelsResponse(WorkerResponse):
    models: List[ModelResponse] = []
