# Sponsorship Tracker

A collaborative web app for a student club to track sponsorship and partnership
outreach. See [PROJECT_SPEC.md](PROJECT_SPEC.md) for the full product spec.

**Status: project skeleton.** Infrastructure, tooling, and a health endpoint
only — no product features yet.

## Layout

```
backend/     FastAPI + SQLAlchemy 2.0 (async) + Alembic
  app/api        HTTP routes
  app/models     SQLAlchemy models (Base only, for now)
  app/schemas    Pydantic schemas
  app/services   business logic
  app/ws         WebSocket handlers
  app/mcp        MCP server
  alembic/       migrations (async env)
  tests/         pytest
frontend/    Vite + React + TypeScript + Tailwind
  src/api        HTTP client, TanStack Query client
  src/components shared UI
  src/features   feature modules
  src/hooks      shared hooks
  src/pages      route components
docker-compose.yml   Postgres 16
```

## Prerequisites

- Docker (for Postgres)
- Python 3.12
- Node.js 20+

## 1. Database

```bash
docker compose up -d          # Postgres 16 on localhost:5432, named volume sponsor_tracker_pgdata
docker compose ps             # wait until the db service is "healthy"
```

Defaults: user `sponsor`, password `sponsor`, database `sponsor_tracker`. Override
with `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT` in the
environment or a root `.env`.

The test database (`sponsor_tracker_test`) is created automatically by the test
suite; you do not need to create it by hand.

```bash
docker compose down           # stop
docker compose down -v        # stop and delete the data volume
```

## 2. Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt    # or requirements.txt for runtime only
cp .env.example .env

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health → `{"status":"ok","database":"ok"}`
  (HTTP 503 with `"database":"error"` when Postgres is unreachable)

Migrations:

```bash
alembic revision --autogenerate -m "add workspaces"   # after adding models
alembic upgrade head
alembic downgrade -1
```

The Alembic environment reads `DATABASE_URL` from settings, so `alembic.ini`
holds no credentials.

Tests, lint, format:

```bash
pytest                # drops/recreates the test DB, migrates, runs tests
ruff check . --fix
black .
```

## 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

- App: http://localhost:5173
- Routes: `/login`, `/workspaces`, `/w/:workspaceId` (`/` redirects to `/workspaces`)

```bash
npm run build          # type-check + production build
npm run lint
npm run format
```

## Configuration

Both apps read configuration from the environment; see `backend/.env.example`
and `frontend/.env.example`.

The two origins must agree: the frontend sends every request with
`credentials: 'include'` (session cookies), so the backend's `CORS_ORIGINS` must
list the exact frontend origin. `*` is not usable with credentials.

| Backend            |                                                      |
| ------------------ | ---------------------------------------------------- |
| `DATABASE_URL`     | async URL, must use the `postgresql+asyncpg://` driver |
| `TEST_DATABASE_URL`| test DB; defaults to `DATABASE_URL` + `_test`        |
| `CORS_ORIGINS`     | JSON list or comma-separated exact origins           |
| `SESSION_SECRET`   | session cookie signing key (used once auth lands)    |
| `DB_ECHO`          | log SQL                                              |

| Frontend            |                          |
| ------------------- | ------------------------ |
| `VITE_API_BASE_URL` | backend origin           |

## Testing notes

`pytest` drops and recreates the test database once per session, runs Alembic to
head, and then wraps **each test in a transaction that is rolled back**
afterwards. The app's own `commit()` calls run against a savepoint
(`join_transaction_mode="create_savepoint"`), so they are undone too and tests
never see each other's data.

Use the `client` fixture for HTTP tests and `db_session` for direct database
access; `client` already overrides the app's session dependency to share the
test transaction.
