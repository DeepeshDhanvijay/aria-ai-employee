# Project 1 Guide: AI Employee for Small Businesses

A build guide for an industry-level first project from your Top 10 list, built with Claude Code. Each later project from the list gets its own chat and reuses the foundation here.

## 1. What you are building

**"Aria"**: an AI operations employee for a small business (for example a dental clinic, salon, or home-services company). It reads inbound email and web chat, answers from the business's own knowledge, books appointments, drafts quotes, logs everything to a CRM, and hands off to a human when it is unsure.

**Why this one first:** it touches almost every building block on your list (agents, tool use, MCP servers, retrieval over documents, a dashboard, automation), so the later projects (document analyst, support agent, chat with your data) become reuse rather than new work.

**Definition of done (the bar for "industry level"):**

- Handles real inbound messages end to end with a human-approval step for risky actions
- Answers are grounded in uploaded business documents and cite them
- Has tests, an evaluation suite, logging, error handling, and CI
- Runs in Docker and is deployed at a public URL
- Has a README and architecture diagram a stranger could follow

## 2. Tool stack

| Layer | Tool | Role |
| --- | --- | --- |
| Builder | **Claude Code** | Writes, tests, and refactors the codebase with you |
| Brain | **Claude API** (tool use, structured outputs, prompt caching) | Reasoning, drafting, decisions |
| Agent loop | **Claude Agent SDK** (or a plain tool-use loop) | Runs multi-step tasks with tools |
| Integrations | **MCP servers**: Gmail, Google Calendar, plus one custom CRM MCP server you write | Gives the agent safe, standard access to business systems |
| Knowledge | **Postgres + pgvector** | Retrieval over business documents (RAG) |
| Backend | **FastAPI (Python)** or Node/TypeScript | API, webhooks, job workers |
| Queue | **Redis + a worker** | Async processing of messages |
| Frontend | **Next.js + Tailwind** | Admin dashboard: inbox, approvals, analytics |
| Auth | Clerk, Auth0, or Supabase Auth | Multi-tenant login |
| Quality | **pytest/Vitest, an eval harness, GitHub Actions** | Prevents regressions |
| Ops | **Docker, Sentry, structured logging** | Deploy and monitor |

Pick one backend language and stay with it. Python is the smoother path if you are new to agents.

## 3. Architecture

1. **Ingest**: Gmail MCP / chat widget webhook receives a message and puts it on the queue.
2. **Classify**: a cheap, fast Claude model labels it (question, booking, quote request, complaint, spam).
3. **Agent run**: a stronger Claude model works the task using tools: `search_knowledge`, `check_calendar`, `create_booking`, `draft_reply`, `update_crm`, `escalate_to_human`.
4. **Guardrails**: any action that spends money, sends external email, or changes a booking goes to an **approval queue** unless the business has enabled auto-send for that category.
5. **Dashboard**: the owner reviews, edits, approves, and sees metrics.
6. **Feedback loop**: edits and rejections are stored and become eval cases.

Design decision to make early: **multi-tenant from day one** (every table has a `business_id`). It is the difference between a demo and a product.

## 4. Set up Claude Code properly first (Day 1)

Most people skip this and get worse results.

1. **Create the repo** and commit an empty skeleton with `/backend`, `/frontend`, `/mcp-crm`, `/evals`, `/docs`.
2. **Write `CLAUDE.md`** at the root: project goal, stack, folder map, commands to run tests and lint, coding conventions, and rules such as "never commit secrets" and "every feature needs a test". Keep it under about 100 lines.
3. **Use plan mode** for every feature: ask Claude Code for a plan, review it, then let it implement.
4. **Add custom subagents** in `.claude/agents/`: a `reviewer` (code review against your conventions), a `test-writer`, and a `security-auditor`.
5. **Add custom slash commands** in `.claude/commands/` for repeated tasks, such as `/new-endpoint` and `/run-evals`.
6. **Add hooks**: auto-run formatter and tests after edits; block edits to `.env`.
7. **Connect MCP servers** via `.mcp.json` (Gmail, Calendar, GitHub, your database) so Claude Code itself can inspect the data and issues while building.
8. **Work in small commits** and ask Claude Code to explain any code you do not understand. You are building this yourself, so use it as a tutor as well as a coder.

