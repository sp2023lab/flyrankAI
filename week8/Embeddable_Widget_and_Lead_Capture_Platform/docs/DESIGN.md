# Phase 1 Design — Embeddable Widget & Lead-Capture Platform

**Status:** Design complete; implementation not started  
**Primary stack:** Python, FastAPI, PostgreSQL, SQLAlchemy 2.x, Alembic, Redis, Docker Compose, Pytest  
**Repository name:** `flyrank-capstone-widget-platform`

## 1. Problem

The platform lets an authenticated customer create a lead-capture widget, receive a one-line `<script>` embed, place it on a website served from another origin, and receive visitor submissions.

The public internet is an untrusted input. Every submission must therefore be validated, origin-checked, rate-limited, spam-filtered, enriched where possible, stored safely, and processed without allowing a failed dependency to break the main request.

## 2. Scope

### Core scope

- Authenticated, tenant-isolated widget CRUD.
- Two widget types: `signup_form` and `contact_form`.
- One-line embed snippet using a versioned JavaScript bundle.
- Public, cached widget configuration endpoint.
- Public cross-origin submission endpoint with correct preflight handling.
- Dynamic server-side validation against the widget's configured fields.
- Payload-size limit, per-IP/per-widget rate limiting, and a honeypot.
- IP-to-geo enrichment using provider A, then provider B.
- Submission succeeds when both geo providers fail.
- DB-backed notification outbox so notification failure never rolls back a submission.
- Owner dashboard endpoints for submissions, totals over time, per-widget counts, and geo breakdown.
- Deterministic tests for the failure cases named in the brief.

### Explicit non-goals

- No drag-and-drop form builder.
- No production hosting, custom domain, or real CDN.
- No complex frontend dashboard.
- No CAPTCHA in the core release.
- No more than two widget types before all acceptance probes pass.

## 3. Actors and request paths

### Widget owner — authenticated

Creates and manages widgets, obtains embed snippets, and views submissions and analytics.

### Customer website — public

Loads `widget.v1.js`, fetches a public widget configuration, and renders the form.

### Website visitor — public

Submits form data from a different origin. The request passes through origin checks, size checks, validation, rate limiting, spam filtering, geo enrichment, persistence, and asynchronous notification.

Keeping these paths separate prevents public routes from accidentally inheriting owner privileges.

## 4. Architecture

```text
Owner
  -> FastAPI owner routes
  -> Widget / Dashboard services
  -> Repositories
  -> PostgreSQL

Customer website
  -> GET /assets/widget.v1.js
  -> GET /public/v1/widgets/{public_id}/config
  -> browser renders widget

Visitor
  -> OPTIONS /public/v1/widgets/{public_id}/submissions
  -> POST /public/v1/widgets/{public_id}/submissions
  -> origin + body-size checks
  -> dynamic validation
  -> rate limiter + honeypot
  -> geo fallback chain
  -> transaction: submission + notification outbox row
  -> success response
  -> background worker sends/logs notification with retries
```

### Layer boundaries

```text
HTTP routes
  -> application services
      -> domain policies and interfaces
          -> repositories and external-provider adapters
```

Route handlers translate HTTP to application commands. Services own the use cases. Repositories own SQL. Geo and notification providers are replaceable adapters.

## 5. Authentication and tenancy

The owner API uses an `X-API-Key` header.

- A seeded tenant receives a high-entropy API key for local development.
- Only a SHA-256 hash of the API key is stored.
- Raw keys are never logged or committed.
- Authentication resolves a `tenant_id`.
- Every widget, submission, and dashboard repository method requires `tenant_id`.
- Access to another tenant's identifier returns `404`, limiting resource enumeration.

This is intentionally simpler than a full account/password system while still providing real authorization and tenant isolation.

## 6. Data model

### `tenants`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | Internal tenant identifier |
| `name` | varchar | Display name |
| `api_key_hash` | varchar unique | Never store the raw key |
| `created_at` | timestamptz | Audit timestamp |

### `widgets`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | Internal identifier |
| `public_id` | UUID unique | Safe identifier used by the embed |
| `tenant_id` | UUID FK | Mandatory tenant scope |
| `widget_type` | enum | `signup_form` or `contact_form` |
| `title` | varchar(120) | Required |
| `description` | varchar(500) nullable | Optional |
| `button_text` | varchar(60) | Required |
| `fields` | JSONB | Ordered field definitions |
| `display_options` | JSONB | Minimal presentation settings |
| `allowed_origins` | JSONB | Exact origins permitted to fetch config and submit |
| `is_active` | boolean | Disabled widgets return `404` publicly |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

Field definitions support:

```json
{
  "name": "email",
  "label": "Email",
  "type": "email",
  "required": true,
  "max_length": 254
}
```

