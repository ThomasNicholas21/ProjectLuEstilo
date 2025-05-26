import pytest
from http import HTTPStatus
from datetime import datetime, timedelta
from uuid import uuid4


def create_mock_product(db_session):
    from src.products.models import Product
    db_session.query(Product).delete()
    db_session.commit()
    unique_id = str(uuid4())
    product = Product(
        name=f"Produto {unique_id[:8]}",
        bar_code=f"BARCODE-{unique_id[:12]}",
        description="Descrição do produto de teste",
        price=100.0,
        stock=10,
        valid_date=datetime.now() + timedelta(days=365),
        images=None,
        category="geral",
        section="geral",
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def create_mock_client(db_session):
    from src.clients.models import Client
    db_session.query(Client).delete()
    db_session.commit()
    unique_id = str(uuid4())
    client = Client(
        name=f"Cliente {unique_id[:8]}",
        cpf=f"{unique_id[:11].replace('-', '')[:3]}.{unique_id[4:7]}.{unique_id[7:9]}-{unique_id[9:11]}",
        email=f"cliente{unique_id[:6]}@teste.com",
        phone="11999999999",
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


def create_mock_order(db_session, client_id, product_id):
    from src.orders.models import Order, OrderItem
    from datetime import datetime, timezone
    db_session.query(Order).delete()
    db_session.commit()
    order = Order(
        id_client=client_id,
        total_amount=2,
        total_price=200.0,
        status="pendente",
        created_at=datetime.now(timezone.utc),
        items=[
            OrderItem(id_product=product_id, amount=2, unit_price=100.0)
        ]
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


def test_create_order_success(client_with_admin, db_session):
    product = create_mock_product(db_session)
    client = create_mock_client(db_session)

    payload = {
        "id_client": client.id_client,
        "status": "pendente",
        "products": [{"id_product": product.id_product, "amount": 2}]
    }

    response = client_with_admin.post("/orders/", json=payload)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["id_order"] is not None


def test_create_order_invalid_product(client_with_admin, db_session):
    client = create_mock_client(db_session)

    payload = {
        "id_client": client.id_client,
        "status": "pendente",
        "products": [{"id_product": 9999, "amount": 1}]
    }

    response = client_with_admin.post("/orders/", json=payload)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_list_orders_success(client, db_session):
    product = create_mock_product(db_session)
    new_client = create_mock_client(db_session)

    create_mock_order(db_session, new_client.id_client, product.id_product)

    response = client.get("/orders/")
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), list)


def test_list_orders_filter_by_status(client, db_session):
    response = client.get("/orders/?status=pendente")
    assert response.status_code == HTTPStatus.OK


def test_list_orders_filter_by_client(client, db_session):
    new_client = create_mock_client(db_session)

    response = client.get(f"/orders/?id_client={new_client.id_client}")
    assert response.status_code == HTTPStatus.OK


def test_list_orders_with_date_range(client):
    response = client.get("/orders/?start_date=2020-01-01T00:00:00Z&end_date=2030-01-01T00:00:00Z")
    assert response.status_code == HTTPStatus.OK


def test_get_order_by_id_success(client, db_session):
    product = create_mock_product(db_session)
    new_client = create_mock_client(db_session)
    order = create_mock_order(db_session, new_client.id_client, product.id_product)

    response = client.get(f"/orders/{order.id_order}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id_order"] == order.id_order


def test_get_order_by_id_not_found(client):
    response = client.get("/orders/99999")

    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert "Pedido ID 99999 não encontrado" in data["detail"]


def test_update_order_success(client_with_admin, db_session):
    product = create_mock_product(db_session)
    client_obj = create_mock_client(db_session)
    order = create_mock_order(db_session, client_obj.id_client, product.id_product)
    new_product = create_mock_product(db_session)
    
    payload = {
        "status": "pago",
        "products": [{"id_product": new_product.id_product, "amount": 1}]
    }

    response = client_with_admin.put(f"/orders/{order.id_order}", json=payload)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["status"] == "pago"
    assert data["total_amount"] == 1
    assert data["total_price"] == new_product.price * 1


def test_update_order_not_found(client_with_admin):
    response = client_with_admin.put("/orders/9999", json={"status": "pago"})
    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert "Pedido ID 9999 não encontrado" in data["detail"]


def test_delete_order_success(client_with_admin, db_session):
    product = create_mock_product(db_session)
    client = create_mock_client(db_session)
    order = create_mock_order(db_session, client.id_client, product.id_product)

    response = client_with_admin.delete(f"/orders/{order.id_order}")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id_order"] == order.id_order


def test_delete_order_not_found(client_with_admin):
    response = client_with_admin.delete("/orders/9999")
    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert "Pedido ID 9999 não encontrado" in data["detail"]
