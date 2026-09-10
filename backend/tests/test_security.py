import pytest
import uuid
import os
from app.db.database import SessionLocal
from app.services.security_policy import SecurityPolicyService
from app.models.user import User
from app.models.workspace import Workspace

@pytest.fixture(scope="module")
def setup_db():
    db = SessionLocal()
    # Create User
    test_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"secuser_{test_id}",
        email=f"secuser_{test_id}@example.com",
        password_hash="test",
        full_name="Security User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create Workspace
    ws = Workspace(
        name="Security Workspace",
        description="Test workspace for Security",
        created_by=user.id
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)
    
    yield {"user_id": str(user.id), "workspace_id": str(ws.id)}
    
    db.delete(ws)
    db.delete(user)
    db.commit()
    db.close()

def test_security_policy_valid_tool(setup_db):
    db = SessionLocal()
    policy_svc = SecurityPolicyService(db)
    
    decision = policy_svc.evaluate_tool_execution(
        tool_name="MyCalc",
        tool_type="calculation",
        agent_id=uuid.uuid4(),
        workspace_id=uuid.UUID(setup_db["workspace_id"]),
        user_id=uuid.UUID(setup_db["user_id"])
    )
    
    assert decision.allowed is True
    assert decision.policy == "allow_registered_tool"
    db.close()

def test_security_policy_invalid_tool(setup_db):
    db = SessionLocal()
    policy_svc = SecurityPolicyService(db)
    
    decision = policy_svc.evaluate_tool_execution(
        tool_name="EvilHax",
        tool_type="unregistered_hacking_tool",
        agent_id=uuid.uuid4(),
        workspace_id=uuid.UUID(setup_db["workspace_id"]),
        user_id=uuid.UUID(setup_db["user_id"])
    )
    
    assert decision.allowed is False
    assert decision.policy == "deny_unknown_tool"
    db.close()

def test_security_policy_path_traversal(setup_db):
    db = SessionLocal()
    policy_svc = SecurityPolicyService(db)
    
    allowed_dir = os.path.abspath(os.getenv("RAG_STORAGE_PATH", "/tmp/rag_storage"))
    
    # Normal file
    decision1 = policy_svc.evaluate_file_access(
        filepath=os.path.join(allowed_dir, "my_safe_file.txt"),
        mode="read",
        workspace_id=uuid.UUID(setup_db["workspace_id"])
    )
    assert decision1.allowed is True
    
    # Path traversal attack
    decision2 = policy_svc.evaluate_file_access(
        filepath=os.path.join(allowed_dir, "../../../etc/passwd"),
        mode="read",
        workspace_id=uuid.UUID(setup_db["workspace_id"])
    )
    assert decision2.allowed is False
    db.close()

def test_sandbox_manager_mock():
    from unittest.mock import patch
    from app.services.sandbox_manager import SandboxManager, SandboxExecutionResult
    
    manager = SandboxManager()
    
    with patch("subprocess.run") as mock_run:
        class MockResult:
            returncode = 0
            stdout = "Hello World"
            stderr = ""
        mock_run.return_value = MockResult()
        
        res = manager.execute_python(code="print('Hello World')")
        
        assert res.success is True
        assert res.stdout == "Hello World"
        
        # Verify network isolation is in the docker command
        called_args = mock_run.call_args[0][0]
        assert "docker" in called_args
        assert "--network" in called_args
        assert "none" in called_args
        assert "--memory" in called_args
        assert "--pids-limit" in called_args
