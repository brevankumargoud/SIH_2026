from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base

if TYPE_CHECKING:
    from .agent import Agent
    from .knowledge_base import KnowledgeBase

class AgentKnowledgeBase(Base):
    __tablename__ = "agent_knowledge_bases"
    __table_args__ = (
        Index("ix_agent_knowledge_bases_knowledge_base_id", "knowledge_base_id"),
    )

    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), primary_key=True)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="knowledge_bases")
    knowledge_base: Mapped["KnowledgeBase"] = relationship("KnowledgeBase", back_populates="agents")
