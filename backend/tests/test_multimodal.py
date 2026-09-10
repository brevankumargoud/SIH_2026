import pytest
import uuid
import os
import tempfile
from app.db.database import SessionLocal
from app.models.user import User
from app.models.workspace import Workspace
from app.models.model_worker import ModelWorker
from app.models.model import Model
from app.services.model_gateway import ModelGatewayService
from app.schemas.model_gateway import InferenceRequest, MessagePayload
from fastapi import HTTPException
from app.services.multimodal_processor import MultimodalProcessor
from app.services.tools.document_process import DocumentProcessTool
from app.services.tools.registry import ToolRegistry

@pytest.fixture(scope="module")
def setup_db():
    db = SessionLocal()
    test_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"multiuser_{test_id}",
        email=f"multiuser_{test_id}@example.com",
        password_hash="test",
        full_name="Multi User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    ws = Workspace(name="Multi WS", created_by=user.id)
    db.add(ws)
    db.commit()
    db.refresh(ws)
    
    # Text worker
    worker_text = ModelWorker(
        name="Text Worker",
        ip_address="127.0.0.1",
        port=8001,
        status="available"
    )
    db.add(worker_text)
    db.commit()
    db.refresh(worker_text)
    
    model_text = Model(
        worker_id=worker_text.id,
        name="LLM Text",
        model_identifier="text-llm",
        model_type="llm",
        modalities=["text"],
        capabilities=["chat"]
    )
    db.add(model_text)
    db.commit()
    
    # Multimodal worker
    worker_mm = ModelWorker(
        name="MM Worker",
        ip_address="127.0.0.1",
        port=8002,
        status="available"
    )
    db.add(worker_mm)
    db.commit()
    db.refresh(worker_mm)
    
    model_mm = Model(
        worker_id=worker_mm.id,
        name="LLM Vision",
        model_identifier="vision-llm",
        model_type="llm",
        modalities=["text", "image", "vision"],
        capabilities=["chat", "multimodal"]
    )
    db.add(model_mm)
    db.commit()
    
    yield {"user_id": str(user.id), "workspace_id": str(ws.id), "mm_worker_id": str(worker_mm.id), "text_worker_id": str(worker_text.id)}
    
    db.delete(model_mm)
    db.delete(worker_mm)
    db.delete(model_text)
    db.delete(worker_text)
    db.delete(ws)
    db.delete(user)
    db.commit()
    db.close()

def test_model_gateway_routing_multimodal(setup_db):
    db = SessionLocal()
    gateway = ModelGatewayService(db)
    
    # Request text only
    req_text = InferenceRequest(
        messages=[MessagePayload(role="user", content="hello")],
        required_modalities=["text"]
    )
    model, worker = gateway.select_model_and_worker(req_text)
    assert model is not None # Any model can do text
    
    # Request image
    req_image = InferenceRequest(
        messages=[MessagePayload(role="user", content="describe this", images=["base64string"])],
        required_modalities=["image", "vision"]
    )
    model_mm, worker_mm = gateway.select_model_and_worker(req_image)
    assert model_mm.model_identifier == "vision-llm"
    assert "image" in model_mm.modalities
    
    # Request nonexistent modality
    req_audio = InferenceRequest(
        messages=[MessagePayload(role="user", content="listen")],
        required_modalities=["audio"]
    )
    with pytest.raises(HTTPException) as exc:
        gateway.select_model_and_worker(req_audio)
    assert exc.value.status_code == 400
    
    db.close()

def test_multimodal_processor_text_file(setup_db):
    db = SessionLocal()
    processor = MultimodalProcessor(db=db)
    
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp.write(b"Hello from txt")
        tmp_name = tmp.name
        
    pages = processor.process_file(tmp_name, "txt")
    assert len(pages) == 1
    assert pages[0].text == "Hello from txt"
    
    os.remove(tmp_name)
    db.close()

def test_document_process_tool(setup_db):
    db = SessionLocal()
    # Need to put the test file in the allowed rag storage path
    allowed_dir = os.path.abspath(os.getenv("RAG_STORAGE_PATH", "/tmp/rag_storage"))
    os.makedirs(allowed_dir, exist_ok=True)
    
    test_file = os.path.join(allowed_dir, "test_doc.md")
    with open(test_file, "w") as f:
        f.write("Test document content.")
        
    tool = ToolRegistry.get_tool("document_process", db=db, workspace_id=uuid.UUID(setup_db["workspace_id"]))
    
    # Test valid execution
    result = tool.execute(filepath=test_file)
    assert result.success is True
    assert "Test document content." in result.output
    
    # Test path traversal denial
    result_fail = tool.execute(filepath="../../../etc/passwd")
    assert result_fail.success is False
    assert "Security Policy Denied" in result_fail.error
    
    os.remove(test_file)
    db.close()