## 5. Build phases

### Phase 1: Foundation (Days 1 to 3)

- Database schema: `businesses`, `users`, `documents`, `chunks`, `conversations`, `messages`, `actions`, `approvals`.
- Auth and tenant isolation.
- Docker Compose for Postgres, Redis, backend.
- CI pipeline running lint and tests on every push.

### Phase 2: Knowledge base / RAG (Days 4 to 7)

- Upload PDFs, FAQs, price lists; extract text; chunk (around 500 to 800 tokens with overlap).
- Embed and store in pgvector; add keyword search too (hybrid search).
- `search_knowledge` tool returns chunks with source and page.
- Require citations in answers; refuse when nothing relevant is found.

### Phase 3: The agent (Days 8 to 12)

- Implement the tool-use loop with a max-step limit and timeout.
- Use **structured outputs** (JSON schema) for classification and drafts.
- Use **prompt caching** for the long system prompt and business profile.
- Write the system prompt as a versioned file, not an inline string.

### Phase 4: Integrations via MCP (Days 13 to 17)

- Connect Gmail and Calendar MCP servers for reading mail, creating events, and checking availability.
- **Build your own MCP server** for a simple CRM (contacts, deals, notes). This is the standout portfolio piece: it shows you can extend an agent, not just call one.
- Handle auth, rate limits, and retries; log every tool call.

### Phase 5: Dashboard and approvals (Days 18 to 22)

- Inbox view, conversation view with agent reasoning summary, approve/edit/reject buttons.
- Settings: tone of voice, business hours, which actions are auto-approved.
- Analytics: response time, resolution rate, escalation rate, estimated hours saved.

### Phase 6: Evals, safety, and hardening (Days 23 to 27)

- **Eval suite**: 50 to 100 realistic test messages with expected outcomes (correct tool, correct facts, correct escalation). Run on every prompt or model change and track the score over time.
- **Prompt-injection defense**: treat email content as untrusted data; never let it change instructions or trigger actions without approval. Write tests that try it.
- **Privacy**: redact sensitive data in logs, add data-deletion endpoints, minimise stored personal data.
- **Failure handling**: dead-letter queue, retries with backoff, graceful fallback to "a human will reply soon".
- **Cost controls**: per-tenant token budgets, cheaper model for classification, caching.

### Phase 7: Deploy and polish (Days 28 to 30)

- Deploy backend (Fly.io, Railway, or AWS) and frontend (Vercel).
- Add Sentry, health checks, and structured logs.
- Write the README: problem, architecture diagram, setup steps, screenshots, eval results, limitations.
- Record a 2 to 3 minute demo video.

## 6. Prompts to give Claude Code at each stage

- "Read CLAUDE.md, then propose a plan for the Phase 2 ingestion pipeline. List files you will create and the tests you will write. Do not code yet."
- "Implement step 1 of the approved plan with tests, then run them."
- "Act as the security-auditor subagent: review this diff for injection, auth, and tenant-isolation issues."
- "Generate 30 adversarial eval cases for the booking flow, including ambiguous dates and angry customers."
- "Explain this module as if I will have to defend it in an interview."

## 7. Common mistakes to avoid

- Letting the agent send emails or change bookings with no approval step.
- Skipping evals and judging quality by a few manual tries.
- Putting everything in one giant prompt instead of tools plus retrieval.
- Building the dashboard before the agent works from the command line.
- Not tracking cost per conversation until the bill arrives.

## 8. Stretch goals

- Voice channel (phone answering) once text is solid.
- Multiple business templates (clinic, salon, trades).
- Weekly summary email to the owner.
- Reuse the RAG core for your next projects: the document analyst and "chat with your data".

## 9. Success checklist

- [ ] Multi-tenant database and auth working
- [ ] RAG answers cite sources and refuse when unsure
- [ ] Agent uses at least 5 tools, including your custom MCP server
- [ ] Approval queue protects risky actions
- [ ] Eval suite with a tracked score and prompt-injection tests
- [ ] CI, Docker, deployed URL, monitoring
- [ ] README, architecture diagram, demo video

After this, start your next project from the Top 10 list in a fresh chat, reusing the RAG and agent foundation.
