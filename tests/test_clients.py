from http import HTTPStatus
import uuid

valid_client = {
    "name": "Maria Souza",
    "cpf": "123.456.789-09",
    "email": "maria@email.com",
    "phone": "(21) 98888-7777"
}


def test_create_client_success(client):
    response = client.post("/clients/", json=valid_client)
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["name"] == valid_client["name"]
    assert data["email"] == valid_client["email"]
    assert "id_client" in data


def test_create_client_duplicate_email(client):
    client.post("/clients/", json=valid_client)  
    duplicate = valid_client.copy()
    duplicate["cpf"] = "987.654.321-00"  
    response = client.post("/clients/", json=duplicate)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "detail" in response.json()
    assert "já cadastrado" in response.json()["detail"]


def test_get_clients(client):
    client.post("/clients/", json=valid_client)
    response = client.get("/clients/")
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0




def test_update_client(client):
    unique_email = f"test{uuid.uuid4().hex[:6]}@email.com"

    valid_client = {
        "name": "Maria Souza",
        "cpf": "327.747.950-10",
        "email": unique_email,
        "phone": "(21) 98888-7777"
    }

    post_resp = client.post("/clients/", json=valid_client)
    print("POST response:", post_resp.status_code, post_resp.json())

    assert post_resp.status_code == HTTPStatus.CREATED

    id_client = post_resp.json()["id_client"]

    update_data = {"name": "Maria Atualizada"}
    response = client.put(f"/clients/{id_client}", json=update_data)

    print("PUT response:", response.status_code, response.json())

    assert response.status_code == HTTPStatus.OK
    assert response.json()["name"] == "Maria Atualizada"


def test_delete_client_success(client):
    post_resp = client.post("/clients/", json=valid_client)
    id_client = post_resp.json()["id_client"]
    response = client.delete(f"/clients/{id_client}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id_client"] == id_client


def test_delete_client_success(client):
    unique_email = f"test{uuid.uuid4().hex[:6]}@email.com"

    valid_client = {
        "name": "Cliente Para Deletar",
        "cpf": "700.795.530-44",
        "email": unique_email,
        "phone": "(11) 99999-1234"
    }

    post_resp = client.post("/clients/", json=valid_client)
    print("POST status:", post_resp.status_code)
    print("POST response:", post_resp.json())

    assert post_resp.status_code == HTTPStatus.CREATED
    id_client = post_resp.json()["id_client"]

    delete_resp = client.delete(f"/clients/{id_client}")
    print("DELETE status:", delete_resp.status_code)
    print("DELETE response:", delete_resp.json())

    assert delete_resp.status_code == HTTPStatus.OK
    assert delete_resp.json()["id_client"] == id_client
