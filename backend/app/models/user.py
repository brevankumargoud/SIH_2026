from __future__ import annotations
import uuid
from typing import TYPE_CHECKING, List
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base

if TYPE_CHECKING:
    from .user_role import UserRole
    from .workspace import Workspace
    from .workspace_member import WorkspaceMember
    from .agent import Agent
    from .conversation import Conversation
    from .document import Document
    from .agent_run import AgentRun
    from .audit_log import AuditLog
    from .knowledge_base import KnowledgeBase

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    roles: Mapped[List["UserRole"]] = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    workspaces_created: Mapped[List["Workspace"]] = relationship("Workspace", back_populates="created_by_user", cascade="all, delete-orphan")
    workspaces_joined: Mapped[List["WorkspaceMember"]] = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")
    agents_created: Mapped[List["Agent"]] = relationship("Agent", back_populates="created_by_user")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="user")
    documents_uploaded: Mapped[List["Document"]] = relationship("Document", back_populates="uploaded_by_user")
    agent_runs: Mapped[List["AgentRun"]] = relationship("AgentRun", back_populates="user")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")
    knowledge_bases_created: Mapped[List["KnowledgeBase"]] = relationship("KnowledgeBase", back_populates="created_by_user")
