from app.db.database import SessionLocal
from app.models.model_worker import ModelWorker
from app.models.model import Model
import uuid

db = SessionLocal()

# Check if already exists
existing = db.query(ModelWorker).filter(ModelWorker.ip_address == "10.151.15.9", ModelWorker.port == 11434).first()
if existing:
    print("Worker already exists.")
else:
    worker = ModelWorker(
        id=uuid.uuid4(),
        name="Laptop-1-Ollama",
        hostname="laptop-1",
        ip_address="10.151.15.9",
        port=11434,
        protocol="http",
        status="available",
        hardware_info={"type": "ollama"},
        is_active=True
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    
    model = Model(
        id=uuid.uuid4(),
        worker_id=worker.id,
        name="Llama 3.2 1B",
        model_identifier="llama3.2:1b",
        model_type="LLM",
        modalities=["text"],
        capabilities=["chat"],
        context_length=131072,
        is_active=True
    )
    db.add(model)
    db.commit()
    print("Registered Laptop-1 Ollama Worker and Model successfully.")
