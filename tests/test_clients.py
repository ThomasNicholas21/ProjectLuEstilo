import pytest
from http import HTTPStatus
from fastapi.testclient import TestClient
from src.clients.models import Client
from uuid import uuid4


def create_mock_client(
    db_session,
    name="Maria Souza",
    cpf="123.456.789-09",
    email=None,
    phone="(21) 98888-7777"
):
    db_session.query(Client).delete()
    db_session.commit()
    client = Client(
        name=name,
        cpf=cpf,
        email=email or f"mock{uuid4().hex[:6]}@email.com",
        phone=phone
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


def test_create_client_success(client: TestClient):
    payload = {
        "name": "Maria Souza",
        "cpf": "123.456.789-09",
        "email": f"maria{uuid4().hex[:6]}@email.com",
        "phone": "(21) 98888-7777"
    }

    response = client.post("/clients/", json=payload)
    assert response.status_code == HTTPStatus.CREATED

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert "id_client" in data


def test_create_client_duplicate_email(client: TestClient, db_session):
    mock_client = create_mock_client(db_session)

    payload = {
        "name": "Outro Nome",
        "cpf": "987.654.321-00",
        "email": mock_client.email,
        "phone": "(11) 99999-9999"
    }

    response = client.post("/clients/", json=payload)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "detail" in response.json()
    assert "já cadastrado" in response.json()["detail"]


def test_get_clients(client: TestClient, db_session):
    create_mock_client(db_session)

    response = client.get("/clients/")
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_update_client_success(client: TestClient, db_session):
    mock_client = create_mock_client(db_session)

    update_data = {"name": "Maria Atualizada"}

    response = client.put(f"/clients/{mock_client.id_client}", json=update_data)

    assert response.status_code == HTTPStatus.OK
    assert response.json()["name"] == "Maria Atualizada"


def test_delete_client_success(client: TestClient, db_session):
    mock_client = create_mock_client(db_session)

    response = client.delete(f"/clients/{mock_client.id_client}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id_client"] == mock_client.id_client
