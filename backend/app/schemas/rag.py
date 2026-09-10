import uuid
from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional, Any
from datetime import datetime

class KnowledgeBaseCreate(BaseModel):
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: Optional[str] = None
    embedding_model_id: Optional[uuid.UUID] = None

class KnowledgeBaseResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    id: uuid.UUID
    knowledge_base_id: uuid.UUID
    filename: str
    file_type: str
    processing_status: str
    chunks: int = 0
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @field_validator("chunks", mode="before")
    @classmethod
    def count_chunks(cls, v: Any) -> int:
        if isinstance(v, (list, tuple, set)):
            return len(v)
        return int(v) if v is not None else 0

class SearchResult(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    content: str
    page_number: Optional[int]
    score: float
    filename: str

class SearchRequest(BaseModel):
    knowledge_base_id: uuid.UUID
    query: str
    top_k: int = 5
