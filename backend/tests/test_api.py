from fastapi.testclient import TestClient

from app.main import app, knowledge, store

client = TestClient(app)


def setup_function() -> None:
    store.businesses.clear()
    store.approvals.clear()
    store.documents.clear()
    knowledge._chunks.clear()


def test_tenant_header_is_required() -> None:
    response = client.get("/approvals")
    assert response.status_code == 400


def test_grounded_response_cites_document() -> None:
    client.post("/businesses", json={"id": "clinic", "name": "Clinic"})
    client.post(
        "/knowledge",
        headers={"X-Business-ID": "clinic"},
        json={"business_id": "clinic", "title": "Hours", "content": "We are open Monday at 9am.", "page": 1},
    )
    response = client.post(
        "/conversations/respond",
        headers={"X-Business-ID": "clinic"},
        json={"customer_name": "Sam", "message": "What are your hours?"},
    )
    assert response.status_code == 200
    assert response.json()["reply"]["citations"][0]["document"] == "Hours"


def test_unknown_request_escalates_and_is_tenant_scoped() -> None:
    client.post("/businesses", json={"id": "one", "name": "One"})
    response = client.post(
        "/conversations/respond",
        headers={"X-Business-ID": "one"},
        json={"customer_name": "Sam", "message": "Can you repair a spaceship?"},
    )
    approval = response.json()["approval"]
    assert approval["status"] == "pending"
    assert client.get("/approvals", headers={"X-Business-ID": "one"}).json()[0]["id"] == approval["id"]
    client.post("/businesses", json={"id": "two", "name": "Two"})
    assert client.get("/approvals", headers={"X-Business-ID": "two"}).json() == []


def test_approval_decision_is_typed_and_persisted() -> None:
    client.post("/businesses", json={"id": "clinic", "name": "Clinic"})
    response = client.post(
        "/conversations/respond",
        headers={"X-Business-ID": "clinic"},
        json={"customer_name": "Sam", "message": "Can you repair a spaceship?"},
    )
    approval_id = response.json()["approval"]["id"]
    decision = client.post(
        f"/approvals/{approval_id}/decision",
        headers={"X-Business-ID": "clinic"},
        json={"decision": "approved"},
    )
    assert decision.status_code == 200
    assert decision.json()["status"] == "approved"
    assert client.get("/approvals", headers={"X-Business-ID": "clinic"}).json()[0]["status"] == "approved"


def test_invalid_approval_decision_is_rejected() -> None:
    client.post("/businesses", json={"id": "clinic", "name": "Clinic"})
    approval_id = client.post(
        "/conversations/respond",
        headers={"X-Business-ID": "clinic"},
        json={"customer_name": "Sam", "message": "Can you repair a spaceship?"},
    ).json()["approval"]["id"]
    response = client.post(
        f"/approvals/{approval_id}/decision",
        headers={"X-Business-ID": "clinic"},
        json={"decision": "sent"},
    )
    assert response.status_code == 422
