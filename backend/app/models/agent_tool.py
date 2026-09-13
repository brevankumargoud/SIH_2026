from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.database import Base

if TYPE_CHECKING:
    from .agent import Agent
    from .tool import Tool

class AgentTool(Base):
    __tablename__ = "agent_tools"
    __table_args__ = (
        Index("ix_agent_tools_tool_id", "tool_id"),
    )

    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    tool_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tools.id", ondelete="CASCADE"), primary_key=True)
    configuration: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="tools")
    tool: Mapped["Tool"] = relationship("Tool", back_populates="agents")
