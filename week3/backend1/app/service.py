from app.models import Task, TaskCreate, TaskUpdate
from app.repositories.interface import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def list_tasks(self) -> list[Task]:
        return self.repository.list_all()

    def get_task(self, task_id: int) -> Task | None:
        return self.repository.get_by_id(task_id)

    def create_task(self, task: TaskCreate) -> Task:
        return self.repository.create(task)

    def update_task(
        self,
        task_id: int,
        task: TaskUpdate,
    ) -> Task | None:
        return self.repository.update(task_id, task)

    def delete_task(self, task_id: int) -> bool:
        return self.repository.delete(task_id)