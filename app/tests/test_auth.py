from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_docs_are_avaliable():
    response = client.get("/docs")

    assert response.status_code == 200


def test_login_success(client):
    # Primeiro, cadastra um usuário de teste.
    register_response = client.post(
        "/auth/register",
        json={
            "company_name": "Empresa Teste",
            "name": "Usuário Teste",
            "email": "teste@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    assert register_response.status_code == 201

    # Agora, tenta fazer login com as credenciais corretas.
    login_response = client.post(
        "/auth/login",
        json={
            "email": "teste@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa Senha Errada",
            "name": "Usuário Teste",
            "email": "senhaerrada@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "senhaerrada@stackflow.com",
            "password": "SenhaIncorreta456!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_nonexistent_email(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "naoexiste@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
