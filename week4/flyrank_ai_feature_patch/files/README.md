# PDF Report Generator

A FlyRank Backend AI Engineering project that queries order data, aggregates it with SQL,
generates PDFs in a background worker, and adds a real schema-validated AI feature for
summarising report text into exactly three bullets.

## Architecture

```text
PDF pipeline
------------
Client -> FastAPI -> PostgreSQL
                    |
                    | enqueue job ID
                    v
                  Redis -> Celery worker -> ReportLab PDF -> shared artifacts

AI pipeline
-----------
Client -> POST /api/v1/summarize -> provider-neutral AI interface
                                  -> Groq chat completions
                                  -> JSON Schema output
                                  -> Pydantic validation
                                  -> three summary bullets
```

The API never sends PDF bytes through Redis. The queue receives only the small job ID. The
worker stores the generated file and records its metadata in PostgreSQL.

Only `app/ai/groq_provider.py` knows Groq's HTTP API. The rest of the application calls the
provider-neutral `AIProvider.complete(...)` interface.

## Features

- `202 Accepted` asynchronous PDF report requests
- Job states: `queued`, `running`, `completed`, `failed`
- SQL aggregation of totals, average order value, status breakdown and daily revenue
- PDF generation with ReportLab
- Shared artifact storage and safe download endpoint
- PostgreSQL persistence
- Redis and Celery worker
- `POST /api/v1/summarize` AI endpoint
- Strict JSON Schema output plus Pydantic validation
- One retry for malformed model output
- Timeout on every AI request
- Retry with exponential backoff for `429`, `5xx`, network failures and timeouts
- No retry for `400` or other non-transient `4xx` responses
- Per-call token and estimated-cost logging without prompts or API keys
- Docker Compose orchestration
- Pytest pipeline and AI reliability tests
- Optional Celery Beat daily scheduled report
- Interactive Swagger UI

## Project structure

```text
app/
├── ai/
│   ├── base.py               # Provider-neutral interface, result and exceptions
│   ├── factory.py            # Provider selection seam
│   └── groq_provider.py      # Groq HTTP request, retries and cost logging
├── routers/
│   ├── summarize.py          # POST /api/v1/summarize
│   └── ...                   # Existing report, demo and health endpoints
├── repositories/             # Database access
├── services/                 # SQL analytics and PDF rendering
├── celery_app.py             # Worker configuration
├── config.py                 # Environment settings
├── database.py               # SQLAlchemy engine/session
├── main.py                   # FastAPI application
├── models.py                 # Orders, jobs and artifacts
├── schemas.py                # Pydantic API and AI models
└── tasks.py                  # Celery background jobs
scripts/seed.py               # Command-line demo data seeder
tests/test_pipeline.py        # Full request -> worker -> PDF test
tests/test_summarize.py       # AI validation, retry, timeout and cost tests
```

## Configuration

Copy the example file and place your own Groq key in the local `.env` file:

```bash
cp .env.example .env
```

```dotenv
AI_PROVIDER=groq
GROQ_API_KEY=your_real_key_here
GROQ_MODEL=openai/gpt-oss-20b
AI_TIMEOUT_SECONDS=20
AI_MAX_RETRIES=1
AI_RETRY_BACKOFF_SECONDS=0.5
GROQ_INPUT_COST_PER_MILLION=0.075
GROQ_OUTPUT_COST_PER_MILLION=0.30
```

`.env` is ignored by Git and the API key is never included in application logs.

## Run with Docker

Docker is the recommended route, especially on Windows, because the API, PostgreSQL, Redis
and the Linux-based Celery worker run consistently in containers.

```bash
docker compose up --build
```

Open:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Demo the AI feature

```bash
curl -X POST http://localhost:8000/api/v1/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Revenue increased by 18 percent. Refunds fell by 7 percent. Mobile orders now account for 61 percent of sales."
  }'
```

Example response:

```json
{
  "bullets": [
    "Revenue increased by 18 percent.",
    "Refunds fell by 7 percent.",
    "Mobile orders account for 61 percent of sales."
  ]
}
```

