from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models import User


USER = {
    "username": "shyam",
    "email": "shyam@example.com",
    "password": "StrongPass123!",
}


def register(client: TestClient) -> None:
    response = client.post("/auth/register", json=USER)
    assert response.status_code == 201, response.text


def login(client: TestClient) -> str:
    response = client.post(
        "/auth/login",
        data={"username": USER["username"], "password": USER["password"]},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_registration_hashes_password(client: TestClient) -> None:
    register(client)

    app = client.app
    with app.state.session_factory() as session:
        user = session.scalar(select(User).where(User.username == USER["username"]))
        assert user is not None
        assert user.hashed_password != USER["password"]
        assert USER["password"] not in user.hashed_password


def test_duplicate_registration_returns_409(client: TestClient) -> None:
    register(client)
    response = client.post("/auth/register", json=USER)
    assert response.status_code == 409


def test_login_returns_bearer_token(client: TestClient) -> None:
    register(client)
    response = client.post(
        "/auth/login",
        data={"username": USER["email"], "password": USER["password"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_in"] == 1800


def test_wrong_password_returns_401(client: TestClient) -> None:
    register(client)
    response = client.post(
        "/auth/login",
        data={"username": USER["username"], "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_protected_route_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/protected")
    assert response.status_code == 401


def test_protected_route_with_invalid_token_returns_401(client: TestClient) -> None:
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )
    assert response.status_code == 401


def test_logged_in_user_can_access_protected_route(client: TestClient) -> None:
    register(client)
    token = login(client)
    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == USER["username"]


def test_inactive_user_receives_403(client: TestClient) -> None:
    register(client)
    token = login(client)
    headers = {"Authorization": f"Bearer {token}"}

    deactivate_response = client.post("/auth/deactivate", headers=headers)
    assert deactivate_response.status_code == 200

    protected_response = client.get("/protected", headers=headers)
    assert protected_response.status_code == 403
    assert protected_response.json()["detail"] == "User account is inactive"

    login_response = client.post(
        "/auth/login",
        data={"username": USER["username"], "password": USER["password"]},
    )
    assert login_response.status_code == 403
