import os
import uuid
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.schemas.agent import ToolResult
from app.services.tools.base import BaseTool
from app.services.tools.registry import ToolRegistry

@ToolRegistry.register("file_read")
class FileReadTool(BaseTool):
    def __init__(self, db: Session, workspace_id: uuid.UUID = None, **kwargs):
        self.db = db
        self.workspace_id = workspace_id

    @property
    def name(self) -> str:
        return "File Read Tool"

    @property
    def description(self) -> str:
        return "Reads the contents of a local file. Input must be a filename present in the workspace."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "The name of the file to read."}
            },
            "required": ["filename"]
        }

    def execute(self, filename: str, **kwargs) -> ToolResult:
        if not filename:
            return ToolResult(success=False, output=None, error="Filename is required")
        
        from app.services.security_policy import SecurityPolicyService
        policy = SecurityPolicyService(self.db)
        decision = policy.evaluate_file_access(filename, "read", workspace_id=self.workspace_id)
        
        if not decision.allowed:
            return ToolResult(success=False, output=None, error=f"Security Policy Denied: {decision.reason}")
            
        target_path = decision.restrictions.get("resolved_path")
        if not target_path or not os.path.exists(target_path):
            return ToolResult(success=False, output=None, error=f"File not found or access denied: {filename}")
            
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return ToolResult(success=True, output=content, metadata={"filename": filename, "size": len(content)})
        except Exception as e:
            return ToolResult(success=False, output=None, error=f"Failed to read file: {str(e)}")
