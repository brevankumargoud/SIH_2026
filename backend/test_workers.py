import uuid
import sys
from sqlalchemy import select
from app.db.database import SessionLocal
from app.models.model_worker import ModelWorker
from app.models.model import Model

db = SessionLocal()
workers = db.execute(select(ModelWorker)).scalars().all()
models = db.execute(select(Model)).scalars().all()

print(f"Workers: {[(w.id, w.status) for w in workers]}")
print(f"Models: {[(m.id, m.is_active) for m in models]}")
