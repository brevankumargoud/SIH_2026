from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class MessageCreate(BaseModel):
    role: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_")

class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    model_id: Optional[uuid.UUID]
    metadata: Dict[str, Any] = Field(validation_alias="metadata_")
    created_at: datetime
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ConversationCreate(BaseModel):
    workspace_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: Optional[uuid.UUID]
    agent_id: Optional[uuid.UUID]
    title: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    content: str
    required_capabilities: List[str] = []
    required_modalities: List[str] = []
    preferred_model: Optional[str] = None
    min_context_length: Optional[int] = None
    parameters: Dict[str, Any] = {}
    knowledge_base_ids: List[uuid.UUID] = []
    use_knowledge: bool = False

class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    user_message: MessageResponse
    assistant_message: MessageResponse
    model: Dict[str, Any]
    metadata: Dict[str, Any]
    sources: List[Dict[str, Any]] = []
