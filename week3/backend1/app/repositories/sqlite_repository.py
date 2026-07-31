import os
import sqlite3
from pathlib import Path

from app.models import Task, TaskCreate, TaskUpdate
from app.repositories.interface import TaskRepository


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[2] / "tasks.db"


class SQLiteTaskRepository(TaskRepository):
    def __init__(self, database_path: str | Path | None = None) -> None:
        configured_path = database_path or os.getenv("DATABASE_PATH")
        self.database_path = Path(configured_path) if configured_path else DEFAULT_DATABASE_PATH
        self._initialise_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialise_database(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
                )
                """
            )

            row_count = connection.execute(
                "SELECT COUNT(*) AS count FROM tasks"
            ).fetchone()["count"]

            if row_count == 0:
                connection.executemany(
                    "INSERT INTO tasks (title, done) VALUES (?, ?)",
                    [
                        ("Learn FastAPI", 0),
                        ("Connect the API to SQLite", 0),
                        ("Test database persistence", 1),
                    ],
                )

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            done=bool(row["done"]),
        )

    def list_all(self) -> list[Task]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, title, done FROM tasks ORDER BY id"
            ).fetchall()

        return [self._row_to_task(row) for row in rows]

    def get_by_id(self, task_id: int) -> Task | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

        return self._row_to_task(row) if row else None

    def create(self, task: TaskCreate) -> Task:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                (task.title, 0),
            )
            task_id = cursor.lastrowid
            row = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

        return self._row_to_task(row)

    def update(self, task_id: int, task: TaskUpdate) -> Task | None:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
                (task.title, int(task.done), task_id),
            )

            if cursor.rowcount == 0:
                return None

            row = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

        return self._row_to_task(row)

    def delete(self, task_id: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,),
            )

        return cursor.rowcount > 0
