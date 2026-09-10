from __future__ import annotations
import uuid
from typing import TYPE_CHECKING, List
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.database import Base

if TYPE_CHECKING:
    from .model_worker import ModelWorker
    from .message import Message
    from .model_inference_run import ModelInferenceRun
    from .knowledge_base import KnowledgeBase

class Model(Base):
    __tablename__ = "models"
    __table_args__ = (
        CheckConstraint("context_length > 0", name="check_models_context_length_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model_workers.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    model_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    modalities: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    capabilities: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    context_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    worker: Mapped["ModelWorker"] = relationship("ModelWorker", back_populates="models")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="model")
    inference_runs: Mapped[List["ModelInferenceRun"]] = relationship("ModelInferenceRun", back_populates="model", cascade="all, delete-orphan")
    knowledge_bases: Mapped[List["KnowledgeBase"]] = relationship("KnowledgeBase", back_populates="embedding_model")
