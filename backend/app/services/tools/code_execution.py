import uuid
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.schemas.agent import ToolResult
from app.services.tools.base import BaseTool
from app.services.tools.registry import ToolRegistry
from app.services.security_policy import SecurityPolicyService
from app.services.sandbox_manager import SandboxManager

@ToolRegistry.register("code_execution")
class CodeExecutionTool(BaseTool):
    def __init__(self, db: Session, workspace_id: uuid.UUID = None, **kwargs):
        self.db = db
        self.workspace_id = workspace_id

    @property
    def name(self) -> str:
        return "Code Execution Sandbox"

    @property
    def description(self) -> str:
        return "Executes Python code in a secure, network-isolated Docker sandbox."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The Python code to execute."}
            },
            "required": ["code"]
        }

    def execute(self, code: str, **kwargs) -> ToolResult:
        if not code:
            return ToolResult(success=False, output=None, error="Code is required")
        
        # We don't evaluate code contents, but we do evaluate if code execution is permitted
        # The orchestrator handles evaluate_tool_execution, but we can do an extra check here if needed.
        
        sandbox = SandboxManager()
        result = sandbox.execute_python(code=code)
        
        # Format the output for the agent
        output_str = f"Exit Code: {result.exit_code}\nDuration: {result.duration}s\n"
        if result.stdout:
            output_str += f"\n--- STDOUT ---\n{result.stdout}\n"
        if result.stderr:
            output_str += f"\n--- STDERR ---\n{result.stderr}\n"
        if result.error:
            output_str += f"\n--- ERROR ---\n{result.error}\n"
            
        return ToolResult(
            success=result.success,
            output=output_str,
            metadata={
                "exit_code": result.exit_code,
                "duration": result.duration,
                "sandbox_active": True,
                "network_isolated": True
            },
            error=result.error if not result.success else None
        )
