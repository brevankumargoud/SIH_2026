from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.model_gateway import InferenceRequest, InferenceResponse
from app.services.model_gateway import ModelGatewayService

from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/models", tags=["models"])

@router.post("/infer", response_model=InferenceResponse)
def infer(request: InferenceRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Intelligently routes inference request to the most suitable local model worker.
    """
    gateway = ModelGatewayService(db)
    return gateway.process_inference(request)
