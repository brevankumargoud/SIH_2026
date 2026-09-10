import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.schemas.agent import ToolResult
from app.services.tools.base import BaseTool
from app.services.tools.registry import ToolRegistry
from app.services.retrieval_service import RetrievalService
from app.models.agent_knowledge_base import AgentKnowledgeBase
from sqlalchemy import select

@ToolRegistry.register("knowledge_search")
class KnowledgeSearchTool(BaseTool):
    def __init__(self, db: Session, agent_id: uuid.UUID):
        self.db = db
        self.agent_id = agent_id

    @property
    def name(self) -> str:
        return "Knowledge Search"

    @property
    def description(self) -> str:
        return "Search local approved knowledge bases for context. Input is a search query."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."}
            },
            "required": ["query"]
        }

    def execute(self, query: str, **kwargs) -> ToolResult:
        if not query:
            return ToolResult(success=False, output=None, error="Query is required")

        # Check which KBs the agent has access to
        stmt = select(AgentKnowledgeBase).where(AgentKnowledgeBase.agent_id == self.agent_id)
        agent_kbs = self.db.execute(stmt).scalars().all()
        
        if not agent_kbs:
            return ToolResult(success=False, output="No knowledge bases available for this agent.", metadata={})

        retrieval_svc = RetrievalService(self.db)
        all_results = []
        for akb in agent_kbs:
            results = retrieval_svc.search(akb.knowledge_base_id, query, top_k=3, threshold=0.3)
            all_results.extend(results)

        all_results.sort(key=lambda x: x.score, reverse=True)
        top_results = all_results[:5]

        if not top_results:
            return ToolResult(success=True, output="No relevant findings in knowledge bases.", metadata={})

        context_str = "\n\n".join([f"[Document: {r.filename}, page {r.page_number}]\n{r.content}" for r in top_results])
        return ToolResult(success=True, output=context_str, metadata={"num_results": len(top_results)})
