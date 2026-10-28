from uuid import uuid4

from .models import Approval, Business, KnowledgeDocument


class Store:
    def __init__(self) -> None:
        self.businesses: dict[str, Business] = {}
        self.approvals: dict[str, Approval] = {}
        self.documents: list[KnowledgeDocument] = []

    def get_business(self, business_id: str) -> Business:
        business = self.businesses.get(business_id)
        if business is None:
            raise KeyError(business_id)
        return business

    def create_approval(self, business_id: str, action_type: str, payload: dict) -> Approval:
        approval = Approval(id=str(uuid4()), business_id=business_id, action_type=action_type, payload=payload)
        self.approvals[approval.id] = approval
        return approval
