# FlyRank W3 A2 Stage Checklist

## Stage 0 — Create your database
- [x] `tasks.db` is created automatically.
- [x] `tasks` table is created automatically.
- [x] Columns: `id`, `title`, `done`.
- [x] Three seed tasks are inserted only when the table is empty.
- [x] Seeding is wrapped in the SQLite connection transaction.

## Stage 1 — Read from the database
- [x] `GET /tasks` reads with SQL.
- [x] `GET /tasks/{id}` uses `WHERE id = ?`.
- [x] Unknown IDs return `404` and `{ "error": "Task not found" }`.

## Stage 2 — Create new tasks
- [x] `POST /tasks` uses a parameterized `INSERT`.
- [x] Missing/empty title returns `400`.
- [x] Successful create returns `201`.
- [x] Data persists in SQLite.

## Stage 3 — Update and delete
- [x] `PUT /tasks/{id}` uses parameterized `UPDATE`.
- [x] `DELETE /tasks/{id}` uses parameterized `DELETE`.
- [x] Delete success returns `204` with no body.
- [x] Unknown IDs return `404`.

## Stage 4 — SQL by hand
- [x] README documents the required SQL queries.
- [ ] Run the queries yourself in DB Browser for SQLite before submission.

## Stage 5 — Publish
- [x] README explains why SQLite was chosen.
- [x] README explains where `tasks.db` lives.
- [x] README contains setup/start instructions.
- [x] README includes an example SQL query.
- [ ] Add your real DB Browser screenshot.
- [ ] Commit each stage in your existing Git repository.
- [ ] Push the repository publicly to GitHub.

## Bonus Stage 6
- [ ] Optional — AI rematch is not included because the assignment says the hand-built Stages 0–5 version should remain the submission and the AI version must be isolated in its own folder/branch.
