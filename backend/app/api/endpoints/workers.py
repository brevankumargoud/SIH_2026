import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.worker import WorkerRegistrationRequest, WorkerResponse, WorkerWithModelsResponse
from app.services.worker_service import WorkerService
from app.api.deps import require_admin
from app.models.user import User

router = APIRouter(prefix="/workers", tags=["workers"])

@router.post("/register", response_model=WorkerWithModelsResponse)
def register_worker(request: WorkerRegistrationRequest, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Internal infrastructure endpoint to register a model worker."""
    service = WorkerService(db)
    return service.register_worker(request)

@router.get("", response_model=List[WorkerWithModelsResponse])
def list_workers(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """List all registered model workers."""
    service = WorkerService(db)
    return service.get_workers()

@router.get("/{worker_id}", response_model=WorkerWithModelsResponse)
def get_worker(worker_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Get a specific model worker by ID."""
    service = WorkerService(db)
    worker = service.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker

@router.post("/{worker_id}/heartbeat", response_model=WorkerResponse)
def worker_heartbeat(worker_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Record a heartbeat from a worker."""
    service = WorkerService(db)
    return service.heartbeat(worker_id)

@router.post("/{worker_id}/deactivate", response_model=WorkerResponse)
def deactivate_worker(worker_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Deactivate a model worker."""
    service = WorkerService(db)
    return service.deactivate(worker_id)
