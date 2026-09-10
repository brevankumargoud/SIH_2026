import uuid
from pydantic import BaseModel, ConfigDict
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
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

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
