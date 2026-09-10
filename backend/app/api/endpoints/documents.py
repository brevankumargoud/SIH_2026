import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.db.database import get_db
from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.schemas.rag import DocumentResponse, SearchRequest, SearchResult
from app.services.document_service import DocumentService
from app.services.retrieval_service import RetrievalService
from app.api.deps import get_current_user, require_workspace_access
from app.models.user import User

router = APIRouter(prefix="", tags=["documents"])

def check_kb_access(kb_id: uuid.UUID, db: Session, current_user: User):
    kb = db.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    require_workspace_access(kb.workspace_id, db, current_user)
    return kb

@router.post("/knowledge-bases/{kb_id}/documents", response_model=DocumentResponse)
def upload_document(
    kb_id: uuid.UUID,
    file: UploadFile = File(...),
    user_id: uuid.UUID = Form(None), # Deprecated explicit user_id form passing
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_kb_access(kb_id, db, current_user)
    svc = DocumentService(db)
    # Use authenticated user rather than form payload
    return svc.process_file(kb_id, current_user.id, file.filename, file.file)

@router.get("/knowledge-bases/{kb_id}/documents", response_model=List[DocumentResponse])
def list_documents(kb_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_kb_access(kb_id, db, current_user)
    stmt = select(Document).options(selectinload(Document.chunks)).where(Document.knowledge_base_id == kb_id)
    return list(db.execute(stmt).scalars().all())

@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Document).options(selectinload(Document.chunks)).where(Document.id == document_id)
    doc = db.execute(stmt).scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    check_kb_access(doc.knowledge_base_id, db, current_user)
    return doc

@router.delete("/documents/{document_id}")
def delete_document(document_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    check_kb_access(doc.knowledge_base_id, db, current_user)
    svc = DocumentService(db)
    svc.delete_document(document_id)
    return {"status": "ok"}

@router.post("/knowledge-bases/{kb_id}/search", response_model=List[SearchResult])
def search_knowledge_base(kb_id: uuid.UUID, request: SearchRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_kb_access(kb_id, db, current_user)
    svc = RetrievalService(db)
    return svc.search(
        knowledge_base_id=kb_id,
        query=request.query,
        top_k=request.top_k
    )
