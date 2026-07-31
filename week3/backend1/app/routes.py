from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_task_service
from app.models import Task, TaskCreate, TaskUpdate
from app.service import TaskService


router = APIRouter()


@router.get("/")
def root() -> dict[str, str]:
    return {"message": "FlyRank Week 3 SQLite CRUD API is running"}


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/tasks", response_model=list[Task])
def list_tasks(
    service: TaskService = Depends(get_task_service),
) -> list[Task]:
    return service.list_tasks()


@router.get("/tasks/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> Task:
    task = service.get_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> Task:
    return service.create_task(task)


@router.put("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> Task:
    task = service.update_task(task_id, task_update)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> None:
    deleted = service.delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
