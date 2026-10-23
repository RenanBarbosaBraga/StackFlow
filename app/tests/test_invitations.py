import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.models.invitation import Invitation
from app.security import hash_invitation_token

client = TestClient(app)


def test_accept_invitation_success(client):
    # Cria a empresa e seu administrador.
    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa Convite",
            "name": "Admin",
            "email": "adminconvite@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    # Faz login como administrador.
    login = client.post(
        "/auth/login",
        json={
            "email": "adminconvite@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    assert login.status_code == 200

    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Cria o convite.
    invitation_response = client.post(
        "/invitation/",
        headers=headers,
        json={"email": "novo@stackflow.com"},
    )
    assert invitation_response.status_code == 200

    invitation_data = invitation_response.json()
    invitation_token = invitation_data["invitation_token"]
    company_id = invitation_data["company_id"]

    # Aceita o convite.
    response = client.post(
        "/public_invitation/accept",
        json={
            "token": invitation_token,
            "email": "novo@stackflow.com",
            "name": "Novo Funcionário",
            "password": "SenhaSegura456!",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Invitation accepted successfully"
    assert data["user"]["email"] == "novo@stackflow.com"
    assert data["user"]["name"] == "Novo Funcionário"
    assert data["user"]["company_id"] == company_id


def test_cannot_accept_invitation_twice(client):
    # Cria a empresa e o administrador.
    client.post(
        "/auth/register",
        json={
            "company_name": "Empresa Convite Reutilizado",
            "name": "Admin",
            "email": "adminreutilizado@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )

    login = client.post(
        "/auth/login",
        json={
            "email": "adminreutilizado@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Cria o convite.
    invitation_response = client.post(
        "/invitation/",
        headers=headers,
        json={"email": "funcionario@stackflow.com"},
    )
    assert invitation_response.status_code == 200

    invitation_token = invitation_response.json()["invitation_token"]

    payload = {
        "token": invitation_token,
        "email": "funcionario@stackflow.com",
        "name": "Funcionário",
        "password": "SenhaSegura456!",
    }

    # Primeira aceitação: deve funcionar.
    first_response = client.post(
        "/public_invitation/accept",
        json=payload,
    )
    assert first_response.status_code == 200

    # Segunda aceitação: deve ser bloqueada.
    second_response = client.post(
        "/public_invitation/accept",
        json=payload,
    )
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Invitation already accepted"


def test_cannot_accept_expired_invitation(client, db_session):
    # Cria a empresa e o administrador.
    register_response = client.post(
        "/auth/register",
        json={
            "company_name": "Empresa Convite Expirado",
            "name": "Admin",
            "email": "adminexpirado@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    assert register_response.status_code == 201

    # Faz login como administrador.
    login = client.post(
        "/auth/login",
        json={
            "email": "adminexpirado@stackflow.com",
            "password": "SenhaSegura123!",
        },
    )
    assert login.status_code == 200

    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Cria o convite.
    invitation_response = client.post(
        "/invitation/",
        headers=headers,
        json={"email": "expirado@stackflow.com"},
    )
    assert invitation_response.status_code == 200

    invitation_token = invitation_response.json()["invitation_token"]
    token_hash = hash_invitation_token(invitation_token)

    # Localiza o convite na sessão do banco de testes.
    invitation = db_session.query(Invitation).filter_by(token_hash=token_hash).first()
    assert invitation is not None

    # Define a expiração no passado.
    invitation.expires_at = datetime.datetime.now(datetime.UTC) - datetime.timedelta(
        hours=1
    )
    db_session.commit()

    # Tenta aceitar o convite expirado.
    response = client.post(
        "/public_invitation/accept",
        json={
            "token": invitation_token,
            "email": "expirado@stackflow.com",
            "name": "Funcionário",
            "password": "SenhaSegura456!",
        },
    )

    assert response.status_code == 410
    assert response.json()["detail"] == "Expired invitation"
