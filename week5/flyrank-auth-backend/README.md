# FlyRank Auth — Login & Protect

A complete FastAPI implementation of the Week 5 Backend AI Engineering authentication assignment.

## What it demonstrates

- User registration with validated username, email, and password
- Passwords stored as Argon2 hashes, never plaintext
- Login using username or email
- Signed JWT bearer access tokens with expiry
- `/protected` available only to an authenticated, active user
- Correct status semantics:
  - **401 Unauthorized**: missing, invalid, expired token or bad login credentials
  - **403 Forbidden**: valid identity, but the account is inactive
- Persistent SQLite database through SQLAlchemy 2.x
- Automated tests covering success and failure paths
- Interactive Swagger documentation at `/docs`

## Run locally

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Set a secret before running. In PowerShell:

```powershell
$env:AUTH_SECRET_KEY = "replace-this-with-a-long-random-secret"
uvicorn app.main:app --reload
```

On macOS/Linux:

```bash
export AUTH_SECRET_KEY="replace-this-with-a-long-random-secret"
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Quick API walkthrough

### 1. Register

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "shyam",
    "email": "shyam@example.com",
    "password": "StrongPass123!"
  }'
```

### 2. Log in

OAuth2 login uses form data rather than JSON:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=shyam&password=StrongPass123!"
```

Copy the returned `access_token`.

### 3. Call the protected route

```bash
curl http://127.0.0.1:8000/protected \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Demonstrate a real 403

Deactivate the authenticated account:

```bash
curl -X POST http://127.0.0.1:8000/auth/deactivate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Calling `/protected` again with the same valid token now returns:

```json
{
  "detail": "User account is inactive"
}
```

with HTTP status **403 Forbidden**.

## Run tests

```bash
pytest -q
```

The suite verifies password hashing, duplicate prevention, valid login, invalid credentials, missing/invalid tokens, protected access, and inactive-user 403 behavior.

## Endpoint summary

| Method | Path | Authentication | Purpose |
|---|---|---:|---|
| GET | `/health` | No | Health check |
| POST | `/auth/register` | No | Create a user with a hashed password |
| POST | `/auth/login` | No | Return a JWT bearer token |
| GET | `/auth/me` | Yes | Return the current user |
| POST | `/auth/deactivate` | Yes | Deactivate the current account |
| GET | `/protected` | Yes | Protected assignment route |

## Deployment note

For a public submission URL, deploy the repository to a Python host such as Render, Railway, Fly.io, or another service that can run the included Dockerfile. Set `AUTH_SECRET_KEY` as a secret environment variable. SQLite is suitable for this assignment demo; for a multi-instance production deployment, switch `DATABASE_URL` to PostgreSQL and use migrations.
