import logging

from fastapi import FastAPI, Header, HTTPException

from .agent import AgentService
from .knowledge import KnowledgeBase, KnowledgeChunk
from .models import Approval, ApprovalDecision, Business, ConversationCreate, KnowledgeDocument
from .store import Store

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
app = FastAPI(title="Aria AI Employee API", version="0.1.0")
store = Store()
knowledge = KnowledgeBase()
agent = AgentService(knowledge)
for document in store.list_documents():
    knowledge.add(KnowledgeChunk(business_id=document.business_id, title=document.title, content=document.content, page=document.page))


def require_business(x_business_id: str | None) -> str:
    if not x_business_id:
        raise HTTPException(status_code=400, detail="X-Business-ID header is required")
    if x_business_id not in store.businesses:
        raise HTTPException(status_code=404, detail="Business not found")
    return x_business_id


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/businesses", response_model=Business, status_code=201)
def create_business(business: Business) -> Business:
    if business.id in store.businesses:
        raise HTTPException(status_code=409, detail="Business already exists")
    store.businesses[business.id] = business
    return business


@app.post("/knowledge", response_model=KnowledgeDocument, status_code=201)
def add_knowledge(document: KnowledgeDocument, x_business_id: str | None = Header(default=None)) -> KnowledgeDocument:
    business_id = require_business(x_business_id)
    if document.business_id != business_id:
        raise HTTPException(status_code=403, detail="Document belongs to another business")
    store.documents.append(document)
    knowledge.add(KnowledgeChunk(business_id=document.business_id, title=document.title, content=document.content, page=document.page))
    return document


@app.post("/conversations/respond")
def respond(message: ConversationCreate, x_business_id: str | None = Header(default=None)) -> dict:
    business_id = require_business(x_business_id)
    reply = agent.respond(business_id, message.message)
    approval: Approval | None = None
    if reply.escalated:
        approval = store.create_approval(
            business_id,
            "human_review",
            {"customer_name": message.customer_name, "customer_email": message.customer_email, "message": message.message, "draft": reply.model_dump()},
        )
    return {"reply": reply, "approval": approval}


@app.get("/approvals", response_model=list[Approval])
def list_approvals(x_business_id: str | None = Header(default=None)) -> list[Approval]:
    business_id = require_business(x_business_id)
    return [approval for approval in store.approvals.values() if approval.business_id == business_id]


@app.post("/approvals/{approval_id}/decision", response_model=Approval)
def decide_approval(
    approval_id: str,
    decision: ApprovalDecision,
    x_business_id: str | None = Header(default=None),
) -> Approval:
    business_id = require_business(x_business_id)
    approval = store.approvals.get(approval_id)
    if approval is None or approval.business_id != business_id:
        raise HTTPException(status_code=404, detail="Approval not found")
    approval.status = decision.decision
    store.update_approval(approval)
    return approval
