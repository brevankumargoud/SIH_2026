import os
import uuid
from typing import Dict, Any
from app.schemas.agent import ToolResult
from app.services.tools.base import BaseTool
from app.services.tools.registry import ToolRegistry
# Need DB session to record the artifact
from sqlalchemy.orm import Session
from app.models.artifact import Artifact

@ToolRegistry.register("file_write")
class FileWriteTool(BaseTool):
    def __init__(self, db: Session, agent_run_id: uuid.UUID = None, workspace_id: uuid.UUID = None, **kwargs):
        self.db = db
        self.agent_run_id = agent_run_id
        self.workspace_id = workspace_id
        self.allowed_dir = os.getenv("RAG_STORAGE_PATH", "/tmp/rag_storage")

    @property
    def name(self) -> str:
        return "File Write Tool"

    @property
    def description(self) -> str:
        return "Writes content to a file and generates an artifact. Input must be filename and content."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "The name of the file to write."},
                "content": {"type": "string", "description": "The content to write into the file."}
            },
            "required": ["filename", "content"]
        }

    def execute(self, filename: str, content: str, **kwargs) -> ToolResult:
        if not filename or not content:
            return ToolResult(success=False, output=None, error="Filename and content are required")
        
        from app.services.security_policy import SecurityPolicyService
        policy = SecurityPolicyService(self.db)
        decision = policy.evaluate_file_access(filename, "write", workspace_id=self.workspace_id)
        
        if not decision.allowed:
            return ToolResult(success=False, output=None, error=f"Security Policy Denied: {decision.reason}")
            
        target_path = decision.restrictions.get("resolved_path")
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Create artifact record
            art = Artifact(
                workspace_id=self.workspace_id,
                agent_run_id=self.agent_run_id,
                name=filename,
                artifact_type="document",
                storage_path=target_path
            )
            self.db.add(art)
            self.db.commit()
            
            return ToolResult(
                success=True, 
                output=f"Successfully wrote {filename}", 
                metadata={"filename": filename, "artifact_id": str(art.id)}
            )
        except Exception as e:
            return ToolResult(success=False, output=None, error=f"Failed to write file: {str(e)}")
