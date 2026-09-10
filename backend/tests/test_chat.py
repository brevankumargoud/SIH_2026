import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import uuid

from app.main import app
from app.db.database import SessionLocal
from app.models.workspace import Workspace
from app.models.user import User
from app.models.model_worker import ModelWorker
from app.models.model import Model

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    db = SessionLocal()
    # Create User
    test_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"chatuser_{test_id}",
        email=f"chatuser_{test_id}@example.com",
        password_hash="test",
        full_name="Chat User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create Workspace
    ws = Workspace(
        name="Chat Workspace",
        description="Test workspace for chat",
        created_by=user.id
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)
    
    yield {"user_id": str(user.id), "workspace_id": str(ws.id)}
    
    # Cleanup (Optional)
    db.delete(ws)
    db.delete(user)
    db.commit()
    db.close()

def test_create_conversation(setup_db):
    res = client.post("/conversations", json={
        "workspace_id": setup_db["workspace_id"],
        "user_id": setup_db["user_id"],
        "title": "My first chat"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "My first chat"
    assert data["workspace_id"] == setup_db["workspace_id"]
    return data["id"]

def test_list_conversations(setup_db):
    res = client.get(f"/conversations?workspace_id={setup_db['workspace_id']}")
    assert res.status_code == 200
    assert len(res.json()) >= 1

def test_get_conversation(setup_db):
    conv_id = test_create_conversation(setup_db)
    res = client.get(f"/conversations/{conv_id}")
    assert res.status_code == 200
    assert res.json()["id"] == conv_id

def test_chat_flow(setup_db):
    conv_id = test_create_conversation(setup_db)
    
    # Setup Worker
    client.post("/workers/register", json={
        "name": "chat-worker",
        "ip_address": "127.0.0.1",
        "port": 8001,
        "models": [
            {
                "model_identifier": "chat-model-1",
                "name": "Chatter",
                "model_type": "llm",
                "capabilities": ["chat"]
            }
        ]
    })
    
    req = {
        "content": "Hello bot!",
        "required_capabilities": ["chat"]
    }
    
    with patch("app.services.model_worker_client.ModelWorkerClient.generate") as mock_gen:
        mock_gen.return_value = {
            "output": "Hello user!",
            "model": "chat-model-1",
            "metadata": {"tokens": 5}
        }
        res = client.post(f"/conversations/{conv_id}/messages", json=req)
        assert res.status_code == 200
        data = res.json()
        assert data["user_message"]["content"] == "Hello bot!"
        assert data["assistant_message"]["content"] == "Hello user!"
        assert "model" in data
        
        # Verify messages history
        res2 = client.get(f"/conversations/{conv_id}/messages")
        assert res2.status_code == 200
        msgs = res2.json()
        assert len(msgs) == 2
        assert msgs[0]["role"] == "user"
        assert msgs[1]["role"] == "assistant"
