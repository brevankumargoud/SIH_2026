from __future__ import annotations
import uuid
from typing import TYPE_CHECKING, List
from datetime import datetime, timezone
from sqlalchemy import String, Integer, BigInteger, Boolean, DateTime, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from app.db.database import Base

if TYPE_CHECKING:
    from .model import Model
    from .model_inference_run import ModelInferenceRun

class ModelWorker(Base):
    __tablename__ = "model_workers"
    __table_args__ = (
        CheckConstraint("port > 0 AND port <= 65535", name="check_worker_port_range"),
        CheckConstraint("status IN ('offline', 'starting', 'available', 'busy', 'error')", name="check_worker_status"),
        Index("ix_model_workers_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str] = mapped_column(INET, nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    protocol: Mapped[str] = mapped_column(String(20), default="http", nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    hardware_info: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    available_vram_mb: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    last_heartbeat: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    models: Mapped[List["Model"]] = relationship("Model", back_populates="worker", cascade="all, delete-orphan")
    inference_runs: Mapped[List["ModelInferenceRun"]] = relationship("ModelInferenceRun", back_populates="worker", cascade="all, delete-orphan")
