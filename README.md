# Enterprise AI Knowledge Assistant 

A multi-tenant internal AI assistant for companies. Combines **RAG over
company documents**, a **structured employee/HR database**, a **deterministic
business-rule engine**, and **role-based access control** — not just a PDF
chatbot.

## Architecture

```
                              ┌─────────────────────────┐
                              │        Frontend         │
                              │  React + TS + Tailwind  │
                              │  Chat UI, Dashboards     │
                              └────────────┬────────────┘
                                           │ JWT
                              ┌────────────▼────────────┐
                              │      FastAPI Backend     │
                              │  Auth · RBAC · Tenancy   │
                              └──┬────────┬─────────┬────┘
                    ┌────────────┘        │         └────────────┐
          ┌─────────▼─────────┐ ┌─────────▼────────┐  ┌──────────▼─────────┐
          │  PostgreSQL (SQL)  │ │  pgvector (RAG)  │  │  Business Rules     │
          │  Company/Employee/ │ │  Document chunks │  │  Leave balance,     │
          │  Leave/Training    │ │  + embeddings     │  │  notice period,    │
          │  (tenant-scoped)   │ │  (tenant-scoped)   │  │  overlap checks    │
          └─────────────────────┘ └───────────────────┘  └─────────────────────┘
                                           │
                                  ┌────────▼────────┐
                                  │  LLM (GPT-5 or   │
                                  │  local, swappable)│
                                  └──────────────────┘
```

### Chat request lifecycle (`app/ai/chat_pipeline.py`)
1. **Authenticate** — JWT decoded, `CurrentUser` carries `company_id`, `role`, `department_id`.
2. **Scope** — every downstream call is filtered by `company_id`; this is the tenant-isolation boundary.
3. **Retrieve documents** — pgvector cosine-similarity search over `document_chunks`, hard-scoped to the tenant.
4. **Retrieve SQL context** — the asking user's own leave balances, org data, and (if Manager+) direct reports.
5. **Business rules** — if the question looks like a leave request, `app/ai/rules/leave_rules.py` computes balance/notice-period/overlap checks deterministically in Python — this is handed to the LLM as ground truth so it can't hallucinate a leave balance number.
6. **LLM reasoning** — role-aware system prompt + combined context sent to the LLM.
7. **Answer + citations** — response, source citations, and rule trace returned and persisted to conversation history.

### Multi-tenancy model
Every tenant-scoped table (`users`, `documents`, `document_chunks`,
`leave_balances`, `leave_requests`, `trainings`, `audit_logs`, ...) carries a
`company_id` column. **Every** query in `app/api/v1/*` and `app/ai/*` filters
on `company_id` taken from the JWT — never from a client-supplied parameter
(`assert_same_company` in `app/core/deps.py` guards this). For a stronger
isolation guarantee in production, add PostgreSQL Row-Level Security (RLS)
policies keyed on `company_id` as defense-in-depth on top of this.

### Roles (hierarchical: each includes the one below)
`Employee < Manager < HR < Admin` — enforced via `require_role()` in
`app/core/deps.py`. Modeled as a single `users.role` enum column rather than
separate tables, since permissions are strictly additive per the spec.

### Swappable AI backends
- **LLM**: `LLM_PROVIDER=openai` (GPT-5) or `LLM_PROVIDER=local` (any
  OpenAI-compatible endpoint — vLLM, Ollama, TGI). See `app/ai/llm.py`.
- **Embeddings**: `EMBEDDING_PROVIDER=local` (`BAAI/bge-small-en-v1.5` via
  sentence-transformers, on-prem friendly) or `openai`. See
  `app/ai/embeddings/embedder.py`.

Swap either without touching any retrieval, pipeline, or API code.

## Project structure

```
enterprise-ai-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entrypoint
│   │   ├── core/                   # config, security (JWT/bcrypt), RBAC deps
│   │   ├── db/                     # SQLAlchemy engine/session, seed script
│   │   ├── models/                 # Company, User, Leave, Document, Training...
│   │   ├── schemas/                 # Pydantic request/response models
│   │   ├── api/v1/                 # auth, employees, departments, leave,
│   │   │                           # documents, chat, analytics routers
│   │   ├── services/                # document_service (extract/chunk/embed)
│   │   └── ai/
│   │       ├── embeddings/         # swappable embedder
│   │       ├── retrieval/          # pgvector search + SQL context
│   │       ├── rules/              # leave business-rule engine
│   │       ├── prompts/            # role-aware prompt templates
│   │       ├── llm.py              # swappable LLM client
│   │       └── chat_pipeline.py    # orchestrates the full RAG+rules flow
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/                  # Landing, Login, Register, Chat,
│   │   │                           # Dashboard, Team, PolicyUpload, Analytics
│   │   ├── components/             # Sidebar, ChatMessage, AppLayout, guards
│   │   ├── context/AuthContext.tsx
│   │   └── lib/api.ts              # axios client + JWT interceptor
│   └── Dockerfile
└── docker-compose.yml
```

## Running locally

### Option A — Docker Compose (recommended)
```bash
cp backend/.env.example backend/.env
# edit backend/.env and set OPENAI_API_KEY (or switch LLM_PROVIDER=local)

docker compose up --build
```
This starts Postgres+pgvector, runs the seed script (creates two demo
tenants), the backend on `:8000`, and the frontend on `:5173`.

Demo logins (password `Password123!`):
- Tenant `acme`: `admin@acme.com`, `hr@acme.com`, `manager@acme.com`, `john@acme.com`
- Tenant `globex`: same pattern, isolated data — log in as `john@acme.com` and
  confirm you cannot see anything from `globex`.

### Option B — Manual
```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY, DATABASE_URL
python -m app.db.init_db      # creates pgvector extension, tables, seed data
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev   # http://localhost:5173, proxies /api to :8000
```

Postgres must have the `vector` extension available (the `pgvector/pgvector`
Docker image ships with it; for a manual Postgres install, run
`CREATE EXTENSION vector;` as a superuser once).

## Environment variables
See `backend/.env.example` for the full list: database URL, JWT secret,
LLM/embedding provider selection and credentials, upload limits, CORS
origins.

## Extending this to full production scale
This scaffold is wired end-to-end and runnable, but a few things are
simplified for clarity and should be hardened before real production use:
- **Background jobs**: document processing runs via FastAPI `BackgroundTasks`;
  swap for Celery/RQ + Redis so uploads don't block and can retry on failure.
- **Alembic migrations**: currently `Base.metadata.create_all` in the seed
  script; add proper Alembic migrations for schema evolution.
- **Row-Level Security**: add Postgres RLS policies on `company_id` as a
  second, database-enforced layer of tenant isolation.
- **Rate limiting & audit logging**: `audit_logs` table exists; wire up
  middleware to actually populate it on sensitive actions.
- **Streaming responses**: `LLMClient.stream_chat` exists but the `/chat`
  endpoint currently returns a single response; wire it to a
  `StreamingResponse`/SSE endpoint and consume it with `EventSource` on the
  frontend for a token-by-token typing effect.
- **Policy-driven business rules**: `NOTICE_REQUIREMENTS` in
  `leave_rules.py` is hardcoded; load it per-company from a `Policy` config
  table instead.
- **NL date parsing**: leave-intent date extraction in `chat_pipeline.py` is
  a lightweight heuristic; swap in `dateparser` or a proper NLU date parser.
