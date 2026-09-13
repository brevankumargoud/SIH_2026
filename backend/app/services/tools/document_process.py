import uuid
import os
import json
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.schemas.agent import ToolResult
from app.services.tools.base import BaseTool
from app.services.tools.registry import ToolRegistry
from app.services.security_policy import SecurityPolicyService
from app.services.multimodal_processor import MultimodalProcessor

@ToolRegistry.register("document_process")
class DocumentProcessTool(BaseTool):
    def __init__(self, db: Session, workspace_id: uuid.UUID = None, **kwargs):
        self.db = db
        self.workspace_id = workspace_id

    @property
    def name(self) -> str:
        return "Document Processing Tool"

    @property
    def description(self) -> str:
        return "Extracts structured text from local multimodal files (PDF, PNG, JPG, WEBP). Supports OCR."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "The local path of the document or image."}
            },
            "required": ["filepath"]
        }

    def execute(self, filepath: str, **kwargs) -> ToolResult:
        if not filepath:
            return ToolResult(success=False, output=None, error="Filepath is required")
            
        policy = SecurityPolicyService(self.db)
        decision = policy.evaluate_file_access(filepath, "read", workspace_id=self.workspace_id)
        
        if not decision.allowed:
            return ToolResult(success=False, output=None, error=f"Security Policy Denied: {decision.reason}")
            
        target_path = decision.restrictions.get("resolved_path")
        if not target_path or not os.path.exists(target_path):
            return ToolResult(success=False, output=None, error=f"File not found: {filepath}")
            
        # Get extension
        ext = target_path.split(".")[-1].lower()
        if ext not in ["txt", "md", "pdf", "png", "jpg", "jpeg", "webp"]:
            return ToolResult(success=False, output=None, error=f"Unsupported format: {ext}")
            
        try:
            processor = MultimodalProcessor(db=self.db)
            extracted_pages = processor.process_file(target_path, ext)
            
            output_blocks = []
            for page in extracted_pages:
                block = f"--- Page {page.page_number} ---\nMetadata: {json.dumps(page.metadata)}\nText:\n{page.text.strip()}\n"
                output_blocks.append(block)
                
            final_text = "\n".join(output_blocks)
            if not final_text.strip():
                final_text = "No content extracted."
                
            return ToolResult(
                success=True,
                output=final_text[:15000],  # Bound output size for the orchestrator
                metadata={"pages_processed": len(extracted_pages), "format": ext}
            )
        except Exception as e:
            return ToolResult(success=False, output=None, error=f"Processing failed: {str(e)}")
