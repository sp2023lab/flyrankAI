# FlyRank Capstone — Embeddable Widget & Lead-Capture Platform

Phase 2 implements the **hardened public submission path** from the FlyRank brief: validation, dynamic CORS, request-size protection, rate limiting, honeypot spam control, two-provider geo fallback, idempotency, persistence, and a failure-tolerant notification outbox.

## Phase 2 status

Implemented in this scaffold:

- PostgreSQL schema + Alembic migration for tenants, widgets, submissions, and notification jobs.
- Hashed API-key authentication and tenant-scoped widget create/list/get endpoints.
- Public config endpoint with a short cache policy.
- Dynamic per-widget CORS and `OPTIONS` preflight for submissions.
- 16 KiB default body limit enforced while streaming the body.
- Pydantic outer-body validation plus dynamic validation against widget field definitions.
- Redis fixed-window limits per widget+IP and per widget.
- `_website` honeypot with silent `202` drop.
- `ip-api.com` -> `ipapi.co` fallback with graceful no-geo degradation.
- Atomic submission + notification-outbox insertion.
- Idempotency via `(widget_id, idempotency_key)` unique constraint.
- Console notification worker with retries and forced-failure switch for the demo.
- Unit tests for the scary business-logic paths.

The versioned embeddable JavaScript renderer, second-origin HTML demo, full dashboard analytics, and final acceptance evidence remain Phase 3 work.

## Run

```bash
cp .env.example .env
# Replace the placeholder API key and IP hash salt with long local random values.
docker compose up --build
```

In another terminal:

```bash
docker compose exec api python -m app.scripts.seed
```

The seed command prints the widget's `public_id`, but deliberately does **not** print the API key.

## Run tests

```bash
docker compose exec api pytest -q
```

## Manual Phase 2 gate

The seeded widget permits `http://localhost:5500`. To exercise geo enrichment with a public test IP while running locally, set `TRUST_PROXY=true` in `.env`, restart the API, and use a deliberate `X-Forwarded-For` value only in this local demo.

```bash
WIDGET_ID=<public-id-from-seed>
IDEMPOTENCY=$(python -c 'import uuid; print(uuid.uuid4())')

curl -i -X OPTIONS   "http://localhost:8000/public/v1/widgets/$WIDGET_ID/submissions"   -H 'Origin: http://localhost:5500'   -H 'Access-Control-Request-Method: POST'   -H 'Access-Control-Request-Headers: Content-Type, Idempotency-Key'

curl -i   "http://localhost:8000/public/v1/widgets/$WIDGET_ID/submissions"   -H 'Origin: http://localhost:5500'   -H 'Content-Type: application/json'   -H "Idempotency-Key: $IDEMPOTENCY"   -H 'X-Forwarded-For: 8.8.8.8'   --data '{"fields":{"name":"Ada","email":"ada@example.com","message":"Hello"},"_website":""}'
```

Expected: `201`, a stored submission, and geo fields when at least one provider is reachable. If both providers are unavailable, the same submission should still return success with null geo fields.

## Failure demonstrations

- **Malformed/invalid input:** omit required email or submit an invalid email -> clean `422` JSON error.
- **Oversized payload:** send more than `MAX_SUBMISSION_BODY_BYTES` -> `413`.
- **Spam:** populate `_website` -> `202`, no row stored.
- **Rate limit:** burst requests -> `429` with `Retry-After`.
- **Geo fallback:** set `GEO_PROVIDER_A_ENABLED=false` -> provider B is used; disable both -> submission still stores.
- **Notification failure:** set `NOTIFICATION_FORCE_FAIL=true` -> worker retries/fails the job, while the original submission remains stored.
- **Idempotency:** resend the same `Idempotency-Key` -> existing submission, no duplicate notification job.

## Security notes

- `.env` is git-ignored; only `.env.example` belongs in the repo.
- Raw API keys are never persisted.
- Raw client IP addresses are used only during the request for rate limiting/geo and are stored only as a salted hash.
- `TRUST_PROXY` defaults to false and should only be enabled behind a trusted proxy (or for the explicit local geo demo above).
- Public widget lookup uses a separate `public_id`; tenant IDs are never returned from public config.

## Architecture

See [`docs/DESIGN.md`](docs/DESIGN.md) and [`docs/PHASE2.md`](docs/PHASE2.md).
