# FlyRank PDF Report Generator + Background AI Jobs

This FastAPI project demonstrates two production-style asynchronous workflows:

1. PDF generation through PostgreSQL, Redis and Celery.
2. AI report summarisation accepted immediately with `202 Accepted`, processed by a worker, and exposed through a polling endpoint.

## BE-06 architecture

```text
Client
  |
  | POST /api/v1/summarize
  | Idempotency-Key: request-123
  v
FastAPI -> PostgreSQL ai_jobs row -> Redis queue -> Celery worker -> Groq
  |                                                       |
  | 202 + Location                                        | validated result/error
  v                                                       v
GET /api/v1/ai-jobs/{job_id} <---------------------- PostgreSQL
```

The API process never waits for the AI provider. It validates the request, persists a queued job, enqueues only the job ID and returns immediately.

## Reliability behaviour

- **Idempotent submission:** the same `Idempotency-Key` returns the original job and is not enqueued twice.
- **Idempotent worker:** completed and permanently failed jobs are not executed again.
- **Atomic claiming:** only a queued/retrying job, or a stale running job, can be claimed.
- **Retries:** retryable provider/network/timeout failures and invalid structured output use bounded exponential backoff.
- **Permanent failure:** exhausted or non-retryable jobs become `failed` with a safe error field.
- **Alerts:** permanent failures emit a structured critical alert and can optionally POST to `AI_FAILURE_WEBHOOK_URL`.
- **Late acknowledgement:** Celery uses `task_acks_late` and `task_reject_on_worker_lost` so interrupted work can be redelivered safely.

Job states:

```text
queued -> running -> completed
            |
            +-> retrying -> running
            |
            +-> failed
```

## Run

```bash
cp .env.example .env
# Put a real GROQ_API_KEY in .env
docker compose up --build
```

Open Swagger at `http://localhost:8000/docs`.

## Submit an AI job

```bash
curl -i -X POST http://localhost:8000/api/v1/summarize \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: demo-request-001" \
  -d '{
    "text": "Revenue increased by 18 percent. Refunds fell by 7 percent. Mobile orders now account for 61 percent of sales."
  }'
```

The response is `202 Accepted` and includes `Location` and `Retry-After` headers:

```json
{
  "id": "JOB_UUID",
  "status": "queued",
  "feature": "summarize",
  "attempts": 0,
  "max_attempts": 3,
  "result": null,
  "error": null,
  "status_url": "http://localhost:8000/api/v1/ai-jobs/JOB_UUID"
}
```

Poll the job:

```bash
curl http://localhost:8000/api/v1/ai-jobs/JOB_UUID
```

Completed response:

```json
{
  "id": "JOB_UUID",
  "status": "completed",
  "attempts": 1,
  "max_attempts": 3,
  "result": {
    "bullets": [
      "Revenue increased by 18 percent.",
      "Refunds fell by 7 percent.",
      "Mobile orders account for 61 percent of sales."
    ]
  },
  "error": null
}
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/summarize` | Persist and enqueue an AI summary job; returns `202` |
| `GET` | `/api/v1/ai-jobs/{job_id}` | Poll AI job state/result/error |
| `POST` | `/api/v1/reports` | Queue a PDF report |
| `GET` | `/api/v1/jobs/{job_id}` | Poll PDF report job state |
| `GET` | `/health` | Database-backed health check |

## Tests

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
PYTHONPATH=. pytest -q
```

The BE-06 tests cover immediate `202`, status URLs, duplicate submissions, successful worker execution, duplicate worker delivery, retry state, exhausted failure alerts and `404` status lookup. Provider calls are mocked and consume no API quota.
