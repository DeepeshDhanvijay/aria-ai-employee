# Architecture and delivery plan

The current MVP implements the Phase 1 safety and tenant boundaries plus the first retrieval path. Local API state is persisted in SQLite, while the Docker deployment points at PostgreSQL as the seam for the next repository layer and pgvector embeddings.

## Request flow

1. A channel adapter submits a message with a business tenant.
2. The agent searches only documents for that tenant.
3. A response includes citations when evidence exists.
4. Unknown or operationally risky requests create a pending approval.
5. The dashboard lists only approvals belonging to the active tenant.

## Current local MVP

- Businesses, knowledge documents, and approvals survive backend restarts in SQLite.
- Approval decisions use a typed request body and are persisted.
- The dashboard can load, approve, and reject pending approvals.
- `python evals/run.py` executes the four baseline safety and grounding cases.

## Next production steps

- Replace the development tenant header with authenticated user-to-business membership checks.
- Add PostgreSQL repositories and migrations, including pgvector embeddings and hybrid search.
- Add Gmail/Calendar adapters behind approval-aware tool interfaces.
- Replace the worker placeholder with Redis Streams or a durable queue and dead-letter handling.
- Add Sentry, PII-redacted structured logs, rate limits, and deletion endpoints.
- Expand the eval harness to 50–100 cases and run it in CI on prompt/model changes.
