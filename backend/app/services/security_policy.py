import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from datetime import datetime, timezone
import os
import re

class PolicyDecision(BaseModel):
    allowed: bool
    reason: str
    policy: str
    restrictions: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class SecurityPolicyService:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_tool_execution(
        self, 
        tool_name: str, 
        tool_type: str, 
        agent_id: uuid.UUID, 
        workspace_id: uuid.UUID, 
        user_id: Optional[uuid.UUID] = None,
        run_id: Optional[uuid.UUID] = None
    ) -> PolicyDecision:
        
        # Risk map
        TOOL_RISK_MAP = {
            "knowledge_search": "SAFE",
            "calculation": "SAFE",
            "file_read": "CONTROLLED",
            "file_write": "CONTROLLED",
            "document_process": "CONTROLLED",
            "create_docx": "CONTROLLED",
            "create_xlsx": "CONTROLLED",
            "create_pptx": "CONTROLLED",
            "create_code_artifact": "CONTROLLED",
            "code_execution": "SANDBOXED"
        }
        
        risk = TOOL_RISK_MAP.get(tool_type)
        
        if not risk:
            decision = PolicyDecision(allowed=False, reason=f"Unknown tool_type {tool_type}", policy="deny_unknown_tool")
        else:
            # We can expand to more granular policies later
            decision = PolicyDecision(allowed=True, reason=f"Tool has valid risk profile {risk}", policy="allow_registered_tool")
            
        self._audit_decision(
            action="evaluate_tool_execution",
            decision=decision,
            user_id=user_id,
            workspace_id=workspace_id,
            details={"tool_name": tool_name, "tool_type": tool_type, "agent_id": str(agent_id), "run_id": str(run_id) if run_id else None}
        )
        return decision

    def evaluate_file_access(
        self,
        filepath: str,
        mode: str,
        workspace_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> PolicyDecision:
        # Resolve path preventing symlink escapes
        allowed_dir = os.path.realpath(os.getenv("RAG_STORAGE_PATH", "/tmp/rag_storage"))
        target_path = os.path.realpath(filepath)
        
        if not target_path.startswith(allowed_dir):
            decision = PolicyDecision(allowed=False, reason="Path traversal detected or access outside allowed directory.", policy="deny_outside_workspace")
        else:
            decision = PolicyDecision(allowed=True, reason="Path is within allowed storage boundary.", policy="allow_within_workspace", restrictions={"resolved_path": target_path})
            
        self._audit_decision(
            action=f"evaluate_file_{mode}",
            decision=decision,
            user_id=user_id,
            workspace_id=workspace_id,
            details={"filepath": filepath, "resolved_path": target_path}
        )
        
        return decision

    def _audit_decision(self, action: str, decision: PolicyDecision, user_id: Optional[uuid.UUID], workspace_id: Optional[uuid.UUID], details: dict):
        log_details = {
            "policy": decision.policy,
            "reason": decision.reason,
            **details
        }
        audit = AuditLog(
            user_id=user_id,
            workspace_id=workspace_id,
            action=action,
            status="allowed" if decision.allowed else "denied",
            details=log_details
        )
        self.db.add(audit)
        self.db.commit()