Allowed field types in the core release are `text`, `email`, and `textarea`.

### `submissions`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `tenant_id` | UUID FK | Duplicated deliberately for safe tenant queries |
| `widget_id` | UUID FK | |
| `idempotency_key` | UUID | Generated by widget JavaScript |
| `payload` | JSONB | Validated field values only |
| `origin` | varchar | Browser origin |
| `ip_hash` | varchar | Hash of the client IP; raw IP is not persisted |
| `user_agent` | varchar(500) nullable | Truncated |
| `country_code` | varchar(2) nullable | Enrichment may be absent |
| `country` | varchar nullable | |
| `city` | varchar nullable | |
| `geo_provider` | varchar nullable | `provider_a`, `provider_b`, or null |
| `created_at` | timestamptz | |

Unique constraint:

```text
(widget_id, idempotency_key)
```

This makes browser retries safe.

### `notification_jobs`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `submission_id` | UUID FK unique | One logical notification per submission |
| `status` | enum | `pending`, `processing`, `sent`, `failed` |
| `attempts` | integer | |
| `next_attempt_at` | timestamptz | Exponential backoff |
| `last_error` | text nullable | Sanitised; no secrets |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

### Indexes

- `widgets(tenant_id)`
- `widgets(public_id)` unique
- `submissions(tenant_id, created_at desc)`
- `submissions(widget_id, created_at desc)`
- `submissions(widget_id, idempotency_key)` unique
- `submissions(country_code)`
- `notification_jobs(status, next_attempt_at)`

## 7. Embed flow

1. Owner creates a widget.
2. API returns the widget and:

```html
<script src="http://localhost:8000/assets/widget.v1.js?id={public_id}"></script>
```

3. `widget.v1.js` reads its own `id` query parameter.
4. It requests `GET /public/v1/widgets/{public_id}/config`.
5. The server returns a small, public-safe JSON configuration.
6. JavaScript renders the configured fields.
7. On submit, JavaScript generates an idempotency UUID and sends it in the `Idempotency-Key` request header.
8. The submission API validates and stores the submission.
9. The widget displays a generic success or safe error message.

## 8. API contracts

All errors use:

```json
{
  "error": {
    "code": "machine_readable_code",
    "message": "Human-readable message",
    "details": []
  }
}
```

### Owner widget API

| Method | Path | Success | Important failures |
|---|---|---:|---|
| POST | `/api/v1/widgets` | `201` | `401`, `422` |
| GET | `/api/v1/widgets` | `200` | `401` |
| GET | `/api/v1/widgets/{id}` | `200` | `401`, `404` |
| PATCH | `/api/v1/widgets/{id}` | `200` | `401`, `404`, `422` |
| DELETE | `/api/v1/widgets/{id}` | `204` | `401`, `404` |
| GET | `/api/v1/widgets/{id}/embed` | `200` | `401`, `404` |

### Public delivery API

| Method | Path | Success | Behaviour |
|---|---|---:|---|
| GET | `/assets/widget.v1.js` | `200` | Long-lived immutable cache |
| GET | `/public/v1/widgets/{public_id}/config` | `200` | Short-lived cache + `ETag`; `404` if missing/inactive |
| OPTIONS | `/public/v1/widgets/{public_id}/config` | `204` | Returns CORS headers only for allowed origin |

### Public submission API

| Method | Path | Success | Important failures |
|---|---|---:|---|
| OPTIONS | `/public/v1/widgets/{public_id}/submissions` | `204` | Preflight |
| POST | `/public/v1/widgets/{public_id}/submissions` | `201` | `400/422`, `413`, `429`, `404` |

A filled honeypot returns a generic `202` but is not stored, avoiding feedback to the bot.

An idempotent replay returns `200` with the existing submission identifier.

### Dashboard API

| Method | Path | Success |
|---|---|---:|
| GET | `/api/v1/submissions?widget_id=&from=&to=&page=` | `200` |
| GET | `/api/v1/dashboard/summary?from=&to=` | `200` |
| GET | `/api/v1/dashboard/widgets/{id}/stats?from=&to=` | `200` |
| GET | `/api/v1/dashboard/geo?from=&to=` | `200` |

## 9. Validation and request limits

- Maximum request body: **16 KiB**, configurable through environment variables.
- Reject an oversized body with `413` before JSON parsing or business logic.
- Widget configuration is validated when created or updated.
- Submission keys must exactly match configured public fields; unknown fields are rejected except the honeypot.
- Required fields must be present.
- Text lengths and email format are enforced server-side.
- `title`, descriptions, field labels, and button text are rendered as text, not HTML.
- User agent and origin lengths are capped before persistence.

## 10. CORS policy

CORS is enforced per widget using its exact `allowed_origins`.

