import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.common.database import Base, get_db
from src.main import app  


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "test_user",
        "password": "test_password",
        "role": "regular"
    })
    assert response.status_code == 201
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
    assert response.status_code == 400
    assert response.json()["detail"] == "Nome de usuário já está em uso."


def test_login_valid_user(client):
    response = client.post("/auth/login", data={
        "username": "test_user",
        "password": "test_password"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post("/auth/login", data={
        "username": "test_user",
        "password": "wrong_password"
    })
    assert response.status_code == 401
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
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["refresh_token"] == refresh_token


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_refresh_token_invalid(client):
    response = client.post("/auth/refresh-token", json={
        "refresh_token": "invalid.token.value"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token inválido ou expirado."
