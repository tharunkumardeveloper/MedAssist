# MedAssist AI

AI-powered symptom checker: users search and pick from a 183-term symptom
vocabulary, get ranked disease candidates, an optional population-scale
chronic-disease risk screening, real-world treatment references, a
risk-priority flag with emergency detection, and a downloadable PDF report.
Providers and admins get a role-gated analytics dashboard with charts across
all assessments; admins also manage user accounts and roles.

**Disclaimer:** This is a preliminary, AI-generated assessment tool, not a
medical diagnosis. It must not be used as a substitute for professional
healthcare advice.

## Architecture

```
web/                 Primary UI: React + Vite + Tailwind + Recharts
backend/              FastAPI service: auth, prediction, risk scoring, reports, analytics, admin
model/                Three model artifacts (see below) + reference data
frontend/             Legacy Streamlit UI, kept for reference (not actively developed)
```

- **Auth**: JWT bearer tokens, bcrypt-hashed passwords, roles `patient` / `provider` / `admin`.
  Self-signup is limited to `patient`/`provider`; the first `admin` account is
  created automatically on startup from `BOOTSTRAP_ADMIN_EMAIL`/`BOOTSTRAP_ADMIN_PASSWORD`,
  and admins can promote other users afterward.
- **Prediction is three independent models, not one blended score** (`backend/predict.py`):
  - **Model 1 — symptom-similarity matcher**: cosine similarity over a 183-term
    symptom vocabulary against 155 reference diseases (`model/model1_*`),
    ranking candidates by confidence, plus a secondary regularized outcome
    classifier and rule-based emergency-symptom detection (2+ red-flag
    symptoms, e.g. chest pain + difficulty breathing, triggers an emergency
    flag).
  - **Model 2 — chronic-condition risk screening**: 10 independent Random
    Forest classifiers trained on the CDC BRFSS 2015 survey (441k
    respondents) — diabetes, heart attack, coronary HD, stroke, asthma, skin
    cancer, other cancer, arthritis, depression, kidney disease — driven by an
    optional lifestyle questionnaire (BMI, smoking, exercise, alcohol,
    cholesterol/blood-pressure history) (`model/model2_*`).
  - **Model 3 — treatment reference retrieval**: TF-IDF cosine similarity over
    999 real, de-identified MIMIC-IV hospital discharge notes, surfacing
    actual prescribed medications for the top-matched condition
    (`model/model3_*`) — illustrative reference only, not a prescription.
- **Risk scoring**: the symptom-similarity risk score is bucketed into
  `LOW` / `REVIEW` / `HIGH PRIORITY`, escalated to `HIGH PRIORITY` whenever
  the emergency-symptom detector fires.
- **Analytics**: risk distribution, top predicted diseases, a 14-day assessment
  trend, and age/gender breakdowns — visible to `provider` and `admin` roles.
- **Storage**: SQLite by default (swap `DATABASE_URL` for Postgres/MySQL in
  production — SQLAlchemy handles the rest).

## Roles

| Role | Can do |
|---|---|
| `patient` | Personal dashboard, symptom checker, assessment history + PDF reports, own profile/medical history |
| `nurse` | Triage queue (emergency case identification) + analytics dashboard |
| `provider` | Analytics dashboard (aggregate stats, charts) + triage queue |
| `clinic_admin`, `hospital_admin`, `telemedicine_admin`, `org_admin` | One role per organization type the platform serves (clinics, hospitals, telemedicine platforms, healthcare organizations). All four have identical, scoped-admin permissions: analytics, triage queue, and user management restricted to patient/nurse/provider accounts — they cannot view or modify `admin` or other org-admin accounts, nor grant those roles. |
| `admin` | Unrestricted: everything above, plus managing any account including other admins/org-admins |

Self-signup is limited to `patient`/`nurse`/`provider`. All admin-tier roles are provisioned by an existing admin (or promoted by an org-admin, within their allowed scope) via `/admin/users`.

## Local setup

Requires Python 3.12 and Node 18+.

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env   # then set SECRET_KEY to: python -c "import secrets; print(secrets.token_hex(32))"
python -m uvicorn main:app --reload

# Frontend (separate terminal)
cd web
npm install
npm run dev
```

Backend runs at `http://127.0.0.1:8000` (interactive docs at `/docs`), frontend
at `http://localhost:5173`. On Windows, always run `python -m uvicorn ...` /
`npm run dev` — the bare `uvicorn`/`streamlit` executables may not be on PATH
even when the packages are installed.

