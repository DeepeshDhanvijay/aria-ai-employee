from .knowledge import KnowledgeBase
from .models import AgentReply


class AgentService:
    def __init__(self, knowledge: KnowledgeBase) -> None:
        self.knowledge = knowledge

    def respond(self, business_id: str, message: str) -> AgentReply:
        results = self.knowledge.search(business_id, message)
        lower = message.lower()
        if not results:
            return AgentReply(
                answer="I don't have enough information to answer that confidently. A human will reply soon.",
                classification="needs_human",
                confidence=0.0,
                escalated=True,
            )
        if any(word in lower for word in ("book", "schedule", "appointment", "quote", "price")):
            classification = "booking_or_quote"
        elif any(word in lower for word in ("angry", "complaint", "refund", "urgent")):
            classification = "complaint"
        else:
            classification = "question"
        citations = self.knowledge.citations(results)
        answer = f"Based on {citations[0].document}: {citations[0].excerpt}"
        return AgentReply(
            answer=answer,
            citations=citations,
            classification=classification,
            confidence=min(0.95, results[0][1]),
            escalated=classification != "question",
        )
