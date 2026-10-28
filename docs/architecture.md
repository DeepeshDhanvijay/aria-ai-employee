# Architecture and delivery plan

The current scaffold implements the Phase 1 safety and tenant boundaries plus the first retrieval path. The in-memory store keeps local startup simple; the Docker deployment points the backend at PostgreSQL and is the seam for SQLAlchemy migrations and pgvector embeddings.

## Request flow

1. A channel adapter submits a message with a business tenant.
2. The agent searches only documents for that tenant.
3. A response includes citations when evidence exists.
4. Unknown or operationally risky requests create a pending approval.
5. The dashboard lists only approvals belonging to the active tenant.

## Next production steps

- Replace the development tenant header with authenticated user-to-business membership checks.
- Add PostgreSQL repositories and migrations, including pgvector embeddings and hybrid search.
- Add Gmail/Calendar adapters behind approval-aware tool interfaces.
- Replace the worker placeholder with Redis Streams or a durable queue and dead-letter handling.
- Add Sentry, PII-redacted structured logs, rate limits, and deletion endpoints.
- Expand the eval harness to 50–100 cases and run it in CI on prompt/model changes.
