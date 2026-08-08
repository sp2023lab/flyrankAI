# EVIDENCE.md

## FlyRank Capstone — Embeddable Widget & Lead-Capture Platform

**Phase:** Phase 2 — Hardened Submission Path  
**Environment:** Docker Compose, FastAPI, PostgreSQL, Redis  
**Local API:** `http://localhost:8001`  
**Second origin used for CORS tests:** `http://localhost:5500`  
**Date captured:** 2026-08-08

This file contains pasted runtime/test proof for the Phase 2 requirements. The commands below were executed against the local Docker Compose stack.

---

## 1. Automated tests

**Result: PASS**

Command:

```powershell
docker compose exec api pytest -q
```

Output:

```text
....................                                                    [100%]
20 passed in 1.43s
```

Focused geo fallback tests:

```powershell
docker compose exec api pytest tests/test_geo_fallback.py -vv
```

Output:

```text
======================================= test session starts ========================================
platform linux -- Python 3.12.13, pytest-8.4.2, pluggy-1.6.0 -- /usr/local/bin/python3.12
cachedir: .pytest_cache
rootdir: /app
configfile: pyproject.toml
plugins: asyncio-1.4.0, anyio-4.14.2
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 2 items

tests/test_geo_fallback.py::test_falls_back_to_second_provider PASSED                        [ 50%]
tests/test_geo_fallback.py::test_all_providers_down_degrades_to_none PASSED                  [100%]

======================================== 2 passed in 0.41s =========================================
```

---

## 2. Seeded widget exists

**Result: PASS**

Command:

```powershell
docker compose exec api python -m app.scripts.seed
```

Output:

```text
Seed complete. widget_public_id=380f2da6-d38d-4bcc-b3e3-53822a2faee4 allowed_origin=http://localhost:5500
API key was read from SEED_TENANT_API_KEY and was not printed.
```

Database proof:

```powershell
docker compose exec db psql -U postgres -d widget_platform -c "SELECT public_id, title, is_active, allowed_origins FROM widgets;"
```

Output:

```text
              public_id               |       title       | is_active |      allowed_origins
--------------------------------------+-------------------+-----------+---------------------------
380f2da6-d38d-4bcc-b3e3-53822a2faee4 | Demo Contact Form | t         | ["http://localhost:5500"]
(1 row)
```

---

## 3. Public config delivery and caching

**Result: PASS**

Command:

```powershell
curl.exe -i "http://localhost:8001/public/v1/widgets/$widgetId/config" `
  -H "Origin: http://localhost:5500"
```

Relevant output:

```text
HTTP/1.1 200 OK
cache-control: public, max-age=60, stale-while-revalidate=300
access-control-allow-origin: http://localhost:5500
access-control-allow-methods: GET, POST, OPTIONS
access-control-allow-headers: Content-Type, Idempotency-Key
access-control-max-age: 600
vary: Origin
content-type: application/json
```

Response body:

```json
{
  "public_id": "380f2da6-d38d-4bcc-b3e3-53822a2faee4",
  "type": "contact_form",
  "title": "Demo Contact Form",
  "description": "Phase 2 seeded widget",
  "button_text": "Contact us",
  "fields": [
    {
      "name": "name",
      "type": "text",
      "label": "Name",
      "required": true,
      "max_length": 100
    },
    {
      "name": "email",
      "type": "email",
      "label": "Email",
      "required": true,
      "max_length": 254
    },
    {
      "name": "message",
      "type": "textarea",
      "label": "Message",
      "required": false,
      "max_length": 1000
    }
  ],
  "display_options": {}
}
```

---

## 4. Allowed-origin CORS preflight

**Result: PASS**

Command:

```powershell
curl.exe -i -X OPTIONS "http://localhost:8001/public/v1/widgets/$widgetId/submissions" `
  -H "Origin: http://localhost:5500" `
  -H "Access-Control-Request-Method: POST" `
  -H "Access-Control-Request-Headers: Content-Type, Idempotency-Key"
```

Output:

```text
HTTP/1.1 204 No Content
access-control-allow-origin: http://localhost:5500
access-control-allow-methods: GET, POST, OPTIONS
access-control-allow-headers: Content-Type, Idempotency-Key
access-control-max-age: 600
vary: Origin
```

This proves the browser preflight path is accepted for the configured external origin.

---

## 5. Valid enriched cross-origin submission

**Result: PASS**

Request body:

```json
{
  "fields": {
    "name": "Ada",
    "email": "ada@example.com",
    "message": "Hello from Phase 2"
  },
  "_website": ""
}
```

