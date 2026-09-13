from __future__ import annotations
import uuid
from typing import TYPE_CHECKING, List
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.database import Base

if TYPE_CHECKING:
    from .agent import Agent
    from .conversation import Conversation
    from .user import User
    from .tool_execution import ToolExecution
    from .model_inference_run import ModelInferenceRun
    from .artifact import Artifact

class AgentRun(Base):
    __tablename__ = "agent_runs"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'running', 'completed', 'failed', 'cancelled')", name="check_agent_run_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    input_data: Mapped[dict] = mapped_column("input", JSONB, default=dict, nullable=False)
    output_data: Mapped[dict | None] = mapped_column("output", JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="runs")
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="agent_runs")
    user: Mapped["User"] = relationship("User", back_populates="agent_runs")
    tool_executions: Mapped[List["ToolExecution"]] = relationship("ToolExecution", back_populates="agent_run", cascade="all, delete-orphan")
    inference_runs: Mapped[List["ModelInferenceRun"]] = relationship("ModelInferenceRun", back_populates="agent_run", cascade="all, delete-orphan")
    artifacts: Mapped[List["Artifact"]] = relationship("Artifact", back_populates="agent_run", cascade="all, delete-orphan")
