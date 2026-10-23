from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_company_cannot_delete_another_company_product(client):
    # Empresa A cria seu usuário.
    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa A",
            "name": "Admin A",
            "email": "admina@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    # Empresa A faz login.
    login_a = client.post(
        "/auth/login",
        json={
            "email": "admina@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    token_a = login_a.json()["access_token"]

    # Empresa A cria um produto.
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

    # Empresa B cria seu usuário.
    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa B",
            "name": "Admin B",
            "email": "adminb@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    # Empresa B faz login.
    login_b = client.post(
        "/auth/login",
        json={
            "email": "adminb@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    token_b = login_b.json()["access_token"]

    # Empresa B tenta excluir o produto da Empresa A.
    response = client.delete(
        f"/products/{product_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404

    # Confirma que o produto continua existindo para a Empresa A.
    check_product = client.get(
        f"/products/{product_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert check_product.status_code == 200
    assert check_product.json()["name"] == "Teclado Gamer"


def test_patch_updates_only_provided_fields(client):
    # Cria a empresa e o administrador.
    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa Patch",
            "name": "Admin Patch",
            "email": "patch@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    # Faz login.
    login = client.post(
        "/auth/login",
        json={
            "email": "patch@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Cria um produto.
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

    # Altera somente o preço.
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
    # Cria a Empresa A.
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

    # Empresa A cria um produto.
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

    # Cria a Empresa B.
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

    # Empresa B tenta alterar o preço do produto da Empresa A.
    response = client.patch(
        f"/products/{product_id}",
        headers=headers_b,
        json={"price": 0.01},
    )

    assert response.status_code == 404

    # Confirma que o produto continua intacto.
    check = client.get(
        f"/products/{product_id}",
        headers=headers_a,
    )

    assert check.status_code == 200
    assert check.json()["name"] == "Monitor"
    assert check.json()["price"] == 800.0
    assert check.json()["quantity"] == 5
