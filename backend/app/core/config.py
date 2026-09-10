from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    PROJECT_NAME: str = "Sovereign On-Premise Agentic AI Workbench"
    SERVICE_NAME: str = "sovereign-ai-workbench"
    API_V1_STR: str = "/api/v1"

    # Core settings required by project specification
    DATABASE_URL: str = "postgresql+psycopg://postgres:password@localhost:5432/sih_2026"
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = True


settings = Settings()
