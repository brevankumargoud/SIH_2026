import uuid
import os
import json
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.schemas.agent import ToolResult
from app.services.tools.base import BaseTool
from app.services.tools.registry import ToolRegistry
from app.services.security_policy import SecurityPolicyService
from app.services.generators import get_generator
from app.models.artifact import Artifact

def _generate_artifact(
    db: Session,
    workspace_id: uuid.UUID,
    agent_run_id: uuid.UUID,
    artifact_type: str,
    ext: str,
    filename: str,
    data: Dict[str, Any]
) -> ToolResult:
    if not filename:
        return ToolResult(success=False, output=None, error="Filename is required")
        
    policy = SecurityPolicyService(db)
    
    # Force the path to be inside rag_storage
    allowed_dir = os.path.realpath(os.getenv("RAG_STORAGE_PATH", "/tmp/rag_storage"))
    safe_filename = os.path.basename(filename)
    if not safe_filename.endswith(ext):
        safe_filename += ext
        
    target_path = os.path.join(allowed_dir, safe_filename)
    
    decision = policy.evaluate_file_access(target_path, "write", workspace_id=workspace_id)
    if not decision.allowed:
        return ToolResult(success=False, output=None, error=f"Security Policy Denied: {decision.reason}")
        
    try:
        generator = get_generator(artifact_type)
        generated_path = generator.generate(target_path, data)
        
        # Validation
        is_valid, validation_msg = generator.validate(generated_path)
        if not is_valid:
            # Clean up invalid artifact
            if os.path.exists(generated_path):
                os.remove(generated_path)
            return ToolResult(success=False, output=None, error=f"Artifact generated but failed validation: {validation_msg}")
            
        file_size = os.path.getsize(generated_path)
        
        # Persist to DB
        artifact = Artifact(
            agent_run_id=agent_run_id,
            name=safe_filename,
            artifact_type=artifact_type,
            mime_type=f"application/{artifact_type}",
            storage_path=generated_path,
            file_size_bytes=file_size
        )
        db.add(artifact)
        db.commit()
        db.refresh(artifact)
        
        return ToolResult(
            success=True,
            output=f"Artifact successfully created: {safe_filename} (ID: {artifact.id})\nValidation: {validation_msg}",
            metadata={"artifact_id": str(artifact.id), "size": file_size, "path": generated_path}
        )
        
    except Exception as e:
        return ToolResult(success=False, output=None, error=f"Generation failed: {str(e)}")


@ToolRegistry.register("create_docx")
class CreateDocxTool(BaseTool):
    def __init__(self, db: Session, workspace_id: uuid.UUID = None, agent_run_id: uuid.UUID = None, **kwargs):
        self.db = db
        self.workspace_id = workspace_id
        self.agent_run_id = agent_run_id

    @property
    def name(self) -> str:
        return "Create DOCX Document"

    @property
    def description(self) -> str:
        return "Creates a formatted Microsoft Word (.docx) deliverable."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Name of the output file (e.g. report.docx)"},
                "data": {
                    "type": "object", 
                    "description": "Structured data. Ex: {'title': '...', 'blocks': [{'type': 'heading', 'level': 1, 'content': '...'}, {'type': 'paragraph', 'content': '...'}], 'sources': []}"
                }
            },
            "required": ["filename", "data"]
        }

    def execute(self, filename: str, data: Dict[str, Any], **kwargs) -> ToolResult:
        return _generate_artifact(self.db, self.workspace_id, self.agent_run_id, "docx", ".docx", filename, data)


@ToolRegistry.register("create_xlsx")
class CreateXlsxTool(BaseTool):
    def __init__(self, db: Session, workspace_id: uuid.UUID = None, agent_run_id: uuid.UUID = None, **kwargs):
        self.db = db
        self.workspace_id = workspace_id
        self.agent_run_id = agent_run_id

    @property
    def name(self) -> str:
        return "Create XLSX Workbook"

    @property
    def description(self) -> str:
        return "Creates a Microsoft Excel (.xlsx) spreadsheet."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "data": {
                    "type": "object",
                    "description": "Ex: {'sheets': [{'name': 'Data', 'headers': ['A','B'], 'rows': [[1,2], [3,4]]}], 'sources': []}"
                }
            },
            "required": ["filename", "data"]
        }

    def execute(self, filename: str, data: Dict[str, Any], **kwargs) -> ToolResult:
        return _generate_artifact(self.db, self.workspace_id, self.agent_run_id, "xlsx", ".xlsx", filename, data)


@ToolRegistry.register("create_pptx")
class CreatePptxTool(BaseTool):
    def __init__(self, db: Session, workspace_id: uuid.UUID = None, agent_run_id: uuid.UUID = None, **kwargs):
        self.db = db
        self.workspace_id = workspace_id
        self.agent_run_id = agent_run_id

    @property
    def name(self) -> str:
        return "Create PPTX Presentation"

    @property
    def description(self) -> str:
        return "Creates a Microsoft PowerPoint (.pptx) presentation."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "data": {
                    "type": "object",
                    "description": "Ex: {'title': '...', 'subtitle': '...', 'slides': [{'title': '...', 'bullets': ['...']}], 'sources': []}"
                }
            },
            "required": ["filename", "data"]
        }

    def execute(self, filename: str, data: Dict[str, Any], **kwargs) -> ToolResult:
        return _generate_artifact(self.db, self.workspace_id, self.agent_run_id, "pptx", ".pptx", filename, data)


@ToolRegistry.register("create_code_artifact")
class CreateCodeArtifactTool(BaseTool):
    def __init__(self, db: Session, workspace_id: uuid.UUID = None, agent_run_id: uuid.UUID = None, **kwargs):
        self.db = db
        self.workspace_id = workspace_id
        self.agent_run_id = agent_run_id

    @property
    def name(self) -> str:
        return "Create Code Artifact"

    @property
    def description(self) -> str:
        return "Generates safe, non-executing code artifacts."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "e.g., script.py, app.js"},
                "data": {
                    "type": "object",
                    "description": "Ex: {'code': '...', 'language': 'python', 'source': '...'}"
                }
            },
            "required": ["filename", "data"]
        }

    def execute(self, filename: str, data: Dict[str, Any], **kwargs) -> ToolResult:
        return _generate_artifact(self.db, self.workspace_id, self.agent_run_id, "code", "", filename, data)
