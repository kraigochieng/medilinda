import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import status
from fastapi.testclient import TestClient
from server.dependencies import get_db
from server.main import app
from server.models.user import UserModel
from server.settings import settings
from server.utils import auth as auth_utils


class FakeSigningKey:
    def __init__(self, key):
        self.key = key


class FakeJwksClient:
    def __init__(self, public_key):
        self.public_key = public_key

    def get_signing_key_from_jwt(self, token):
        return FakeSigningKey(self.public_key)


@pytest.fixture
def private_key():
    return Ed25519PrivateKey.generate()


@pytest.fixture
def raw_client(db, private_key, monkeypatch):
    """Client using the real auth dependency (no override)."""
    monkeypatch.setattr(
        auth_utils, "get_jwks_client", lambda: FakeJwksClient(private_key.public_key())
    )
    auth_utils._api_key_cache.clear()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def make_token(private_key, **overrides):
    claims = {
        "sub": "ba-user-1",
        "username": "kraig",
        "first_name": "Kraig",
        "last_name": "Ochieng",
        "aud": settings.better_auth_audience,
        "iss": settings.better_auth_url,
        "exp": int(time.time()) + 300,
    }
    claims.update(overrides)
    return jwt.encode(claims, private_key, algorithm="EdDSA")


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_valid_jwt_creates_local_user(raw_client, db, private_key):
    response = raw_client.get(
        "/api/v1/users/me", headers=bearer(make_token(private_key))
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == "ba-user-1"
    assert response.json()["username"] == "kraig"
    assert db.query(UserModel).filter(UserModel.id == "ba-user-1").count() == 1


def test_valid_jwt_reuses_existing_local_user(raw_client, db, private_key):
    db.add(
        UserModel(
            id="ba-user-1",
            username="legacy-name",
            password="x",
            first_name="Old",
            last_name="User",
        )
    )
    db.commit()

    response = raw_client.get(
        "/api/v1/users/me", headers=bearer(make_token(private_key))
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "legacy-name"
    assert db.query(UserModel).count() == 1


def test_expired_jwt_is_rejected(raw_client, private_key):
    token = make_token(private_key, exp=int(time.time()) - 10)
    response = raw_client.get("/api/v1/users/me", headers=bearer(token))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_jwt_signed_with_other_key_is_rejected(raw_client):
    token = make_token(Ed25519PrivateKey.generate())
    response = raw_client.get("/api/v1/users/me", headers=bearer(token))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_jwt_with_wrong_audience_is_rejected(raw_client, private_key):
    token = make_token(private_key, aud="someone-else")
    response = raw_client.get("/api/v1/users/me", headers=bearer(token))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_missing_credentials_are_rejected(raw_client):
    response = raw_client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_disabled_user_is_rejected(raw_client, db, private_key):
    db.add(UserModel(id="ba-user-1", username="kraig", password="x", disabled=True))
    db.commit()

    response = raw_client.get(
        "/api/v1/users/me", headers=bearer(make_token(private_key))
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


class FakeApiKeyHttp:
    """Stands in for httpx.AsyncClient when calling Better Auth."""

    calls = 0
    payload: dict = {}

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, url, json):
        FakeApiKeyHttp.calls += 1

        class Response:
            @staticmethod
            def json():
                return FakeApiKeyHttp.payload

        return Response()


@pytest.fixture
def fake_api_key_http(monkeypatch):
    FakeApiKeyHttp.calls = 0
    monkeypatch.setattr(auth_utils.httpx, "AsyncClient", FakeApiKeyHttp)
    return FakeApiKeyHttp


def test_valid_api_key_authenticates(raw_client, db, fake_api_key_http):
    db.add(UserModel(id="owner-1", username="owner", password="x"))
    db.commit()
    fake_api_key_http.payload = {"valid": True, "key": {"referenceId": "owner-1"}}

    response = raw_client.get("/api/v1/users/me", headers={"x-api-key": "key-1"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == "owner-1"


def test_invalid_api_key_is_rejected(raw_client, fake_api_key_http):
    fake_api_key_http.payload = {"valid": False, "key": None, "error": {}}

    response = raw_client.get("/api/v1/users/me", headers={"x-api-key": "bad"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_valid_api_key_result_is_cached(raw_client, db, fake_api_key_http):
    db.add(UserModel(id="owner-1", username="owner", password="x"))
    db.commit()
    fake_api_key_http.payload = {"valid": True, "key": {"referenceId": "owner-1"}}

    raw_client.get("/api/v1/users/me", headers={"x-api-key": "key-1"})
    raw_client.get("/api/v1/users/me", headers={"x-api-key": "key-1"})

    assert fake_api_key_http.calls == 1