The model is asked for strict JSON Schema output and the returned JSON is then validated again
with Pydantic. If the model output is malformed or does not contain exactly three non-empty
bullets, the application makes one fresh model call. A second invalid response becomes a clean
`502 Bad Gateway` response rather than crashing the API.

A successful provider call writes a line similar to:

```text
INFO ai_call feature=summarize provider=groq model=openai/gpt-oss-20b input_tokens=184 output_tokens=61 estimated_cost_usd=0.00003210
```

The estimate uses the configurable input and output prices in `.env`. Token counts come from the
provider response.

## Demo the PDF pipeline

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

Generated files also appear in the local `artifacts/` directory because it is shared by the API
and worker containers.

## Endpoint summary

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Database-backed health check |
| `POST` | `/api/v1/summarize` | Return exactly three schema-validated AI summary bullets |
| `POST` | `/api/v1/demo/orders/seed` | Add deterministic demonstration data |
| `GET` | `/api/v1/demo/orders/summary` | Preview the SQL aggregation |
| `POST` | `/api/v1/reports` | Queue a PDF report and return `202` |
| `GET` | `/api/v1/jobs/{job_id}` | Poll background job status |
| `GET` | `/api/v1/reports` | List generated artifacts |
| `GET` | `/api/v1/reports/{report_id}` | Read artifact metadata |
| `GET` | `/api/v1/reports/{report_id}/download` | Download the PDF |

## AI reliability behaviour

| Failure | Behaviour |
|---|---|
| Invalid model JSON or wrong schema | Make one new model call, then return `502` |
| Provider `429` | Retry with short exponential backoff |
| Provider `5xx` | Retry with short exponential backoff |
| Timeout or network failure | Retry once, then return `504` or `503` |
| Provider `400` or other non-transient `4xx` | Do not retry; return a clean `502` |
| Missing API key | Return `503` without exposing configuration details |

## Provider seam

Application code depends on this interface:

```python
await provider.complete(
    feature="summarize",
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    schema=SummaryResult.model_json_schema(),
)
```

`app/ai/factory.py` is the only provider-selection point. Adding Gemini or Ollama means adding a
provider implementation and selecting it there; the endpoint and schemas do not change.

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

Beat creates a database job each day and sends its ID to the worker, reusing the same on-demand
generation pipeline.

## Tests

Local tests use SQLite, an in-memory Celery configuration and mocked AI transports, so PostgreSQL,
Redis and a Groq API key are not required:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
ruff check .
```

The tests cover the full PDF pipeline, valid AI responses, empty input, malformed-output retry,
clean failure after two invalid outputs, `429` retry, `5xx` retry, timeout handling, no retry for
`400`, token/cost logging and API-key redaction.

## Failure handling

If PDF generation fails, the worker rolls back the active transaction and records the error
against the job with `failed` status. If Redis is unavailable when the API attempts to enqueue a
job, the job is marked failed and the API returns `503 Service Unavailable`.

AI provider failures are translated into clean gateway/service responses. Provider response bodies,
prompts, source text and API keys are not placed in logs.

## Deployment notes

For a public PDF-pipeline deployment, deploy all four runtime components:

1. FastAPI web service
2. Celery worker using the same image
3. PostgreSQL database
4. Redis broker

Both the API and worker must have access to the same persistent artifact storage. In a larger
production system, replace the shared directory with S3-compatible object storage and save the
object key in `report_artifacts.file_path`.

Add `GROQ_API_KEY` as a secret environment variable on the deployment platform. Do not commit a
real key to GitHub.

## Technical references

- FastAPI container deployment: https://fastapi.tiangolo.com/deployment/docker/
- Groq structured outputs: https://console.groq.com/docs/structured-outputs
- Groq API reference: https://console.groq.com/docs/api-reference
- Groq pricing: https://groq.com/pricing
- Celery documentation: https://docs.celeryq.dev/
- Celery Redis broker: https://docs.celeryq.dev/en/main/getting-started/backends-and-brokers/redis.html
- SQLAlchemy ORM: https://docs.sqlalchemy.org/orm/
- ReportLab PDF library: https://docs.reportlab.com/reportlab/userguide/ch1_intro/
