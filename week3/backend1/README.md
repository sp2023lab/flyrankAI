# FlyRank Backend AI Engineering - Week 3 A2

## Connecting Your CRUD to the Database

This project implements the FlyRank Week 3 assignment by moving a task CRUD API from in-memory storage to a real **SQLite** database while keeping the API contract stable.

The key architecture is:

```text
Client -> FastAPI routes -> Service -> Repository -> SQLite (tasks.db)
```

The API describes what the application does; SQLite is only the persistence layer underneath it.

## Technologies

- Python 3.10+
- FastAPI
- Pydantic
- SQLite via Python's built-in `sqlite3` module
- Uvicorn
- Pytest

## Why SQLite?

SQLite was chosen because it is lightweight, stores the entire database in a single file, requires no separate database server, and is included with Python. It also gives the project persistence, so tasks remain available after the API process stops and restarts.

## Project Structure

```text
flyrank-w3-a2/
├── app/
│   ├── repositories/
│   │   ├── interface.py
│   │   └── sqlite_repository.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   └── service.py
├── docs/
│   └── DATABASE_SCREENSHOT.md
├── tests/
│   └── test_tasks.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Database

The database file is:

```text
tasks.db
```

It is created automatically in the project root the first time the application accesses the repository. The file is intentionally listed in `.gitignore`, so a clean clone creates its own database automatically.

The application also creates the `tasks` table if it does not already exist:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
);
```

When the table is empty, exactly three starter tasks are inserted. The repository checks `SELECT COUNT(*) FROM tasks` before seeding, so restarting the application does not duplicate them.

## Setup and Run

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app.main:app --reload
```

The API is available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Purpose | Success |
|---|---|---|---|
| GET | `/tasks` | List all tasks | `200` |
| GET | `/tasks/{id}` | Get one task | `200` |
| POST | `/tasks` | Create a task | `201` |
| PUT | `/tasks/{id}` | Update a task | `200` |
| DELETE | `/tasks/{id}` | Delete a task | `204` |

Unknown task IDs return:

```json
{
  "error": "Task not found"
}
```

with status `404`.

Invalid request bodies return:

```json
{
  "error": "Invalid request"
}
```

with status `400`.

## Example Requests

List tasks:

```bash
curl -i http://127.0.0.1:8000/tasks
```

Create a task:

```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
```

Update a task:

```bash
curl -i -X PUT http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","done":true}'
```

Delete a task:

```bash
curl -i -X DELETE http://127.0.0.1:8000/tasks/1
```

## Persistence Check

1. Start the API.
2. Create a task with `POST /tasks`.
3. Confirm it appears in `GET /tasks`.
4. Stop Uvicorn.
5. Start Uvicorn again.
6. Run `GET /tasks` again.
7. The task is still present because it was stored in `tasks.db`, not in Python memory.

## SQL Explored by Hand

Example query used in Stage 4:

```sql
SELECT * FROM tasks WHERE done = 1;
```

This returns only tasks whose `done` value is `1`, meaning the task is completed.

Other assignment queries:

```sql
SELECT * FROM tasks;
SELECT COUNT(*) FROM tasks;
UPDATE tasks SET done = 1;
DELETE FROM tasks WHERE done = 1;
```

After changing the database manually, `GET /tasks` reads the same database file, so the API reflects those changes immediately.

## Database Viewer Screenshot

The assignment asks for a screenshot of `tasks.db` open in **DB Browser for SQLite**. Add your screenshot here before submission, for example:

```markdown
![SQLite tasks table](docs/database-browser.png)
```

See `docs/DATABASE_SCREENSHOT.md` for the exact steps.

## Tests

Run:

```bash
pytest
```

The tests verify:

- the database seeds exactly three tasks only once;
- `POST /tasks` creates persistent data;
- a repository restart does not lose created tasks;
- the complete create/read/update/delete cycle works;
- unknown IDs return `404`;
- missing or empty titles return `400`.

Keeping the same endpoint behaviour while changing only the storage implementation demonstrates that persistence is an implementation detail behind the API contract.

## Suggested Stage Commits

When integrating this work into the Assignment 1 repository, commit each stage separately as required by FlyRank:

```text
Stage 0: create SQLite database
Stage 1: database read endpoints
Stage 2: insert into database
Stage 3: update and delete with SQL
Stage 4: explored SQLite
Stage 5: database documentation
```

The database uses parameterized `?` placeholders for values in CRUD queries instead of concatenating user input into SQL strings.
