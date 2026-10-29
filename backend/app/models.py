from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Business(BaseModel):
    id: str
    name: str
    timezone: str = "UTC"
    auto_approve_categories: list[str] = Field(default_factory=list)


class ConversationCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=200)
    customer_email: Optional[str] = Field(default=None, max_length=320)
    message: str = Field(min_length=1, max_length=10000)


class Citation(BaseModel):
    document: str
    page: Optional[int] = None
    excerpt: str


class AgentReply(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    classification: str
    confidence: float = Field(ge=0, le=1)
    escalated: bool = False


class Approval(BaseModel):
    id: str
    business_id: str
    action_type: str
    payload: dict
    status: str = "pending"
    created_at: datetime = Field(default_factory=utc_now)


class ApprovalDecision(BaseModel):
    decision: str = Field(pattern="^(approved|rejected)$")


class KnowledgeDocument(BaseModel):
    business_id: str
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1, max_length=200000)
    page: Optional[int] = None
