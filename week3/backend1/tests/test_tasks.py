from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_repository
from app.main import app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    database_path = tmp_path / "tasks.db"
    monkeypatch.setenv("DATABASE_PATH", str(database_path))
    get_repository.cache_clear()

    with TestClient(app) as test_client:
        yield test_client

    get_repository.cache_clear()


def test_database_is_seeded_once(client: TestClient) -> None:
    first_response = client.get("/tasks")
    assert first_response.status_code == 200
    assert len(first_response.json()) == 3

    get_repository.cache_clear()

    second_response = client.get("/tasks")
    assert second_response.status_code == 200
    assert len(second_response.json()) == 3


def test_create_task_persists_after_repository_restart(client: TestClient) -> None:
    create_response = client.post("/tasks", json={"title": "Persistent task"})
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Persistent task"
    assert created["done"] is False

    get_repository.cache_clear()

    list_response = client.get("/tasks")
    assert list_response.status_code == 200
    assert any(task["id"] == created["id"] for task in list_response.json())


def test_full_crud_cycle(client: TestClient) -> None:
    create_response = client.post("/tasks", json={"title": "Write tests"})
    assert create_response.status_code == 201
    created = create_response.json()

    get_response = client.get(f"/tasks/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json() == created

    update_response = client.put(
        f"/tasks/{created['id']}",
        json={"title": "Write better tests", "done": True},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Write better tests"
    assert update_response.json()["done"] is True

    delete_response = client.delete(f"/tasks/{created['id']}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    missing_response = client.get(f"/tasks/{created['id']}")
    assert missing_response.status_code == 404
    assert missing_response.json() == {"error": "Task not found"}


def test_unknown_id_returns_404(client: TestClient) -> None:
    response = client.get("/tasks/999999")
    assert response.status_code == 404
    assert response.json() == {"error": "Task not found"}


def test_missing_or_empty_title_returns_400(client: TestClient) -> None:
    missing_title = client.post("/tasks", json={})
    assert missing_title.status_code == 400
    assert missing_title.json() == {"error": "Invalid request"}

    empty_title = client.post("/tasks", json={"title": "   "})
    assert empty_title.status_code == 400
    assert empty_title.json() == {"error": "Invalid request"}
