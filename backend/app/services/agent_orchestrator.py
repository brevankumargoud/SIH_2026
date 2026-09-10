import json
import logging
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import select

from app.models.agent import Agent
from app.models.agent_run import AgentRun
from app.models.tool_execution import ToolExecution
from app.models.agent_tool import AgentTool
from app.models.tool import Tool
from app.models.workspace import Workspace
from app.schemas.model_gateway import InferenceRequest, MessagePayload
from app.services.model_gateway import ModelGatewayService

from app.services.tools.registry import ToolRegistry
# Ensure tools are imported to register themselves
import app.services.tools.knowledge_search
import app.services.tools.calculation
import app.services.tools.file_read
import app.services.tools.file_write
import app.services.tools.code_execution
import app.services.tools.document_process
import app.services.tools.deliverables

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self, db: Session, agent_id: uuid.UUID):
        self.db = db
        self.agent_id = agent_id
        
        self.agent = self.db.get(Agent, agent_id)
        if not self.agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        if not self.agent.is_active:
            raise HTTPException(status_code=400, detail="Agent is inactive")

        # Load allowed tools
        stmt = select(Tool).join(AgentTool).where(AgentTool.agent_id == agent_id, Tool.is_enabled == True)
        self.allowed_tools = self.db.execute(stmt).scalars().all()
        self.allowed_tool_names = {t.name: t for t in self.allowed_tools}
        
    def execute(self, run_id: uuid.UUID, input_data: Dict[str, Any], max_iterations: int = 5, preferred_model: str = None) -> AgentRun:
        run_record = self.db.get(AgentRun, run_id)
        if not run_record:
            raise HTTPException(status_code=404, detail="AgentRun not found")

        run_record.status = "running"
        run_record.started_at = datetime.now(timezone.utc)
        self.db.commit()

        # Build tools description
        tools_desc = []
        for t in self.allowed_tools:
            try:
                kwargs_to_inject = {
                    "db": self.db, 
                    "agent_id": self.agent_id, 
                    "agent_run_id": run_id, 
                    "workspace_id": self.agent.workspace_id
                }
                try:
                    tool_inst = ToolRegistry.get_tool(t.tool_type, **kwargs_to_inject)
                except TypeError:
                    tool_inst = ToolRegistry.get_tool(t.tool_type)
                
                tools_desc.append({
                    "name": tool_inst.name,
                    "description": tool_inst.description,
                    "parameters": tool_inst.parameters_schema
                })
            except Exception as e:
                logger.warning(f"Failed to load tool {t.name}: {e}")

        system_prompt = self.agent.system_prompt or "You are an AI assistant."
        system_instruction = (
            f"{system_prompt}\n\n"
            f"You have access to the following tools:\n{json.dumps(tools_desc, indent=2)}\n\n"
            "You must respond in valid JSON format only, with the following structure:\n"
            "{\n"
            '  "thought": "Your reasoning about what to do next",\n'
            '  "action": "The name of the tool to use, or \'final_answer\' to deliver the result",\n'
            '  "action_input": "The parameters for the tool as a JSON object, or the final answer text if action is \'final_answer\'"\n'
            "}\n"
        )

        messages = [
            MessagePayload(role="system", content=system_instruction),
            MessagePayload(role="user", content=json.dumps(input_data))
        ]

        gateway = ModelGatewayService(self.db)
        iterations = 0
        final_answer = None
        error_msg = None

        while iterations < max_iterations:
            iterations += 1
            
            # Model execution
            req = InferenceRequest(
                messages=messages,
                preferred_model=preferred_model,
                required_capabilities=["chat"],
                parameters={"format": "json"} # enforce JSON if supported
            )
            
            try:
                resp = gateway.process_inference(req)
                raw_output = resp.output.strip()
                # Parse JSON
                try:
                    # simplistic extraction just in case there are markdown blocks
                    if "```json" in raw_output:
                        raw_output = raw_output.split("```json")[1].split("```")[0].strip()
                    elif "```" in raw_output:
                        raw_output = raw_output.split("```")[1].split("```")[0].strip()
                        
                    parsed = json.loads(raw_output)
                except Exception as e:
                    messages.append(MessagePayload(role="assistant", content=raw_output))
                    messages.append(MessagePayload(role="user", content='{"error": "Failed to parse JSON. Please return valid JSON with thought, action, action_input."}'))
                    continue

                messages.append(MessagePayload(role="assistant", content=json.dumps(parsed)))

                thought = parsed.get("thought", "")
                action = parsed.get("action", "")
                action_input = parsed.get("action_input", {})

                if action == "final_answer":
                    final_answer = action_input
                    break
                
                # Check Tool allowlist
                if action not in self.allowed_tool_names:
                    msg = f"Tool '{action}' is not allowed or does not exist."
                    messages.append(MessagePayload(role="user", content=json.dumps({"tool_error": msg})))
                    # record failed execution
                    continue
                
                tool_record = self.allowed_tool_names[action]
                
                # Check Security Policy
                from app.services.security_policy import SecurityPolicyService
                policy_svc = SecurityPolicyService(self.db)
                decision = policy_svc.evaluate_tool_execution(
                    tool_name=action,
                    tool_type=tool_record.tool_type,
                    agent_id=self.agent_id,
                    workspace_id=self.agent.workspace_id,
                    user_id=run_record.user_id,
                    run_id=run_id
                )
                
                if not decision.allowed:
                    msg = f"Security Policy Denied execution of '{action}': {decision.reason}"
                    messages.append(MessagePayload(role="user", content=json.dumps({"tool_error": msg})))
                    # optionally log a failed tool_execution record here
                    continue
                
                # Execute tool
                tool_exec = ToolExecution(
                    agent_run_id=run_id,
                    tool_id=tool_record.id,
                    input_data=action_input if isinstance(action_input, dict) else {"input": action_input},
                    status="running",
                    started_at=datetime.now(timezone.utc)
                )
                self.db.add(tool_exec)
                self.db.commit()

                tool_result_output = None
                try:
                    kwargs_to_inject = {
                        "db": self.db, 
                        "agent_id": self.agent_id, 
                        "agent_run_id": run_id, 
                        "workspace_id": self.agent.workspace_id
                    }
                    try:
                        tool_inst = ToolRegistry.get_tool(tool_record.tool_type, **kwargs_to_inject)
                    except TypeError: # If tool doesn't accept them, instantiate safely
                        tool_inst = ToolRegistry.get_tool(tool_record.tool_type)
                    
                    # Convert action_input dict to kwargs
                    kwargs = action_input if isinstance(action_input, dict) else {"expression": str(action_input)}
                    result = tool_inst.execute(**kwargs)
                    
                    tool_exec.status = "completed" if result.success else "failed"
                    tool_exec.output_data = {"output": result.output, "metadata": result.metadata}
                    tool_exec.error_message = result.error
                    
                    tool_result_output = result.output if result.success else result.error
                except Exception as e:
                    tool_exec.status = "failed"
                    tool_exec.error_message = str(e)
                    tool_result_output = f"Internal Tool Error: {str(e)}"
                
                tool_exec.completed_at = datetime.now(timezone.utc)
                self.db.commit()

                # Add observation to messages
                messages.append(MessagePayload(role="user", content=json.dumps({
                    "tool": action,
                    "observation": tool_result_output
                })))

            except Exception as e:
                error_msg = str(e)
                break

        # Finalize run
        run_record.completed_at = datetime.now(timezone.utc)
        if final_answer:
            run_record.status = "completed"
            run_record.output_data = {"final_answer": final_answer, "iterations": iterations}
        else:
            run_record.status = "failed"
            run_record.error_message = error_msg or "Max iterations reached without final_answer."
        
        self.db.commit()
        self.db.refresh(run_record)
        return run_record
