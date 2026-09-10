import pytest
from fastapi.testclient import TestClient
import uuid
import io

from app.main import app
from sqlalchemy import text
from app.db.database import SessionLocal
from app.models.workspace import Workspace
from app.models.user import User

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    db = SessionLocal()
    # Create User
    test_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"raguser_{test_id}",
        email=f"raguser_{test_id}@example.com",
        password_hash="test",
        full_name="RAG User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create Workspace
    ws = Workspace(
        name="RAG Workspace",
        description="Test workspace for RAG",
        created_by=user.id
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)
    
    yield {"user_id": str(user.id), "workspace_id": str(ws.id)}
    
    # Clean up dependent records
    db.execute(text("DELETE FROM document_chunks"))
    db.execute(text("DELETE FROM documents"))
    db.execute(text("DELETE FROM knowledge_bases"))
    db.execute(text("DELETE FROM messages"))
    db.execute(text("DELETE FROM conversations"))
    db.commit()
    
    db.delete(ws)
    db.delete(user)
    db.commit()
    db.close()

def test_kb_crud(setup_db):
    res = client.post("/knowledge-bases", json={
        "workspace_id": setup_db["workspace_id"],
        "user_id": setup_db["user_id"],
        "name": "Test KB"
    })
    assert res.status_code == 200
    kb_id = res.json()["id"]

    res_list = client.get(f"/knowledge-bases?workspace_id={setup_db['workspace_id']}")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1
    
    return kb_id

def test_document_upload_and_search(setup_db):
    kb_id = test_kb_crud(setup_db)

    # Upload document
    file_content = b"This is a test document containing confidential information about project X. Project X uses a 750 degree distillation process."
    res = client.post(
        f"/knowledge-bases/{kb_id}/documents",
        data={"user_id": setup_db["user_id"]},
        files={"file": ("test_doc.txt", file_content, "text/plain")}
    )
    assert res.status_code == 200
    doc = res.json()
    assert doc["processing_status"] == "completed"
    
    # Search
    res_search = client.post(f"/knowledge-bases/{kb_id}/search", json={
        "knowledge_base_id": kb_id,
        "query": "What is the distillation temperature for Project X?",
        "top_k": 3
    })
    assert res_search.status_code == 200
    results = res_search.json()
    assert len(results) > 0
    assert "750 degree" in results[0]["content"]

def test_chat_with_rag(setup_db):
    kb_id = test_kb_crud(setup_db)
    file_content = b"The secret code is 42."
    client.post(
        f"/knowledge-bases/{kb_id}/documents",
        data={"user_id": setup_db["user_id"]},
        files={"file": ("secret.txt", file_content, "text/plain")}
    )
    
    # Create conversation
    conv_res = client.post("/conversations", json={
        "workspace_id": setup_db["workspace_id"],
        "user_id": setup_db["user_id"],
        "title": "RAG Chat"
    })
    conv_id = conv_res.json()["id"]

    # Mock gateway generating output
    from unittest.mock import patch
    with patch("app.services.model_worker_client.ModelWorkerClient.generate") as mock_gen:
        mock_gen.return_value = {
            "output": "Based on retrieved context, the secret code is 42.",
            "model": "mock-llm",
            "metadata": {"tokens": 10}
        }
        
        # Register mock worker
        client.post("/workers/register", json={
            "name": "rag-worker",
            "ip_address": "127.0.0.1",
            "port": 8002,
            "models": [{"model_identifier": "mock-llm", "name": "LLM", "model_type": "llm", "capabilities": ["chat"]}]
        })
        
        chat_req = {
            "content": "What is the secret code?",
            "required_capabilities": ["chat"],
            "knowledge_base_ids": [kb_id],
            "use_knowledge": True
        }
        
        res = client.post(f"/conversations/{conv_id}/messages", json=chat_req)
        assert res.status_code == 200
        data = res.json()
        assert len(data["sources"]) > 0
        assert "secret.txt" in data["sources"][0]["filename"]
