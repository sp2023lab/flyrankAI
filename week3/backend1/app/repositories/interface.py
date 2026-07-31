from typing import Protocol

from app.models import Task, TaskCreate, TaskUpdate


class TaskRepository(Protocol):
    def create(self, task: TaskCreate) -> Task:
        ...

    def list_all(self) -> list[Task]:
        ...

    def get_by_id(self, task_id: int) -> Task | None:
        ...

    def update(
        self,
        task_id: int,
        task: TaskUpdate,
    ) -> Task | None:
        ...

    def delete(self, task_id: int) -> bool:
        ...