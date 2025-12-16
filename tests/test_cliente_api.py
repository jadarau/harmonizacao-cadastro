import pytest
from fastapi.testclient import TestClient
from app.main import app


def make_cliente(nome="João", emails=None, tels=None, enderecos=None):
    return {
        "nome": nome,
        "telefone": tels or ["11999999999"],
        "email": emails or ["joao@example.com"],
        "nascimento": "1990-01-01",
        "origem": "website",
        "classificacao": "morno",
        "enderecos": enderecos or [
            {
                "logradouro": "Rua A",
                "numero": "100",
                "complemento": None,
                "bairro": "Centro",
                "cidade": "SP",
                "estado": "SP",
                "cep": "01001000",
                "tipo": "residencial"
            }
        ]
    }


@pytest.mark.asyncio
async def test_upsert_new_client(monkeypatch):
    class FakeRepo:
        async def find_by_email_or_phone(self, emails, telefones):
            return None

        async def create(self, cliente):
            return "abc123"

    def get_repo():
        return FakeRepo()

    app.dependency_overrides = {}
    from app.database.deps import get_cliente_repository
    app.dependency_overrides[get_cliente_repository] = get_repo

    client = TestClient(app)
    resp = client.post("/v1/cliente/formulario", json=make_cliente())
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "success"
    assert data["message"].startswith("Cliente criado")


@pytest.mark.asyncio
async def test_upsert_existing_by_email_add_phone_and_address(monkeypatch):
    existing = {
        "id": "abc123",
        "nome": "João",
        "telefone": ["11911111111"],
        "email": ["joao@example.com"],
        "nascimento": "1990-01-01",
        "origem": "website",
        "classificacao": "morno",
        "enderecos": [
            {
                "logradouro": "Rua A",
                "numero": "100",
                "complemento": None,
                "bairro": "Centro",
                "cidade": "SP",
                "estado": "SP",
                "cep": "01001000",
                "tipo": "residencial"
            }
        ]
    }

    calls = {"updated": False}

    class FakeRepo:
        async def find_by_email_or_phone(self, emails, telefones):
            if "joao@example.com" in emails:
                return existing
            return None

        async def update_add_fields(self, **kwargs):
            calls["updated"] = True
            return True

        async def create(self, cliente):
            raise AssertionError("Should not create on existing")

    def get_repo():
        return FakeRepo()

    app.dependency_overrides = {}
    from app.database.deps import get_cliente_repository
    app.dependency_overrides[get_cliente_repository] = get_repo

    client = TestClient(app)
    payload = make_cliente(
        emails=["joao@example.com"],
        tels=["11911111111", "11922222222"],
        enderecos=[
            existing["enderecos"][0],
            {
                "logradouro": "Rua B",
                "numero": "200",
                "complemento": None,
                "bairro": "Centro",
                "cidade": "SP",
                "estado": "SP",
                "cep": "01002000",
                "tipo": "residencial"
            }
        ],
    )
    resp = client.post("/v1/cliente/formulario", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["message"].startswith("Cliente atualizado")
    assert calls["updated"] is True