The backend's `.env` `CORS_ORIGINS` must include whatever origin the frontend
is served from (`http://localhost:5173` by default) or the browser will block
every request — the frontend logs a clear console message diagnosing this if
it happens.

An admin account is created automatically on first backend startup using
`BOOTSTRAP_ADMIN_EMAIL` / `BOOTSTRAP_ADMIN_PASSWORD` from `.env` (defaults to
`admin@medassist.local` / `ChangeMe123!` — change this before any real use).

## Running with Docker

```bash
cp .env.example .env   # set SECRET_KEY at the project root
docker compose up --build
```

Starts the backend (`:8000`) and the React frontend (`:5173`, served via
nginx). SQLite data and generated PDF reports persist in named Docker volumes
across restarts. The legacy Streamlit UI isn't started by default; run
`docker compose --profile legacy up` to include it on `:8501`.

## Configuration (backend/.env)

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | *(required, no safe default)* | JWT signing key |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token lifetime |
| `DATABASE_URL` | `sqlite:///./medassist.db` | SQLAlchemy connection string |
| `CORS_ORIGINS` | includes `:5173` and `:8501` | Comma-separated allowed origins |
| `LOGIN_RATE_LIMIT_ATTEMPTS` | `10` | Max login/signup attempts per window per IP |
| `LOGIN_RATE_LIMIT_WINDOW_SECONDS` | `60` | Rate-limit window size |
| `BOOTSTRAP_ADMIN_EMAIL` / `BOOTSTRAP_ADMIN_PASSWORD` | `admin@medassist.local` / `ChangeMe123!` | Creates one admin account on first startup if no admin exists yet |

`web/.env` has one variable: `VITE_API_URL` (defaults to `http://127.0.0.1:8000`).

## API overview

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/signup` | POST | none | Create a patient/provider account |
| `/login` | POST | none | Get a bearer token (blocked if account is deactivated) |
| `/health` | GET | none | Liveness check |
| `/reference-data` | GET | none | Symptom vocabulary, screenable chronic conditions, smoker-status options (powers the interactive symptom picker) |
| `/assess` | POST | user | Run a symptom assessment (symptoms list + vitals + optional lifestyle risk-screening profile) |
| `/history` | GET | user | List the caller's past assessments |
| `/report/{id}` | GET | user | Download a PDF report for an assessment |
| `/profile` | GET/PUT | user | View/update patient profile & medical history |
| `/analytics` | GET | provider, admin | Risk/disease/trend/demographic stats across all users |
| `/admin/users` | GET | admin | List all users with role, status, assessment count |
| `/admin/users/{id}` | PATCH | admin | Change a user's role or activate/deactivate them |

## Debugging

- Backend logs the effective CORS origin list and database URL on startup —
  check this first if the frontend reports "Could not reach the MedAssist API".
- Unhandled backend exceptions are logged with a full traceback (not just a
  bare 500) via a global exception handler in `main.py`.
- The frontend's axios client (`web/src/lib/api.js`) logs every failed
  request to the browser console with method, URL, status/response body, or —
  if no response was received — a hint pointing at the backend being down, a
  wrong `VITE_API_URL`, or a CORS origin mismatch.

## Tests

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

Tests run against an isolated temporary SQLite database per test — they do
not touch `medassist.db`.

## Known limitations / next steps

- Model 1's disease-level training data has very few real patient records per
  disease (many diseases have ~1 sample), so confidence scores express
  relative rank among the candidates shown, not a calibrated absolute
  probability — this is called out directly in the notebook that produced
  the artifacts (`MedAssist_Multimodal_Healthcare_AI.ipynb`).
- Model 2's chronic-condition screeners are trained on adult US survey
  respondents (BRFSS 2015); treat flagged results as a screening prompt to
  see a clinician, not a diagnosis.
- Model 3's treatment examples come from real but de-identified MIMIC-IV notes
  and may contain redaction placeholders (`___`) from the source anonymization.
- The in-memory rate limiter resets on restart and isn't shared across
  multiple backend processes/workers — fine for a single instance, swap for a
  Redis-backed limiter before scaling horizontally.
- No email verification or password-reset flow yet.
