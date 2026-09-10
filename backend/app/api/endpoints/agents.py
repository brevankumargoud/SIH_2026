import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.agent import AgentRunCreate, AgentRunResponse
from app.services.agent_service import AgentService
from app.api.deps import get_current_user, require_agent_access
from app.models.user import User

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/{agent_id}/runs", response_model=AgentRunResponse)
def execute_agent_run(
    agent_id: uuid.UUID, 
    request: AgentRunCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    require_agent_access(agent_id, db, current_user)
    svc = AgentService(db)
    
    # Overwrite user_id payload structurally to prevent spoofing
    request.user_id = current_user.id
    
    return svc.execute_agent(agent_id, request)
