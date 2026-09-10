import uuid
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.artifact import Artifact
from app.models.agent_run import AgentRun
from app.api.deps import get_current_user, require_workspace_access, require_admin
from app.models.user import User

router = APIRouter(prefix="/artifacts", tags=["artifacts"])

@router.get("/{artifact_id}")
def download_artifact(
    artifact_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    artifact = db.get(Artifact, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
        
    # To check access, we must find the workspace it belongs to.
    # Artifact belongs to AgentRun -> Agent -> Workspace
    run = db.get(AgentRun, artifact.agent_run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Artifact context not found")
        
    # require_workspace_access will raise 403 if they don't have access
    require_workspace_access(run.agent.workspace_id, db, current_user)
    
    if not os.path.exists(artifact.storage_path):
        raise HTTPException(status_code=404, detail="File physically missing")
        
    return FileResponse(
        path=artifact.storage_path,
        filename=artifact.name,
        media_type=artifact.mime_type
    )
