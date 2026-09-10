import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ToolParameterSchema(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True

class ToolSchema(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameterSchema] = []

class AgentRunCreate(BaseModel):
    input_data: Dict[str, Any]
    user_id: Optional[uuid.UUID] = None
    conversation_id: Optional[uuid.UUID] = None
    max_iterations: int = 10
    preferred_model: Optional[str] = None

class AgentRunResponse(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    status: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class AgentPlanStep(BaseModel):
    step_number: int
    description: str
    status: str = "pending"

class ToolResult(BaseModel):
    success: bool
    output: Any
    metadata: Dict[str, Any] = {}
    error: Optional[str] = None
