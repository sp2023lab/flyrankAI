from functools import lru_cache

from app.repositories.interface import TaskRepository
from app.repositories.sqlite_repository import SQLiteTaskRepository
from app.service import TaskService


@lru_cache
def get_repository() -> TaskRepository:
    return SQLiteTaskRepository()


def get_task_service() -> TaskService:
    return TaskService(get_repository())