# Phase 3 Merge Guide

This ZIP is a **full project snapshot**, not only a diff.

## Before copying it over the live Windows project

1. Keep your current `.env` private and backed up. The ZIP intentionally contains only `.env.example`.
2. Keep any screenshots/raw terminal transcripts you want for evidence.
3. Copy the Phase 3 files into the capstone project, allowing source/docs files to update.
4. Do **not** add `.env` to Git.

## Reset temporary Phase 2 failure-demo settings

During Phase 2 you deliberately disabled dependencies. Before the normal Phase 3 browser demo, use normal settings in `.env`:

```env
GEO_PROVIDER_A_ENABLED=true
GEO_PROVIDER_B_ENABLED=true
NOTIFICATION_FORCE_FAIL=false
```

`TRUST_PROXY=false` is the safe default. If you keep it `true` for a deliberate local test, document why; do not treat arbitrary forwarded headers as trusted in production.

The generated project uses:

```env
PUBLIC_BASE_URL=http://localhost:8001
SEED_WIDGET_ORIGIN=http://localhost:5500
```

## Restart after the merge

```powershell
docker compose down
docker compose up --build
```

The updated Compose file uses a named PostgreSQL volume. If your old database container did not use that volume, the first run of this version may start with a fresh database. That is fine for the capstone; run the seed command again:

```powershell
docker compose exec api python -m app.scripts.seed
```

Then:

```powershell
docker compose exec api python -m pytest -q
```

## Browser demo

Copy the `widget_public_id` printed by the seed command into `customer-site/index.html`, replacing:

```text
PASTE_WIDGET_PUBLIC_ID_HERE
```

Serve the external site:

```powershell
cd customer-site
python -m http.server 5500
```

Open `http://localhost:5500` and submit the widget.

For the minimal owner table, open:

```text
http://localhost:8001/demo/dashboard
```

and enter the local `SEED_TENANT_API_KEY` when prompted.

## Evidence

Phase 2 evidence is preserved in `EVIDENCE.md`. Phase 3 sections are intentionally TODO until you capture the actual browser/dashboard runtime results locally.
