# PDF Report Generator

A complete Week 4 FlyRank Backend AI Engineering assignment: query data, aggregate it with SQL, generate a PDF in a background worker, store the PDF as an artifact, and return a download link when the job completes.

## Architecture

```text
Client
  |
  | POST /api/v1/reports
  v
FastAPI API --------------------> PostgreSQL
  |                               - orders
  | enqueue job                   - report_jobs
  v                               - report_artifacts
Redis broker
  |
  v
Celery worker
  | SQL aggregation
  | ReportLab rendering
  v
Shared artifacts directory
  |
  v
GET /api/v1/reports/{report_id}/download
```

The API never sends PDF bytes through Redis. The queue receives only the small job ID. The worker stores the generated file and records its metadata in PostgreSQL.

## Features

- `202 Accepted` asynchronous report requests
- Job states: `queued`, `running`, `completed`, `failed`
- SQL aggregation of totals, average order value, status breakdown and daily revenue
- PDF generation with ReportLab
- Shared artifact storage and safe download endpoint
- PostgreSQL persistence
- Redis and Celery worker
- Docker Compose orchestration
- Pytest end-to-end pipeline test
- Optional Celery Beat daily scheduled report
- Interactive Swagger UI

## Project structure

```text
app/
├── routers/                 # HTTP endpoints
├── repositories/            # Database access
├── services/                # SQL analytics and PDF rendering
├── celery_app.py            # Worker configuration
├── config.py                # Environment settings
├── database.py              # SQLAlchemy engine/session
├── main.py                  # FastAPI application
├── models.py                # Orders, jobs and artifacts
├── schemas.py               # Pydantic API models
└── tasks.py                 # Celery background jobs
scripts/seed.py              # Command-line demo data seeder
tests/test_pipeline.py       # Full request -> worker -> PDF test
```

## Run with Docker

Docker is the recommended route, especially on Windows, because the API, PostgreSQL, Redis and the Linux-based Celery worker run consistently in containers.

```bash
cp .env.example .env
docker compose up --build
```

Open:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Demo the full pipeline

### 1. Seed order data

```bash
curl -X POST http://localhost:8000/api/v1/demo/orders/seed \
  -H "Content-Type: application/json" \
  -d '{"count":60}'
```

### 2. Request a PDF report

```bash
curl -X POST http://localhost:8000/api/v1/reports \
  -H "Content-Type: application/json" \
  -d '{"report_type":"sales_summary","title":"FlyRank Sales Summary"}'
```

Example response:

```json
{
  "id": "JOB_UUID",
  "status": "queued",
  "report_type": "sales_summary",
  "title": "FlyRank Sales Summary",
  "requested_at": "2026-07-11T13:00:00Z",
  "started_at": null,
  "completed_at": null,
  "report_id": null,
  "error": null,
  "status_url": "http://localhost:8000/api/v1/jobs/JOB_UUID",
  "download_url": null
}
```

### 3. Poll the job

```bash
curl http://localhost:8000/api/v1/jobs/JOB_UUID
```

When completed, the response contains `report_id` and `download_url`.

### 4. Download the PDF

```bash
curl -OJ http://localhost:8000/api/v1/reports/REPORT_UUID/download
```

Generated files also appear in the local `artifacts/` directory because it is shared by the API and worker containers.

## Endpoint summary

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Database-backed health check |
| `POST` | `/api/v1/demo/orders/seed` | Add deterministic demonstration data |
| `GET` | `/api/v1/demo/orders/summary` | Preview the SQL aggregation |
| `POST` | `/api/v1/reports` | Queue a PDF report and return `202` |
| `GET` | `/api/v1/jobs/{job_id}` | Poll background job status |
| `GET` | `/api/v1/reports` | List generated artifacts |
| `GET` | `/api/v1/reports/{report_id}` | Read artifact metadata |
| `GET` | `/api/v1/reports/{report_id}/download` | Download the PDF |

## Scheduled report stretch goal

Set the schedule in `.env`:

```dotenv
ENABLE_SCHEDULED_REPORTS=true
SCHEDULE_HOUR_UTC=8
SCHEDULE_MINUTE_UTC=0
```

Then start the optional Celery Beat service:

```bash
docker compose --profile schedule up --build
```

Beat creates a database job each day and sends its ID to the worker, reusing the same on-demand generation pipeline.

## Tests

Local tests use SQLite and an in-memory Celery configuration, so PostgreSQL and Redis are not required:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
ruff check .
```

The main test seeds orders, queues a job, executes the worker task, verifies the completed state, downloads the artifact and confirms that the response begins with a valid `%PDF` header.

## Failure handling

If PDF generation fails, the worker rolls back the active transaction and records the error against the job with `failed` status. If Redis is unavailable when the API attempts to enqueue a job, the job is marked failed and the API returns `503 Service Unavailable`.

## Deployment notes

For a public submission, deploy all four runtime components:

1. FastAPI web service
2. Celery worker using the same image
3. PostgreSQL database
4. Redis broker

Both the API and worker must have access to the same persistent artifact storage. In a larger production system, replace the shared directory with S3-compatible object storage and save the object key in `report_artifacts.file_path`.

## Technical references

- FastAPI container deployment: https://fastapi.tiangolo.com/deployment/docker/
- Celery documentation: https://docs.celeryq.dev/
- Celery Redis broker: https://docs.celeryq.dev/en/main/getting-started/backends-and-brokers/redis.html
- SQLAlchemy ORM: https://docs.sqlalchemy.org/orm/
- ReportLab PDF library: https://docs.reportlab.com/reportlab/userguide/ch1_intro/
