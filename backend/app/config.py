import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./aria.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    crm_mcp_url: str = os.getenv("CRM_MCP_URL", "http://localhost:8001")


settings = Settings()
