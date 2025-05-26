import io
import uuid
from datetime import date
from http import HTTPStatus
from src.products.models import Product


def create_mock_products(db_session):
    db_session.query(Product).delete()
    db_session.commit()

    db_session.add_all([
        Product(
            name="Notebook",
            bar_code=str(uuid.uuid4())[:13],
            price=2500.00,
            stock=5,
            category="Eletrônicos",
            section="Informática",
            valid_date=date(2025, 12, 31)
        ),
        Product(
            name="Fone Bluetooth",
            bar_code=str(uuid.uuid4())[:13],
            price=299.90,
            stock=0,
            category="Eletrônicos",
            section="Áudio",
            valid_date=date(2025, 12, 31)
        ),
        Product(
            name="Tênis Esportivo",
            bar_code=str(uuid.uuid4())[:13],
            price=199.90,
            stock=10,
            category="Calçados",
            section="Esportes",
            valid_date=date(2025, 12, 31)
        )
    ])
    db_session.commit()


def create_product(name, price, stock, category, section):
    return Product(
        name=name,
        bar_code=str(uuid.uuid4())[:13],
        price=price,
        stock=stock,
        category=category,
        section=section,
        valid_date=date(2025, 12, 31)
    )


def test_create_product_success(client_with_admin):
    image = io.BytesIO(b"fake image content")
    barcode = str(uuid.uuid4())[:13]

    data = {
        "name": "Tênis de Corrida",
        "bar_code": barcode,
        "description": "Um tênis muito bom",
        "price": 199.90,
        "stock": 20,
        "valid_date": "2025-12-31",
        "category": "Calçados",
        "section": "Esportes"
    }
    files = {"image": ("tenis.jpg", image, "image/jpeg")}

    response = client_with_admin.post("/products/", data=data, files=files)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["bar_code"] == barcode


def test_create_product_invalid_date(client_with_admin):
    data = {
        "name": "Produto X",
        "bar_code": "9876543210123",
        "price": 99.90,
        "stock": 10,
        "valid_date": "31/12/2025"
    }

    response = client_with_admin.post("/products/", data=data)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json()["detail"] == "Formato de data inválido. Use YYYY-MM-DD"


def test_list_all_products(client, db_session):
    create_mock_products(db_session)

    response = client.get("/products/")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 3


def test_pagination(client_with_admin):
    response = client_with_admin.get("/products/?skip=1&limit=1")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1


def test_filter_by_category(client, db_session):
    create_mock_products(db_session)

    response = client.get("/products/?category=Eletrônicos")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert all(prod["category"].lower() == "eletrônicos" for prod in data)
    assert len(data) == 2


def test_filter_by_price(client, db_session):
    create_mock_products(db_session)

    response = client.get("/products/?price=199.90")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert all(prod["price"] == 199.90 for prod in data)
    assert len(data) == 1


def test_filter_available_true(client, db_session):
    create_mock_products(db_session)

    response = client.get("/products/?available=true")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert all(prod["stock"] > 0 for prod in data)
    assert len(data) == 2


def test_filter_available_false(client, db_session):
    create_mock_products(db_session)

    response = client.get("/products/?available=false")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert all(prod["stock"] == 0 for prod in data)
    assert len(data) == 1


def test_combined_filter(client, db_session):
    create_mock_products(db_session)

    response = client.get("/products/?category=eletrônicos&available=true")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Notebook"


def test_update_product_success(client_with_admin, db_session):
    create_mock_products(db_session)
    product = db_session.query(Product).first()
    payload = {
        "price": 149,
        "stock": 25,
        "description": "Produto atualizado"
    }

    response = client_with_admin.put(f"/products/{product.id_product}", data=payload)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id_product"] == product.id_product
    assert data["price"] == 149
    assert data["stock"] == 25
    assert data["description"] == "Produto atualizado"


def test_update_product_not_found(client_with_admin):
    payload = {"price": 199.90}
    response = client_with_admin.put(f"/products/{999}", data=payload)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "não encontrado" in response.json()["detail"].lower()


def test_delete_product_success(client_with_admin, db_session):
    create_mock_products(db_session)
    product = db_session.query(Product).first()
    print(product.id_product)

    response = client_with_admin.delete(f"/products/{product.id_product}")

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id_product"] == product.id_product


def test_delete_product_not_found(client_with_admin):
    response = client_with_admin.delete("/products/9999")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "não encontrado" in response.json()["detail"].lower()