The request was sent from origin `http://localhost:5500` with a fresh idempotency key and `X-Forwarded-For: 8.8.8.8`.

HTTP output:

```text
201
{"status":"stored","submission_id":"399e53bc-dd4f-4834-b46a-72cd8f413f10","duplicate":false}
```

Database proof:

```powershell
docker compose exec db psql -U postgres -d widget_platform -c "SELECT id, payload, country_code, country, city, geo_provider, created_at FROM submissions ORDER BY created_at DESC LIMIT 5;"
```

Relevant row:

```text
                  id                  |                                   payload                                   | country_code |    country    |  city   | geo_provider |          created_at
--------------------------------------+-----------------------------------------------------------------------------+--------------+---------------+---------+--------------+-------------------------------
399e53bc-dd4f-4834-b46a-72cd8f413f10 | {"name": "Ada", "email": "ada@example.com", "message": "Hello from Phase 2"} | US           | United States | Ashburn | ip-api       | 2026-08-08 01:08:20.271684+00
(1 row)
```

This proves a valid cross-origin submission was stored and enriched with geo data.

---

## 6. Invalid payload

**Result: PASS**

A malformed JSON submission was sent to the public submission endpoint.

Output:

```text
HTTP/1.1 422 Unprocessable Entity
content-type: application/json
```

Body:

```json
{
  "error": {
    "code": "invalid_submission",
    "message": "Malformed JSON.",
    "details": []
  }
}
```

No `500` was produced.

---

## 7. Oversized payload

**Result: PASS**

A JSON body containing a message larger than the configured `16384` byte maximum was submitted.

Output:

```text
HTTP/1.1 413 Request Entity Too Large
access-control-allow-origin: http://localhost:5500
access-control-allow-methods: GET, POST, OPTIONS
access-control-allow-headers: Content-Type, Idempotency-Key
vary: Origin
content-type: application/json
```

Body:

```json
{
  "error": {
    "code": "payload_too_large",
    "message": "Request body exceeds 16384 bytes.",
    "details": []
  }
}
```

---

## 8. Rate limiting

**Result: PASS**

Six rapid requests were sent from the same forwarded IP and widget using fresh idempotency keys.

Output:

```text
REQUEST 1
HTTP/1.1 202 Accepted

REQUEST 2
HTTP/1.1 202 Accepted

REQUEST 3
HTTP/1.1 202 Accepted

REQUEST 4
HTTP/1.1 202 Accepted

REQUEST 5
HTTP/1.1 202 Accepted

REQUEST 6
HTTP/1.1 429 Too Many Requests
retry-after: 60
```

This proves the configured per-widget/IP limiter returns `429` under a burst and communicates a retry interval.

---

## 9. Honeypot spam control

**Result: PASS**

Spam body:

```json
{
  "fields": {
    "name": "Spam Bot",
    "email": "bot@example.com"
  },
  "_website": "https://spam.example"
}
```

HTTP response:

```text
202
{"status":"accepted"}
```

Database check after the request:

```text
count
-------
0
(1 row)
```

The response intentionally does not reveal the spam decision, while the submission is not stored.

---

## 10. Idempotent retry

**Result: PASS**

The same logical submission was resent using the same `Idempotency-Key`.

First submission:

```text
201
{"status":"stored","submission_id":"399e53bc-dd4f-4834-b46a-72cd8f413f10","duplicate":false}
```

Retry:

```text
200
{"status":"stored","submission_id":"399e53bc-dd4f-4834-b46a-72cd8f413f10","duplicate":true}
```

Database proof showed only one submission row:

```text
count
-------
1
(1 row)
```

Database proof also showed only one notification job for the submission:

```text
count
-------
1
(1 row)
```

This proves a retried action happens once.

---

## 11. Geo provider fallback

**Result: PASS — deterministic automated proof**

Focused test command:

```powershell
docker compose exec api pytest tests/test_geo_fallback.py -vv
```

Relevant output:

```text
tests/test_geo_fallback.py::test_falls_back_to_second_provider PASSED
tests/test_geo_fallback.py::test_all_providers_down_degrades_to_none PASSED

2 passed in 0.41s
```

The fallback test deterministically simulates provider A failing and verifies that provider B supplies the result.

### Manual live-provider note

For manual development, provider A was disabled and provider B (`ipapi.co`) was enabled:

```text
GEO_PROVIDER_A_ENABLED=false
GEO_PROVIDER_B_ENABLED=true
```

Resolved Compose configuration also showed the same values.

The live provider B request returned:

