from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Aria CRM MCP Server", version="0.1.0")
contacts: dict[str, dict] = {}
notes: list[dict] = []


class Contact(BaseModel):
    business_id: str
    name: str = Field(min_length=1)
    email: str | None = None


class Note(BaseModel):
    business_id: str
    contact_id: str
    body: str = Field(min_length=1)


def require_business(header: str | None, body_business_id: str) -> None:
    if not header:
        raise HTTPException(status_code=400, detail="X-Business-ID header is required")
    if header != body_business_id:
        raise HTTPException(status_code=403, detail="Business mismatch")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/tools/contacts")
def create_contact(contact: Contact, x_business_id: str | None = Header(default=None)) -> dict:
    require_business(x_business_id, contact.business_id)
    contact_id = str(uuid4())
    contacts[contact_id] = {"id": contact_id, **contact.model_dump()}
    return contacts[contact_id]


@app.post("/tools/notes")
def create_note(note: Note, x_business_id: str | None = Header(default=None)) -> dict:
    require_business(x_business_id, note.business_id)
    contact = contacts.get(note.contact_id)
    if contact is None or contact["business_id"] != note.business_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    item = {"id": str(uuid4()), **note.model_dump()}
    notes.append(item)
    return item
