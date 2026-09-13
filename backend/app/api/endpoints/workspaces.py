import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.api.deps import get_current_user
from pydantic import BaseModel, ConfigDict
from datetime import datetime

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    created_by: uuid.UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

@router.get("/default", response_model=WorkspaceResponse)
def get_or_create_default_workspace(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ws = db.execute(select(Workspace).where(Workspace.created_by == current_user.id)).scalars().first()
    if not ws:
        ws = Workspace(name="Default Workspace", created_by=current_user.id)
        db.add(ws)
        db.commit()
        db.refresh(ws)
    return ws
