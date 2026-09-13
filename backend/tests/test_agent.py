import pytest
from fastapi.testclient import TestClient
import uuid

from app.main import app
from sqlalchemy import text
from app.db.database import SessionLocal
from app.models.workspace import Workspace
from app.models.user import User
from app.models.agent import Agent
from app.models.tool import Tool
from app.models.agent_tool import AgentTool
from app.models.agent_knowledge_base import AgentKnowledgeBase
from app.models.knowledge_base import KnowledgeBase
import os

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    db = SessionLocal()
    # Create User
    test_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"agentuser_{test_id}",
        email=f"agentuser_{test_id}@example.com",
        password_hash="test",
        full_name="Agent User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create Workspace
    ws = Workspace(
        name="Agent Workspace",
        description="Test workspace for Agents",
        created_by=user.id
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)
    
    # Create an Agent
    agent = Agent(
        workspace_id=ws.id,
        name="Test Agent",
        description="A test agent",
        system_prompt="You are a test agent.",
        agent_type="custom",
        created_by=user.id
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    # Create Tools
    tool_calc = Tool(
        workspace_id=ws.id,
        name="calculate",
        tool_type="calculation",
        description="Calculate things"
    )
    db.add(tool_calc)
    db.commit()
    db.refresh(tool_calc)

    # Link tool to agent
    at = AgentTool(agent_id=agent.id, tool_id=tool_calc.id)
    db.add(at)
    db.commit()
    
    yield {"user_id": str(user.id), "workspace_id": str(ws.id), "agent_id": str(agent.id), "tool_calc_id": str(tool_calc.id)}
    
    # Clean up dependent records
    db.execute(text("DELETE FROM tool_executions"))
    db.execute(text("DELETE FROM agent_runs"))
    db.execute(text("DELETE FROM agent_tools"))
    db.execute(text("DELETE FROM tools"))
    db.execute(text("DELETE FROM agent_knowledge_bases"))
    db.execute(text("DELETE FROM agents"))
    db.execute(text("DELETE FROM workspaces"))
    db.execute(text("DELETE FROM users"))
    db.commit()
    db.close()


def test_agent_run_success(setup_db):
    agent_id = setup_db["agent_id"]

    # Mock gateway
    from unittest.mock import patch
    with patch("app.services.model_worker_client.ModelWorkerClient.generate") as mock_gen:
        # We need the mock to simulate a thinking process
        # Turn 1: Thought -> Call calculation
        # Turn 2: Thought -> final_answer
        
        mock_gen.side_effect = [
            {
                "output": '{"thought": "I need to calculate", "action": "calculate", "action_input": {"expression": "2 + 2"}}',
                "model": "mock-llm",
                "metadata": {"tokens": 10}
            },
            {
                "output": '{"thought": "I have the result", "action": "final_answer", "action_input": "The answer is 4."}',
                "model": "mock-llm",
                "metadata": {"tokens": 10}
            }
        ]
        
        # Register mock worker
        client.post("/workers/register", json={
            "name": "agent-worker",
            "ip_address": "127.0.0.1",
            "port": 8003,
            "models": [{"model_identifier": "mock-llm", "name": "LLM", "model_type": "llm", "capabilities": ["chat"]}]
        })
        
        res = client.post(f"/agents/{agent_id}/runs", json={
            "input_data": {"task": "What is 2 + 2?"},
            "user_id": setup_db["user_id"],
            "max_iterations": 5
        })
        
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["output_data"]["final_answer"] == "The answer is 4."
        assert data["output_data"]["iterations"] == 2


def test_agent_run_disallowed_tool(setup_db):
    agent_id = setup_db["agent_id"]

    from unittest.mock import patch
    with patch("app.services.model_worker_client.ModelWorkerClient.generate") as mock_gen:
        # Mock LLM tries to call a tool it doesn't have explicitly allowed
        mock_gen.side_effect = [
            {
                "output": '{"thought": "I will read a file", "action": "file_read", "action_input": {"filename": "test.txt"}}',
                "model": "mock-llm",
                "metadata": {"tokens": 10}
            },
            {
                "output": '{"thought": "Oh I cant do that", "action": "final_answer", "action_input": "I am not allowed."}',
                "model": "mock-llm",
                "metadata": {"tokens": 10}
            }
        ]
        
        res = client.post(f"/agents/{agent_id}/runs", json={
            "input_data": {"task": "Read a file"},
            "user_id": setup_db["user_id"],
            "max_iterations": 3
        })
        
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["output_data"]["final_answer"] == "I am not allowed."
