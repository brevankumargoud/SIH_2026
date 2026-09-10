from __future__ import annotations
import uuid
from typing import TYPE_CHECKING, List
from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.database import Base

if TYPE_CHECKING:
    from .workspace import Workspace
    from .user import User
    from .conversation import Conversation
    from .agent_tool import AgentTool
    from .agent_knowledge_base import AgentKnowledgeBase
    from .agent_run import AgentRun

class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    configuration: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="agents")
    created_by_user: Mapped["User"] = relationship("User", back_populates="agents_created")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="agent")
    tools: Mapped[List["AgentTool"]] = relationship("AgentTool", back_populates="agent", cascade="all, delete-orphan")
    knowledge_bases: Mapped[List["AgentKnowledgeBase"]] = relationship("AgentKnowledgeBase", back_populates="agent", cascade="all, delete-orphan")
    runs: Mapped[List["AgentRun"]] = relationship("AgentRun", back_populates="agent", cascade="all, delete-orphan")
