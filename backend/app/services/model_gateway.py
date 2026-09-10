import time
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from app.models.model_worker import ModelWorker
from app.models.model import Model
from app.schemas.model_gateway import InferenceRequest, InferenceResponse
from app.services.model_worker_client import ModelWorkerClient

logger = logging.getLogger(__name__)

class ModelGatewayService:
    def __init__(self, db: Session):
        self.db = db

    def select_model_and_worker(self, request: InferenceRequest) -> tuple[Model, ModelWorker]:
        # Query active models on available active workers
        stmt = (
            select(Model)
            .join(ModelWorker)
            .where(Model.is_active == True)
            .where(ModelWorker.is_active == True)
            .where(ModelWorker.status == "available")
        )
        candidates = self.db.execute(stmt).scalars().all()
        
        if not candidates:
            raise HTTPException(status_code=503, detail="No available model workers.")

        eligible_models = []
        for model in candidates:
            # Check minimum context length
            if request.min_context_length and (model.context_length is None or model.context_length < request.min_context_length):
                continue
                
            # Check modalities
            if request.required_modalities:
                if not all(m in model.modalities for m in request.required_modalities):
                    continue
                    
            # Check capabilities
            if request.required_capabilities:
                if not all(c in model.capabilities for c in request.required_capabilities):
                    continue
                    
            eligible_models.append(model)
            
        if not eligible_models:
            raise HTTPException(status_code=400, detail="No available models match the required capabilities, modalities, or context length.")
            
        # Try preferred model
        if request.preferred_model:
            for model in eligible_models:
                if model.model_identifier == request.preferred_model:
                    return model, model.worker
                    
        # Deterministic tie-breaker: sort by context length (desc), then ID
        eligible_models.sort(key=lambda m: (m.context_length or 0, str(m.id)), reverse=True)
        selected_model = eligible_models[0]
        return selected_model, selected_model.worker

    def process_inference(self, request: InferenceRequest) -> InferenceResponse:
        model, worker = self.select_model_and_worker(request)
        
        client = ModelWorkerClient(
            ip_address=worker.ip_address,
            port=worker.port,
            protocol=worker.protocol
        )
        
        messages_payload = []
        for msg in request.messages:
            payload_msg = {"role": msg.role, "content": msg.content}
            if msg.images:
                payload_msg["images"] = msg.images
            messages_payload.append(payload_msg)
        
        start_time = time.time()
        # ModelWorkerClient.generate() returns None on failure instead of throwing
        response = client.generate(
            model=model.model_identifier,
            messages=messages_payload,
            parameters=request.parameters
        )
        latency_ms = int((time.time() - start_time) * 1000)
        
        if not response:
            logger.error(f"Inference failed or timed out on worker {worker.id}")
            raise HTTPException(status_code=502, detail="Worker inference failed or timed out.")
            
        return InferenceResponse(
            output=response.get("output", ""),
            model=response.get("model", model.model_identifier),
            worker_id=worker.id,
            metadata=response.get("metadata", {}),
            latency_ms=latency_ms
        )
