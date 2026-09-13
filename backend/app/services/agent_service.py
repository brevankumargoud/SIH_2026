import uuid
from sqlalchemy.orm import Session
from app.models.agent_run import AgentRun
from app.schemas.agent import AgentRunCreate
from app.services.agent_orchestrator import AgentOrchestrator

class AgentService:
    def __init__(self, db: Session):
        self.db = db

    def execute_agent(self, agent_id: uuid.UUID, request: AgentRunCreate) -> AgentRun:
        # Create run record
        run = AgentRun(
            agent_id=agent_id,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            status="pending",
            input_data=request.input_data
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        # Run orchestrator
        orchestrator = AgentOrchestrator(self.db, agent_id)
        return orchestrator.execute(
            run_id=run.id,
            input_data=request.input_data,
            max_iterations=request.max_iterations,
            preferred_model=request.preferred_model
        )
