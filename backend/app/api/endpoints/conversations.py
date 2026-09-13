import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.chat import ConversationCreate, ConversationResponse, ChatRequest, ChatResponse, MessageResponse
from app.services.chat_service import ChatService
from app.api.deps import get_current_user, require_workspace_access
from app.models.user import User
from fastapi import HTTPException

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("", response_model=ConversationResponse)
def create_conversation(request: ConversationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_workspace_access(request.workspace_id, db, current_user)
    svc = ChatService(db)
    return svc.create_conversation(request)

@router.get("", response_model=List[ConversationResponse])
def list_conversations(workspace_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_workspace_access(workspace_id, db, current_user)
    from sqlalchemy import select
    from app.models.conversation import Conversation
    stmt = select(Conversation).where(Conversation.workspace_id == workspace_id)
    return list(db.execute(stmt).scalars().all())

@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ChatService(db)
    conv = svc.get_conversation(conversation_id)
    if not conv: raise HTTPException(status_code=404, detail="Not found")
    require_workspace_access(conv.workspace_id, db, current_user)
    return conv

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
def get_messages(conversation_id: uuid.UUID, limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ChatService(db)
    conv = svc.get_conversation(conversation_id)
    if not conv: raise HTTPException(status_code=404, detail="Not found")
    require_workspace_access(conv.workspace_id, db, current_user)
    svc = ChatService(db)
    return svc.get_conversation_messages(conversation_id, limit)

@router.post("/{conversation_id}/messages", response_model=ChatResponse)
def send_message(conversation_id: uuid.UUID, request: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ChatService(db)
    conv = svc.get_conversation(conversation_id)
    if not conv: raise HTTPException(status_code=404, detail="Not found")
    require_workspace_access(conv.workspace_id, db, current_user)
    svc = ChatService(db)
    return svc.send_message(conversation_id, request)
