# tests/test_auth.py
import pytest
from http import HTTPStatus


def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "test_user",
        "password": "test_password",
        "role": "regular"
    })
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["username"] == "test_user"
    assert data["role"] == "regular"
    assert "id_user" in data


def test_register_existing_user(client):
    response = client.post("/auth/register", json={
        "username": "test_user",
        "password": "new_pass",
        "role": "admin"
    })
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Nome de usuário já está em uso."


def test_login_valid_user(client):
    response = client.post("/auth/login", data={
        "username": "test_user",
        "password": "test_password"
    })
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post("/auth/login", data={
        "username": "test_user",
        "password": "wrong_password"
    })
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Credenciais inválidas."


def test_refresh_token_valid(client):
    login_response = client.post("/auth/login", data={
        "username": "test_user",
        "password": "test_password"
    })
    refresh_token = login_response.json()["refresh_token"]

    response = client.post("/auth/refresh-token", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "access_token" in data
    assert data["refresh_token"] == refresh_token


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_refresh_token_invalid(client):
    response = client.post("/auth/refresh-token", json={
        "refresh_token": "invalid.token.value"
    })
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Refresh token inválido ou expirado."
