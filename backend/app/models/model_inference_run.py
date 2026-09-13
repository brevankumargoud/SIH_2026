from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.database import Base

if TYPE_CHECKING:
    from .agent_run import AgentRun
    from .model import Model
    from .model_worker import ModelWorker

class ModelInferenceRun(Base):
    __tablename__ = "model_inference_runs"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'running', 'completed', 'failed', 'cancelled')", name="check_inference_run_status"),
        CheckConstraint("input_tokens >= 0", name="check_inference_runs_input_tokens_positive"),
        CheckConstraint("output_tokens >= 0", name="check_inference_runs_output_tokens_positive"),
        CheckConstraint("latency_ms >= 0", name="check_inference_runs_latency_ms_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=True, index=True)
    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"), nullable=False, index=True)
    worker_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model_workers.id", ondelete="CASCADE"), nullable=False, index=True)
    request_data: Mapped[dict] = mapped_column("request", JSONB, default=dict, nullable=False)
    response_data: Mapped[dict | None] = mapped_column("response", JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    agent_run: Mapped["AgentRun"] = relationship("AgentRun", back_populates="inference_runs")
    model: Mapped["Model"] = relationship("Model", back_populates="inference_runs")
    worker: Mapped["ModelWorker"] = relationship("ModelWorker", back_populates="inference_runs")
