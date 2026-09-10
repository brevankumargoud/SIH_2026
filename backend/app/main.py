from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.endpoints import workers
from app.api.endpoints import models
from app.api.endpoints import conversations
from app.api.endpoints import knowledge_bases
from app.api.endpoints import documents
from app.api.endpoints import agents
from app.api.endpoints import security
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Clean startup and shutdown lifecycle management."""
    logger.info("Starting up %s (Environment: %s)", settings.PROJECT_NAME, settings.ENVIRONMENT)
    yield
    logger.info("Shutting down %s", settings.PROJECT_NAME)


# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Backend API foundation for the Sovereign On-Premise Agentic AI Workbench. "
        "Built for Smart India Hackathon 2026."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS) for local frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.endpoints import auth
from app.api.endpoints import artifacts

# Register routers
from app.api.endpoints import workspaces

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(workspaces.router)
app.include_router(artifacts.router)
app.include_router(health_router)
app.include_router(workers.router)
app.include_router(models.router)
app.include_router(conversations.router)
app.include_router(knowledge_bases.router)
app.include_router(documents.router)
app.include_router(agents.router)
app.include_router(security.router)


@app.get("/", tags=["Root"], include_in_schema=False)
def root():
    """Root entrypoint providing basic service metadata."""
    return {
        "service": settings.SERVICE_NAME,
        "name": settings.PROJECT_NAME,
        "docs": "/docs",
        "health": "/health",
    }
