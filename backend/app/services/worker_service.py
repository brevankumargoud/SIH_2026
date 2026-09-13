import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from app.models.model_worker import ModelWorker
from app.models.model import Model
from app.schemas.worker import WorkerRegistrationRequest

class WorkerService:
    def __init__(self, db: Session):
        self.db = db
        
    def register_worker(self, request: WorkerRegistrationRequest) -> ModelWorker:
        stmt = select(ModelWorker).where(ModelWorker.name == request.name)
        existing_worker = self.db.execute(stmt).scalar_one_or_none()
        
        if existing_worker:
            existing_worker.hostname = request.hostname
            existing_worker.ip_address = request.ip_address
            existing_worker.port = request.port
            existing_worker.protocol = request.protocol
            existing_worker.hardware_info = request.hardware_info
            existing_worker.available_vram_mb = request.available_vram_mb
            existing_worker.status = "available"
            existing_worker.last_heartbeat = datetime.now(timezone.utc)
            existing_worker.is_active = True
            worker = existing_worker
        else:
            worker = ModelWorker(
                name=request.name,
                hostname=request.hostname,
                ip_address=request.ip_address,
                port=request.port,
                protocol=request.protocol,
                status="available",
                hardware_info=request.hardware_info,
                available_vram_mb=request.available_vram_mb,
                last_heartbeat=datetime.now(timezone.utc),
                is_active=True
            )
            self.db.add(worker)
            
        self.db.flush()
        
        provided_model_ids = [m.model_identifier for m in request.models]
        for existing_model in worker.models:
            if existing_model.model_identifier not in provided_model_ids:
                existing_model.is_active = False
        
        existing_models_map = {m.model_identifier: m for m in worker.models}
        for model_data in request.models:
            if model_data.model_identifier in existing_models_map:
                m = existing_models_map[model_data.model_identifier]
                m.name = model_data.name
                m.version = model_data.version
                m.provider = model_data.provider
                m.model_type = model_data.model_type
                m.modalities = model_data.modalities
                m.capabilities = model_data.capabilities
                m.context_length = model_data.context_length
                m.is_active = True
            else:
                new_model = Model(
                    worker_id=worker.id,
                    name=model_data.name,
                    model_identifier=model_data.model_identifier,
                    version=model_data.version,
                    provider=model_data.provider,
                    model_type=model_data.model_type,
                    modalities=model_data.modalities,
                    capabilities=model_data.capabilities,
                    context_length=model_data.context_length,
                    is_active=True
                )
                self.db.add(new_model)
                
        self.db.commit()
        self.db.refresh(worker)
        return worker

    def get_workers(self) -> List[ModelWorker]:
        stmt = select(ModelWorker)
        return list(self.db.execute(stmt).scalars().all())
        
    def get_worker(self, worker_id: uuid.UUID) -> Optional[ModelWorker]:
        return self.db.get(ModelWorker, worker_id)
        
    def heartbeat(self, worker_id: uuid.UUID) -> ModelWorker:
        worker = self.get_worker(worker_id)
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        worker.last_heartbeat = datetime.now(timezone.utc)
        worker.status = "available"
        self.db.commit()
        self.db.refresh(worker)
        return worker
        
    def deactivate(self, worker_id: uuid.UUID) -> ModelWorker:
        worker = self.get_worker(worker_id)
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        worker.status = "offline"
        worker.is_active = False
        self.db.commit()
        self.db.refresh(worker)
        return worker
