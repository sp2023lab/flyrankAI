# Phase 2 — Hardened Submission Path

## Gate

A cross-origin request from an allowed origin reaches the public endpoint, passes boundary validation and abuse controls, is enriched by the first available geo provider, and is stored with a notification-outbox row. Dependency failure must degrade, not convert the request into a `500`.

## Implemented request path

```text
OPTIONS/POST request
  -> widget lookup
  -> exact origin check + response CORS headers
  -> bounded streaming body read
  -> JSON + Pydantic outer-shape validation
  -> idempotency lookup
  -> Redis widget/IP + widget-total rate limits
  -> honeypot drop
  -> dynamic configured-field validation
  -> geo provider A -> provider B -> no geo
  -> atomic submission + notification job
  -> 201 (or 200 on idempotent replay)
```

## Error contract

Public application errors use:

```json
{"error":{"code":"invalid_submission","message":"...","details":[]}}
```

Expected statuses: `200/201/202`, `403`, `404`, `413`, `422`, `429`. Untrusted input should not cause a `500`.

## Phase 2 test target

The included tests are deterministic and do not call live geo providers. Full browser/second-origin rendering is intentionally deferred to Phase 3.