For an allowed origin:

- `Access-Control-Allow-Origin` echoes the exact origin.
- `Vary: Origin` is included.
- Allowed methods are `GET`, `POST`, and `OPTIONS`.
- Allowed request headers include `Content-Type` and `Idempotency-Key`.
- Credentials are not used.

For a disallowed origin, the server omits CORS permission headers and returns a safe `403` for direct non-browser calls.

A custom public-route CORS component is used because the origin policy depends on the widget being requested.

## 11. Caching

### Versioned bundle

`/assets/widget.v1.js`

```text
Cache-Control: public, max-age=31536000, immutable
```

A code change creates a new URL such as `widget.v2.js`.

### Widget configuration

```text
Cache-Control: public, max-age=60, stale-while-revalidate=300
ETag: "<config-version>"
Vary: Origin
```

Updating a widget changes the ETag. The public response excludes tenant identifiers, API-key material, and internal fields.

## 12. Abuse and spam controls

### Rate limiting

Redis maintains counters for:

- `widget + IP`: default 5 submissions per minute.
- `widget total`: default 100 submissions per minute.

Limits are configurable. Tests use a fake clock and an in-memory Redis substitute or isolated Redis database.

A burst returns `429` with `Retry-After`. The limiter must reject excess traffic without preventing a legitimate request after the window resets.

### Honeypot

The rendered form includes a visually hidden `_website` field that real users leave empty. A populated value produces a generic `202`; no submission or notification job is created.

## 13. Geo fallback

`GeoEnrichmentService` receives the client IP and tries:

1. `GeoProviderA`
2. `GeoProviderB`

Each call has a short timeout. Provider errors, invalid responses, and timeouts are caught and logged safely.

- Provider A succeeds: store its result.
- Provider A fails and B succeeds: store B's result.
- Both fail: store the submission with null geo fields.
- Geo failure never changes a successful submission into a `5xx`.

Tests mock both providers; no test depends on the public internet.

## 14. Safe side effect and background job

The submission and a `notification_jobs` row are created in the same database transaction. The HTTP response does not wait for email or webhook delivery.

A worker:

1. Claims a pending job.
2. Sends the console/Mailpit notification.
3. Marks it `sent`, or schedules a retry.
4. Uses exponential backoff with a maximum number of attempts.
5. Marks exhausted jobs `failed` and emits a structured error log.

A notification failure cannot roll back or delete the stored submission.

## 15. Idempotency

`widget.v1.js` generates a UUID for a submission attempt and reuses it when retrying the same request.

The unique database constraint on `(widget_id, idempotency_key)` prevents duplicates. If the same request reaches the service twice, the API returns the already-created submission rather than running enrichment and notification twice.

## 16. Planned package structure

```text
app/
├── api/
│   ├── dependencies.py
│   ├── owner_widgets.py
│   ├── public_widgets.py
│   ├── submissions.py
│   └── dashboard.py
├── core/
│   ├── config.py
│   ├── errors.py
│   ├── logging.py
│   └── security.py
├── domain/
│   ├── models.py
│   ├── policies.py
│   └── ports.py
├── repositories/
│   ├── tenants.py
│   ├── widgets.py
│   ├── submissions.py
│   └── notification_jobs.py
├── services/
│   ├── widgets.py
│   ├── submissions.py
│   ├── geo.py
│   ├── notifications.py
│   └── analytics.py
├── integrations/
│   ├── geo_provider_a.py
│   ├── geo_provider_b.py
│   └── notifier.py
├── workers/
│   └── notifications.py
├── static/
│   └── widget.v1.js
├── db/
│   ├── models.py
│   └── session.py
└── main.py

customer-site/
└── index.html

tests/
├── unit/
├── integration/
└── acceptance/
```

## 17. Test plan

The implementation is not considered complete until deterministic tests prove:

- Unauthenticated owner routes are rejected.
- Tenant A cannot read or mutate tenant B's data.
- CORS preflight succeeds for an allowed origin.
- A disallowed origin is not granted CORS permission.
- Malformed payload returns a clean `4xx`, never `500`.
- Oversized payload returns `413`.
- Rate-limit burst returns `429`.
- Honeypot submissions are not stored.
- Provider A failure falls back to provider B.
- Both geo providers failing still stores the submission.
- Notification failure still returns success and stores the submission.
- Duplicate idempotency key creates only one submission and one notification job.
- Widget script loads on a second-origin page and submits successfully.
- Dashboard counts and geo aggregations are tenant-scoped.

## 18. Phase 1 gate

Phase 1 is complete when:

- This design has been reviewed.
- The separate public repository exists.
- The initial repository files are committed.
- The data model, API contracts, layers, failure policy, and non-goals are accepted.
- No main feature implementation has started before these decisions are understood.
