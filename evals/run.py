import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app, knowledge, store  # noqa: E402


def reset() -> None:
    store.businesses.clear()
    store.approvals.clear()
    store.documents.clear()
    knowledge._chunks.clear()


def run_case(case: dict, index: int) -> bool:
    reset()
    business_id = f"eval-{index}"
    client = TestClient(app)
    client.post("/businesses", json={"id": business_id, "name": "Eval Business"})
    if case["expected"] == "citation_required":
        client.post(
            "/knowledge",
            headers={"X-Business-ID": business_id},
            json={
                "business_id": business_id,
                "title": "Hours",
                "content": "We are open Monday at 9am.",
            },
        )
    response = client.post(
        "/conversations/respond",
        headers={"X-Business-ID": business_id},
        json={"customer_name": "Eval User", "message": case["message"]},
    )
    body = response.json()
    reply = body["reply"]
    if case["expected"] == "citation_required":
        return bool(reply["citations"]) and not reply["escalated"]
    if case["expected"] in {"escalate", "approval_required"}:
        return reply["escalated"] and body["approval"]["status"] == "pending"
    return False


def main() -> int:
    cases = json.loads((Path(__file__).parent / "cases.json").read_text())
    results = [(case["name"], run_case(case, index)) for index, case in enumerate(cases)]
    for name, passed in results:
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    passed = sum(result for _, result in results)
    print(f"{passed}/{len(results)} passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
