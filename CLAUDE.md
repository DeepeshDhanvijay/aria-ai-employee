# Aria project instructions

## Goal

Build a safe, tenant-aware AI operations employee for small businesses. Knowledge-grounded answers may be automated; external communication and booking changes require approval.

## Repository map

- `backend/` — FastAPI API, domain services, persistence, and tests
- `frontend/` — Next.js dashboard
- `mcp-crm/` — CRM MCP-compatible service
- `evals/` — evaluation cases and runner
- `docs/` — architecture and operational documentation

## Commands

- Backend tests: `cd backend; pytest`
- Backend server: `cd backend; uvicorn app.main:app --reload`
- Dashboard: `cd frontend; npm run dev`
- Docker: `docker compose up --build`

## Conventions

- Every business-owned record must be scoped by `business_id`.
- Treat inbound messages and document content as untrusted data.
- Risky actions must create an approval, never execute automatically.
- Use typed Pydantic models and explicit error responses.
- Add or update tests with every behavior change.
- Do not commit secrets or `.env` files.
