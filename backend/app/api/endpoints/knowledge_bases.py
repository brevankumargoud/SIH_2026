import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import get_db
from app.models.knowledge_base import KnowledgeBase
from app.schemas.rag import KnowledgeBaseCreate, KnowledgeBaseResponse
from app.models.user import User
from app.models.workspace import Workspace
from app.api.deps import get_current_user, require_workspace_access

router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])

@router.get("/default", response_model=KnowledgeBaseResponse)
def get_or_create_default_kb(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Find any KB for the user
    kb = db.execute(select(KnowledgeBase).where(KnowledgeBase.created_by == current_user.id)).scalars().first()
    if kb:
        return kb

    # No KB found, check for any workspace
    ws = db.execute(select(Workspace).where(Workspace.created_by == current_user.id)).scalars().first()
    if not ws:
        ws = Workspace(name="Default Workspace", created_by=current_user.id)
        db.add(ws)
        db.commit()
        db.refresh(ws)

    kb = KnowledgeBase(
        workspace_id=ws.id,
        name="Prototype KB",
        description="Default knowledge base for prototype integration",
        created_by=current_user.id
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb

@router.post("", response_model=KnowledgeBaseResponse)
def create_knowledge_base(request: KnowledgeBaseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_workspace_access(request.workspace_id, db, current_user)
    kb = KnowledgeBase(
        workspace_id=request.workspace_id,
        name=request.name,
        description=request.description,
        embedding_model_id=request.embedding_model_id,
        created_by=request.user_id
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb

@router.get("", response_model=List[KnowledgeBaseResponse])
def list_knowledge_bases(workspace_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_workspace_access(workspace_id, db, current_user)
    stmt = select(KnowledgeBase).where(KnowledgeBase.workspace_id == workspace_id)
    return list(db.execute(stmt).scalars().all())

@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
def get_knowledge_base(kb_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    kb = db.get(KnowledgeBase, kb_id)
    if not kb: raise HTTPException(status_code=404, detail="Not found")
    require_workspace_access(kb.workspace_id, db, current_user)
    return kb

@router.delete("/{kb_id}")
def delete_knowledge_base(kb_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    kb = db.get(KnowledgeBase, kb_id)
    if not kb: raise HTTPException(status_code=404, detail="Not found")
    require_workspace_access(kb.workspace_id, db, current_user)
    kb = db.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(kb)
    db.commit()
    return {"status": "ok"}
