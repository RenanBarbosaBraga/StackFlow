from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_company_cannot_delete_another_company_product(client):
    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa A",
            "name": "Admin A",
            "email": "admina@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    login_a = client.post(
        "/auth/login",
        json={
            "email": "admina@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    token_a = login_a.json()["access_token"]

    product_response = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "name": "Teclado Gamer",
            "price": 150.0,
            "quantity": 10,
        },
    )
    assert product_response.status_code == 200
    product_id = product_response.json()["products"]["id"]

    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa B",
            "name": "Admin B",
            "email": "adminb@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    login_b = client.post(
        "/auth/login",
        json={
            "email": "adminb@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    token_b = login_b.json()["access_token"]

    response = client.delete(
        f"/products/{product_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404

    check_product = client.get(
        f"/products/{product_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert check_product.status_code == 200
    assert check_product.json()["name"] == "Teclado Gamer"


def test_patch_updates_only_provided_fields(client):
    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa Patch",
            "name": "Admin Patch",
            "email": "patch@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    login = client.post(
        "/auth/login",
        json={
            "email": "patch@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/products/",
        headers=headers,
        json={
            "name": "Teclado Gamer",
            "price": 150.0,
            "quantity": 10,
        },
    )
    assert created.status_code == 200
    product_id = created.json()["products"]["id"]

    response = client.patch(
        f"/products/{product_id}",
        headers=headers,
        json={"price": 179.90},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Teclado Gamer"
    assert response.json()["price"] == 179.90
    assert response.json()["quantity"] == 10


def test_company_cannot_patch_another_company_product(client):
    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa Patch A",
            "name": "Admin A",
            "email": "patcha@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    login_a = client.post(
        "/auth/login",
        json={
            "email": "patcha@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    created = client.post(
        "/products/",
        headers=headers_a,
        json={
            "name": "Monitor",
            "price": 800.0,
            "quantity": 5,
        },
    )
    assert created.status_code == 200
    product_id = created.json()["products"]["id"]

    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa Patch B",
            "name": "Admin B",
            "email": "patchb@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    login_b = client.post(
        "/auth/login",
        json={
            "email": "patchb@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    response = client.patch(
        f"/products/{product_id}",
        headers=headers_b,
        json={"price": 0.01},
    )

    assert response.status_code == 404

    check = client.get(
        f"/products/{product_id}",
        headers=headers_a,
    )

    assert check.status_code == 200
    assert check.json()["name"] == "Monitor"
    assert check.json()["price"] == 800.0
    assert check.json()["quantity"] == 5


def test_company_cannot_get_another_company_product(client):
    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa Consulta A",
            "name": "Admin Consulta A",
            "email": "consulta.a@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    login_a = client.post(
        "/auth/login",
        json={
            "email": "consulta.a@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    created = client.post(
        "/products/",
        headers=headers_a,
        json={
            "name": "Notebook Empresarial",
            "price": 3500.0,
            "quantity": 3,
        },
    )

    assert created.status_code == 200
    product_id = created.json()["products"]["id"]

    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa Consulta B",
            "name": "Admin Consulta B",
            "email": "consulta.b@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    login_b = client.post(
        "/auth/login",
        json={
            "email": "consulta.b@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    response = client.get(
        f"/products/{product_id}",
        headers=headers_b,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

    owner_response = client.get(
        f"/products/{product_id}",
        headers=headers_a,
    )

    assert owner_response.status_code == 200
    assert owner_response.json()["name"] == "Notebook Empresarial"


def test_list_products_returns_only_current_company_products(client):
    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa Lista A",
            "name": "Admin Lista A",
            "email": "listaa@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    login_a = client.post(
        "/auth/login",
        json={
            "email": "listaa@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    assert login_a.status_code == 200

    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa Lista B",
            "name": "Admin Lista B",
            "email": "listab@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    login_b = client.post(
        "/auth/login",
        json={
            "email": "listab@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    assert login_b.status_code == 200

    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    product_a = client.post(
        "/products/",
        headers=headers_a,
        json={
            "name": "Teclado da Empresa A",
            "price": 150.0,
            "quantity": 10,
        },
    )
    assert product_a.status_code == 200

    product_b = client.post(
        "/products/",
        headers=headers_b,
        json={
            "name": "Mouse da Empresa B",
            "price": 80.0,
            "quantity": 5,
        },
    )
    assert product_b.status_code == 200

    response = client.get(
        "/products/",
        headers=headers_a,
    )

    assert response.status_code == 200

    products = response.json()
    product_names = [product["name"] for product in products]

    assert "Teclado da Empresa A" in product_names
    assert "Mouse da Empresa B" not in product_names
    assert len(products) == 1
