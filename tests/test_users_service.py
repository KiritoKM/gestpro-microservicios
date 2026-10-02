import pytest
from fastapi.testclient import TestClient
from conftest import load_microservice

users_module = load_microservice("service_users", "users_app_module")
client = TestClient(users_module.app)


def setup_module():
    users_module.init_db()


def test_users_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "users_and_auth"
    assert data["status"] == "ok"
    assert data["port"] == 8001


def test_get_users_list():
    response = client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 2
    roles = [u["role"] for u in users]
    assert "admin" in roles
    assert "vendedor" in roles


def test_get_user_by_id():
    response = client.get("/users/1")
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == 1
    assert "username" in user
    assert "email" in user


def test_get_user_not_found():
    response = client.get("/users/999999")
    assert response.status_code == 404


def test_login_successful():
    response = client.post("/users/login", json={"username": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["user"]["role"] == "admin"
    assert "token" in data


def test_login_invalid_user():
    response = client.post("/users/login", json={"username": "usuario_inexistente"})
    assert response.status_code == 401
