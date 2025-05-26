import pytest
from http import HTTPStatus
from src.auth.models import User
from src.auth.security.token import get_password_hash


def create_mock_user(db_session):
    db_session.query(User).delete()
    db_session.commit()
    user = User(
        username="test_user",
        password=get_password_hash("test_password"),
        role="regular"
    )
    db_session.add(user)
    db_session.commit()


def test_register_user_success(client):
    response = client.post("/auth/register", json={
        "username": "new_user",
        "password": "new_password",
        "role": "regular"
    })

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["username"] == "new_user"
    assert data["role"] == "regular"
    assert "id_user" in data


def test_register_user_already_exists(client, db_session):
    create_mock_user(db_session)

    response = client.post("/auth/register", json={
        "username": "test_user",
        "password": "test_password",
        "role": "regular"
    })

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Nome de usuário já existe."


def test_login_user_success(client, db_session):
    create_mock_user(db_session)

    response = client.post("/auth/login", data={
        "username": "test_user",
        "password": "test_password"
    })

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_user_invalid_credentials(client, db_session):
    create_mock_user(db_session)

    response = client.post("/auth/login", data={
        "username": "test_user",
        "password": "wrong_password"
    })

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Credenciais inválidas."


def test_refresh_token_success(client, db_session):
    create_mock_user(db_session)
    
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


def test_refresh_token_invalid(client):
    response = client.post("/auth/refresh-token", json={
        "refresh_token": "invalid.token.value"
    })

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Refresh token inválido ou expirado."
