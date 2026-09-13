import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.agent import AgentRunCreate, AgentRunResponse, AgentResponse
from app.services.agent_service import AgentService
from app.api.deps import get_current_user, require_agent_access, require_workspace_access
from app.models.user import User
from app.models.agent import Agent
from app.models.workspace import Workspace
from sqlalchemy import select

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/default", response_model=AgentResponse)
def get_or_create_default_agent(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Find any agent for the user
    agent = db.execute(select(Agent).where(Agent.created_by == current_user.id)).scalars().first()
    if agent:
        return {"id": agent.id, "name": agent.name, "description": agent.description or "", "status": "active", "model_id": "llama3.2:1b", "allowed_tools": ["knowledge_search"]}

    # Get or create workspace
    ws = db.execute(select(Workspace).where(Workspace.created_by == current_user.id)).scalars().first()
    if not ws:
        ws = Workspace(name="Default Workspace", created_by=current_user.id)
        db.add(ws)
        db.commit()
        db.refresh(ws)

    agent = Agent(
        workspace_id=ws.id,
        name="Prototype Operations Agent",
        description="Default agent for task orchestration and retrieval",
        system_prompt="You are an autonomous AI operations assistant. You can use available tools to answer questions.",
        agent_type="conversational",
        created_by=current_user.id,
        is_active=True
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)

    # Automatically link agent to default KB
    from app.models.knowledge_base import KnowledgeBase
    from app.models.agent_knowledge_base import AgentKnowledgeBase
    kb = db.execute(select(KnowledgeBase).where(KnowledgeBase.created_by == current_user.id)).scalars().first()
    if kb:
        akb = db.execute(select(AgentKnowledgeBase).where(AgentKnowledgeBase.agent_id == agent.id, AgentKnowledgeBase.knowledge_base_id == kb.id)).scalars().first()
        if not akb:
            akb = AgentKnowledgeBase(agent_id=agent.id, knowledge_base_id=kb.id)
            db.add(akb)
            db.commit()

    return {"id": agent.id, "name": agent.name, "description": agent.description or "", "status": "active", "model_id": "llama3.2:1b", "allowed_tools": ["knowledge_search"]}

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
