# /new-endpoint

Create a new FastAPI endpoint with the following rules:

1. Add a typed Pydantic request model if relevant.
2. Enforce `X-Business-ID` access checks.
3. Return explicit 4xx errors instead of silent failures.
4. Add or update tests for the endpoint.
5. Keep the change minimal and tenant-aware.
