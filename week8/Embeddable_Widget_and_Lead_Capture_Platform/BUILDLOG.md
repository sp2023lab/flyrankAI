# Build Log

## Phase 1 — Design

The capstone architecture, data model, API surface, failure behaviour, and explicit non-goals were designed before the main implementation.

## 2026-08-07 — Phase 2 hardened submission path

### Work completed

- Implemented the Postgres persistence model and Alembic migration.
- Implemented a seeded tenant/widget path and basic authenticated widget management.
- Implemented the public submission route with bounded body reading and standard JSON errors.
- Added exact per-widget CORS handling and preflight.
- Added configured-field validation, Redis rate limits, and a honeypot.
- Added two-provider geo fallback with graceful no-geo degradation.
- Added salted IP hashing for persisted request metadata.
- Added atomic submission + notification-outbox creation.
- Added a background notification worker with retry/failure state.
- Added idempotent replay handling.
- Added deterministic unit tests for core failure paths.

### AI assistance

ChatGPT generated the initial Phase 2 implementation from the supplied FlyRank capstone brief and the Phase 1 design. AI assistance was used for scaffolding, architecture translation, code drafting, tests, and documentation.

### Human review required before submission

The developer must run the system, inspect the migration and security boundaries, understand the Redis limiter and outbox behaviour, and be able to explain any evaluator-selected lines. Any code not understood should be changed before it is submitted.
