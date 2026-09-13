import os
import uuid
import tempfile
import asyncio
from io import BytesIO
from app.db.database import SessionLocal
from app.models.user import User
from app.models.workspace import Workspace
from app.models.knowledge_base import KnowledgeBase
from app.services.multimodal_processor import MultimodalProcessor
from app.services.document_service import DocumentService
from app.services.model_gateway import ModelGatewayService
from app.schemas.model_gateway import InferenceRequest, MessagePayload
from app.models.model_worker import ModelWorker
from app.models.model import Model
from app.services.tools.registry import ToolRegistry
from fastapi import HTTPException
from PIL import Image

def verify():
    db = SessionLocal()
    print("--- STARTING PHASE 9A VERIFICATION ---")
    
    # 1. SETUP
    test_id = uuid.uuid4().hex[:8]
    user = User(username=f"v_user_{test_id}", email=f"v_{test_id}@example.com", password_hash="test", full_name="Verification User")
    db.add(user)
    ws = Workspace(name="Verification WS", created_by=user.id)
    db.add(ws)
    db.commit()
    db.refresh(user)
    db.refresh(ws)
    
    kb = KnowledgeBase(workspace_id=ws.id, name="Verification KB", description="Test")
    db.add(kb)
    db.commit()
    db.refresh(kb)
    
    allowed_dir = os.path.abspath(os.getenv("RAG_STORAGE_PATH", "/tmp/rag_storage"))
    os.makedirs(allowed_dir, exist_ok=True)
    
    # 2. IMAGE PROCESSING GRACEFUL DEGRADATION
    print("\n[1] Verifying Image Processing (Graceful Degradation)...")
    img_path = os.path.join(allowed_dir, f"test_img_{test_id}.png")
    img = Image.new('RGB', (10, 10), color = 'red')
    img.save(img_path)
    
    processor = MultimodalProcessor(db=db)
    try:
        pages = processor.process_file(img_path, "png")
        print("FAIL: Expected RuntimeError due to missing tesseract, but it succeeded.")
    except RuntimeError as e:
        if "OCR Provider (Tesseract) is unavailable" in str(e):
            print("PASS: MultimodalProcessor gracefully aborted image processing due to missing OCR dependencies.")
        else:
            print(f"FAIL: Unexpected error: {e}")
            
    # 3. RAG INTEGRATION (Text PDF)
    print("\n[2] Verifying RAG Integration (PDF text extraction)...")
    # Generate a simple text PDF
    import pypdf
    from reportlab.pdfgen import canvas
    pdf_path = os.path.join(allowed_dir, f"test_pdf_{test_id}.pdf")
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, "Verification PDF Content - Page 1")
    c.showPage()
    c.drawString(100, 750, "Verification PDF Content - Page 2")
    c.save()
    
    doc_svc = DocumentService(db)
    with open(pdf_path, "rb") as f:
        doc = doc_svc.process_file(kb_id=kb.id, user_id=user.id, filename=f"test_pdf_{test_id}.pdf", file_obj=f)
        
    print(f"Document Status: {doc.processing_status}")
    chunks = doc.chunks
    print(f"Extracted Chunks: {len(chunks)}")
    for chunk in chunks:
        print(f" - Page {chunk.page_number}: {chunk.content.strip()}")
    if len(chunks) == 2 and chunks[0].page_number == 1 and chunks[1].page_number == 2:
        print("PASS: RAG Integration correctly extracted chunks and preserved page numbers.")
    else:
        print("FAIL: RAG Integration failed to preserve chunks or page numbers.")
        
    # 4. MULTIMODAL MODEL ROUTING
    print("\n[3] Verifying Multimodal Model Gateway Routing...")
    # Add dummy workers
    w_text = ModelWorker(name=f"T_{test_id}", ip_address="127.0.0.1", port=8001, status="available")
    w_mm = ModelWorker(name=f"M_{test_id}", ip_address="127.0.0.1", port=8002, status="available")
    db.add_all([w_text, w_mm])
    db.commit()
    db.refresh(w_text); db.refresh(w_mm)
    
    m_text = Model(worker_id=w_text.id, name="Text", model_identifier="text-llm", model_type="llm", modalities=["text"], capabilities=["chat"])
    m_mm = Model(worker_id=w_mm.id, name="Vision", model_identifier="vision-llm", model_type="llm", modalities=["text", "image", "vision"], capabilities=["chat", "multimodal"])
    db.add_all([m_text, m_mm])
    db.commit()
    
    gateway = ModelGatewayService(db)
    req = InferenceRequest(messages=[MessagePayload(role="user", content="Describe", images=["base64_foo"])], required_modalities=["image"])
    selected_model, _ = gateway.select_model_and_worker(req)
    if "image" in selected_model.modalities:
        print(f"PASS: Gateway successfully routed multimodal request to {selected_model.model_identifier}")
    else:
        print(f"FAIL: Gateway routed to wrong model: {selected_model.model_identifier}")
        
    # 5. SECURITY CONTROLS (DocumentProcessTool)
    print("\n[4] Verifying Security Controls (Path Traversal)...")
    import app.services.tools.document_process
    tool = ToolRegistry.get_tool("document_process", db=db, workspace_id=ws.id)
    res = tool.execute(filepath="../../../../../etc/passwd")
    if not res.success and "Security Policy Denied" in res.error:
        print(f"PASS: Security Policy prevented path traversal. Error: {res.error}")
    else:
        print("FAIL: Path traversal was not properly blocked!")
        
    # 6. AUDIT LOGS
    print("\n[5] Verifying Audit Logging...")
    from app.models.system_event import SystemEvent
    events = db.query(SystemEvent).filter(SystemEvent.event_type == "multimodal_processing").all()
    if len(events) > 0:
        print(f"PASS: Found {len(events)} multimodal_processing audit events.")
        for e in events:
            print(f" - {e.severity.upper()}: {e.message} (Metadata: {e.metadata_})")
    else:
        print("FAIL: No audit events were generated.")

    print("\n--- VERIFICATION COMPLETE ---")
    
if __name__ == "__main__":
    verify()
