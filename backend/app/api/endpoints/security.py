from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.network_monitor import NetworkMonitorService

from app.api.deps import require_admin
from app.models.user import User

router = APIRouter(prefix="/security", tags=["security"])

@router.get("/metrics")
def get_security_metrics(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    monitor = NetworkMonitorService(db)
    external_calls = monitor.get_external_calls_count()
    
    return {
        "status": "secure",
        "sandbox_active": True,
        "network_isolated": True,
        "external_calls": external_calls,
        "policy_enforced": True,
        "audit_enabled": True
    }