```text
429
{
  "error": true,
  "reason": "RateLimited",
  "message": "Visit https://ipapi.co/ratelimited/ for details"
}
```

Application log:

```text
geo_provider_failed provider=ipapi.co error=HTTPStatusError
```

The submission path still succeeded without geo, demonstrating graceful degradation even when the real fallback provider was rate-limited. The deterministic test above is the canonical proof of the A -> B fallback behavior.

---

## 12. All geo providers unavailable

**Result: PASS**

Both providers were disabled:

```text
GEO_PROVIDER_A_ENABLED=false
GEO_PROVIDER_B_ENABLED=false
```

Submission response:

```text
201
{"status":"stored","submission_id":"1f603405-bf98-43bd-976b-c086b0e46e88","duplicate":false}
```

Database proof:

```text
                                           payload                                            | country_code | country | city | geo_provider
----------------------------------------------------------------------------------------------+--------------+---------+------+--------------
{"name": "No Geo Test", "email": "nogeo@example.com", "message": "Both providers disabled"}   |              |         |      |
(1 row)
```

The submission was stored successfully with null/empty geo fields.

---

## 13. Background notification — successful processing

**Result: PASS**

The notification worker was started and the previously pending notification was processed.

Worker status:

```text
worker ... Up
```

Database proof:

```text
            submission_id             | status | attempts |        next_attempt_at        | last_error
--------------------------------------+--------+----------+-------------------------------+------------
399e53bc-dd4f-4834-b46a-72cd8f413f10 | sent   |        1 | 2026-08-08 01:08:20.271684+00 |
(1 row)
```

Worker log:

```text
INFO:notification-worker:confirmation_notification submission_id=399e53bc-dd4f-4834-b46a-72cd8f413f10
```

---

## 14. Notification failure does not break submission

**Result: PASS**

The notification worker was configured to fail deliberately.

The public submission still succeeded:

```text
201
{"status":"stored","submission_id":"3b77c63c-4e4b-44c8-aa24-8918612e03e3","duplicate":false}
```

Database proof that the submission survived:

```text
                  id                  |                                                    payload
--------------------------------------+----------------------------------------------------------------------------------------------------------------
3b77c63c-4e4b-44c8-aa24-8918612e03e3 | {"name": "Notification Failure Test", "email": "notifyfail@example.com", "message": "Submission must survive"}
(1 row)
```

Notification job state after retries:

```text
            submission_id             | status | attempts |  last_error
--------------------------------------+--------+----------+--------------
3b77c63c-4e4b-44c8-aa24-8918612e03e3 | failed |        3 | RuntimeError
1f603405-bf98-43bd-976b-c086b0e46e88 | sent   |        1 |
2894198e-a32e-406f-a52f-2d5561f7f248 | sent   |        1 |
399e53bc-dd4f-4834-b46a-72cd8f413f10 | sent   |        1 |
(4 rows)
```

Worker logs:

```text
WARNING:notification-worker:notification_failed job=49fca1e7-542e-460b-86a9-5c874c139a8d attempts=1
WARNING:notification-worker:notification_failed job=49fca1e7-542e-460b-86a9-5c874c139a8d attempts=2
WARNING:notification-worker:notification_failed job=49fca1e7-542e-460b-86a9-5c874c139a8d attempts=3
```

This proves a non-critical notification failure does not roll back or destroy the original submission.

---

# Phase 2 acceptance summary

| Requirement | Evidence |
|---|---|
| Automated tests | PASS — 20/20 |
| Public widget config | PASS — `200` |
| Cache headers | PASS |
| Allowed-origin CORS | PASS |
| Preflight handling | PASS — `204` |
| Valid cross-origin submission | PASS — `201` |
| Stored geo enrichment | PASS |
| Invalid/malformed input | PASS — `422` |
| Oversized payload | PASS — `413` |
| Rate limiting | PASS — `429` + `Retry-After` |
| Honeypot spam control | PASS — `202`, no row |
| Idempotency | PASS — duplicate retry reuses same row |
| Provider A -> provider B fallback | PASS — deterministic test |
| All providers unavailable | PASS — submission still stored |
| Background job | PASS |
| Notification failure isolation | PASS — submission survives three failed retries |

## Phase 2 gate

**PASS**

A valid request from a different origin successfully reached the public submission API, passed validation and abuse controls, was geo-enriched, and was stored in PostgreSQL.

Submission:

```text
399e53bc-dd4f-4834-b46a-72cd8f413f10
```

Stored geo proof:

```text
country_code = US
country      = United States
city         = Ashburn
geo_provider = ip-api
```

Phase 2 — Hardened Submission Path is complete.
