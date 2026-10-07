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

### Step 4 — Supabase Postgres and patient seed

Done for patients. Notes are still later.

`config/database.py` connects to Supabase. On startup, `main.py` creates the `patients` table and, when it is empty, inserts 20 fictional patients from `models/patient.py`. A later restart does not insert them again.

The log line to look for is `Seeded 20 fictional patients`. If the rows were already there, the log says the seed was skipped.

### Step 5 — Patient routes

Done. All five live in `routes/patients.py`, and `main.py` only attaches the router.

| Method and URL | Answers |
| --- | --- |
| `GET /patients` | A page of patients. Accepts `page`, `page_size`, `search`, `status`, `sort_by`, `sort_dir`. |
| `GET /patients/{patient_id}` | One patient, or 404. |
| `POST /patients` | 201 with the saved patient, or 422. |
| `PUT /patients/{patient_id}` | The updated patient, or 404. |
| `DELETE /patients/{patient_id}` | 204 with no body, or 404. |

Notes from building it:

- Age is never stored. `calculate_age_in_years` works it out from `date_of_birth`, so the browser cannot send a wrong age.
- Sorting by age flips the date order, because an older patient has an earlier date of birth.
- `sort_by`, `sort_dir`, `status`, and `blood_type` are fixed lists. Anything else is a 422 before the query runs.
- A birth date or a last visit in the future is rejected.
- `database_session` used to log a stack trace for every 404 and 422. It now logs only real `SQLAlchemyError` failures, so the log shows database problems instead of normal rejected input.

Checked against the live Supabase data: the list returned all 20, a name search narrowed it to 1, the status filter returned the 4 critical patients, a created patient came back as 201 and was then deleted with 204, and the table was back to 20 rows afterwards.

### Step 6 — Frontend routes, sidebar, and patient screens

Done. Two screens were added with one new file, `FRONTEND/VITE/dashboard/src/PatientList.jsx`.

- `App.jsx` now holds the addresses: `/` is the dashboard, `/patients` is the list, `/patients/:patientId` is one patient, and anything else shows "Page not found".
- The nav moved into a collapsible sidebar. The button in the top bar collapses it to symbols only. A screen narrower than 980px collapses it on its own.
- The list reads `GET /patients` with search, status, sort, and page buttons. Typing waits 300ms so one name does not send one request per key.
- Loading, empty, and network-error states are all shown. During an error the table, the page buttons, and the total count are hidden, so a failed request never looks like a result.
- The detail screen shows "Patient not available" for a missing id and for an id that is not a number.

## Later

These stay "not started" until we reach them. Add notes under each one when we do the work.

### Step 7 — Notes and summary

Not started.

Add create, list, and delete for notes. Add `GET /patients/{id}/summary` as a chart summary template.

### Step 8 — Add and edit patient form

Not started.

The API already accepts `POST` and `PUT`. The screen for them is still to build.

### Step 9 — Docker and README

Not started.

Add Dockerfiles, `docker-compose.yml`, `.env.example`, and `README.md` so another person can run the whole app.
