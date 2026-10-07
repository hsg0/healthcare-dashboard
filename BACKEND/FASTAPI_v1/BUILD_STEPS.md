# Build steps

WHAT — A running list of the backend steps for this healthcare dashboard.

WHY — So the next step is obvious, and finished work is not repeated.

HOW — Update this file at the end of each step. Change that step from "not started" to "done", and write what actually happened.

IMPORTANT — This file is notes only. It does not start the server or touch the database. Do not put passwords, tokens, or real patient data here.

Child-readable code, adult-level production safety.

## Done

### Step 1 — Coding rules

Done.

The rules live in `.cursor/rules/coding-rules.mdc` at the project root. They apply to every session.

- Backend packages and commands use uv only.
- Frontend packages and commands use npm only.
- Patient and note data will live in PostgreSQL.
- This app has no login.
- The patient summary will be a plain template, not an AI diagnosis.
- Every important application file starts with WHAT, WHY, HOW, and IMPORTANT.

### Step 2 — uv init

Done. Folder is now `BACKEND/FASTAPI_v1`. Python on this Mac is `python3` 3.14.8. The `python` command is not installed. uv used that 3.14 interpreter.

`uv init` named the project `fastapi` because the folder was named FASTAPI. `uv add fastapi` then failed: a project cannot depend on a package with the same name.

Fix:

- Project name in `pyproject.toml` is `FASTAPI_v1`, the same as this folder. That name is not the `fastapi` package, so `uv add` can install FastAPI.
- Removed the generated `fastapi` script and the `src/fastapi` stub. Those would have hidden the real FastAPI command.
- Set `package = false` so uv treats this as an app, not a library.

Packages now in `pyproject.toml`:

- `fastapi[standard]>=0.142.2`
- `sqlalchemy[asyncio]>=2.1.3`
- `asyncpg>=0.32.0`
- `pydantic-settings>=2.15.0`
- `email-validator>=2.3.0`

### Step 3 — Health check and folder setup

Done. The backend now matches the folder shape from the Dr. Pharma API, without the pieces this app does not need.

```
FASTAPI_v1/
  main.py
  config/
  controllers/
  models/
  routes/
```

`main.py` is the file we run. `GET /health` returns `{"status": "ok"}`.

```bash
cd BACKEND/FASTAPI_v1
uv run python main.py
```

Then open `http://127.0.0.1:4020/health`.

`limiter/` and `middleware/` are not here. Those folders in the other project are for rate limits and login. This dashboard has neither.

The old `src/fastapi` folder was removed again. A local folder named `fastapi` would hide the real FastAPI library.

## Next

### Step 4 — Supabase Postgres

Connection file is in place. Tables and seed data are not.

`config/database.py` reads `.env` and opens an async SQLAlchemy session to Supabase. `main.py` runs `SELECT 1` on startup. If that fails, the server stops.

Copy `.env.example` to `.env` and fill in the pooler settings from the Supabase dashboard (Project Settings → Database). Do not commit `.env`.

Still to do: patient and note tables in `models/`, create them on startup, and seed 20 fictional patients.

## Later

These stay "not started" until we reach them. Add notes under each one when we do the work.

### Step 5 — Patient routes

Not started.

Add list, get, create, update, and delete. Validate every input with Pydantic. Use 201, 204, 404, and 422.

### Step 6 — Notes and summary

Not started.

Add create, list, and delete for notes. Add `GET /patients/{id}/summary` as a chart summary template.

### Step 7 — Frontend

Not started.

Create the Vite React app in `FRONTEND/VITE` with npm. Then build the layout, list, detail, form, and 404 page.

### Step 8 — Docker and README

Not started.

Add Dockerfiles, `docker-compose.yml`, `.env.example`, and `README.md` so another person can run the whole app.
