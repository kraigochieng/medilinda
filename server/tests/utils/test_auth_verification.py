import time

import jwt
from jwt.exceptions import PyJWKClientError
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
    last_headers: dict = {}

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, url, json, headers):
        FakeApiKeyHttp.calls += 1
        FakeApiKeyHttp.last_headers = headers

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
    assert fake_api_key_http.last_headers == {
        "x-internal-secret": settings.better_auth_internal_secret
    }


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


def test_malformed_token_is_rejected(raw_client):
    response = raw_client.get("/api/v1/users/me", headers=bearer("not-a-jwt"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_token_without_subject_is_rejected(raw_client, private_key):
    claims = {
        "aud": settings.better_auth_audience,
        "iss": settings.better_auth_url,
        "exp": int(time.time()) + 300,
    }
    token = jwt.encode(claims, private_key, algorithm="EdDSA")

    response = raw_client.get("/api/v1/users/me", headers=bearer(token))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_wrong_issuer_is_rejected(raw_client, private_key):
    token = make_token(private_key, iss="https://evil.example.com")
    response = raw_client.get("/api/v1/users/me", headers=bearer(token))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unreachable_jwks_is_rejected(raw_client, monkeypatch):
    class BrokenJwksClient:
        def get_signing_key_from_jwt(self, token):
            raise PyJWKClientError("jwks unreachable")

    monkeypatch.setattr(auth_utils, "get_jwks_client", lambda: BrokenJwksClient())

    response = raw_client.get("/api/v1/users/me", headers=bearer("a.b.c"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_bearer_token_wins_over_api_key(raw_client, db, private_key, fake_api_key_http):
    db.add(UserModel(id="ba-user-1", username="kraig", password="x"))
    db.commit()
    fake_api_key_http.payload = {"valid": True, "key": {"referenceId": "someone-else"}}

    response = raw_client.get(
        "/api/v1/users/me",
        headers={**bearer(make_token(private_key)), "x-api-key": "key-1"},
    )

    assert response.json()["id"] == "ba-user-1"
    assert fake_api_key_http.calls == 0


def test_api_key_cache_expires(raw_client, db, fake_api_key_http, monkeypatch):
    db.add(UserModel(id="owner-1", username="owner", password="x"))
    db.commit()
    fake_api_key_http.payload = {"valid": True, "key": {"referenceId": "owner-1"}}
    clock = {"now": 1000.0}
    monkeypatch.setattr(auth_utils.time, "monotonic", lambda: clock["now"])

    raw_client.get("/api/v1/users/me", headers={"x-api-key": "key-1"})
    clock["now"] += auth_utils._API_KEY_CACHE_TTL_SECONDS - 1
    raw_client.get("/api/v1/users/me", headers={"x-api-key": "key-1"})
    assert fake_api_key_http.calls == 1

    clock["now"] += 2  # past the 60 second window
    raw_client.get("/api/v1/users/me", headers={"x-api-key": "key-1"})
    assert fake_api_key_http.calls == 2


def test_revoked_key_is_rejected_after_cache_expires(
    raw_client, db, fake_api_key_http, monkeypatch
):
    db.add(UserModel(id="owner-1", username="owner", password="x"))
    db.commit()
    clock = {"now": 1000.0}
    monkeypatch.setattr(auth_utils.time, "monotonic", lambda: clock["now"])

    fake_api_key_http.payload = {"valid": True, "key": {"referenceId": "owner-1"}}
    assert raw_client.get("/api/v1/users/me", headers={"x-api-key": "k"}).status_code == 200

    fake_api_key_http.payload = {"valid": False, "key": None, "error": {}}
    clock["now"] += auth_utils._API_KEY_CACHE_TTL_SECONDS + 1
    assert raw_client.get("/api/v1/users/me", headers={"x-api-key": "k"}).status_code == 401


def test_invalid_api_key_is_not_cached(raw_client, fake_api_key_http):
    fake_api_key_http.payload = {"valid": False, "key": None, "error": {}}

    raw_client.get("/api/v1/users/me", headers={"x-api-key": "bad"})
    raw_client.get("/api/v1/users/me", headers={"x-api-key": "bad"})

    assert fake_api_key_http.calls == 2


def test_auth_service_outage_returns_503(raw_client, monkeypatch):
    class DownHttp:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def post(self, url, json, headers):
            raise auth_utils.httpx.ConnectError("down")

    monkeypatch.setattr(auth_utils.httpx, "AsyncClient", DownHttp)

    response = raw_client.get("/api/v1/users/me", headers={"x-api-key": "k"})

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_non_json_reply_from_auth_service_returns_503(raw_client, monkeypatch):
    class HtmlHttp:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def post(self, url, json, headers):
            class Response:
                @staticmethod
                def json():
                    raise ValueError("not json")

            return Response()

    monkeypatch.setattr(auth_utils.httpx, "AsyncClient", HtmlHttp)

    response = raw_client.get("/api/v1/users/me", headers={"x-api-key": "k"})

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_new_users_get_distinct_placeholder_passwords(raw_client, db, private_key):
    for sub, name in [("ba-1", "one"), ("ba-2", "two")]:
        token = make_token(private_key, sub=sub, username=name)
        assert raw_client.get("/api/v1/users/me", headers=bearer(token)).status_code == 200

    passwords = [u.password for u in db.query(UserModel).all()]
    assert len(set(passwords)) == 2


def post_institution(client, headers):
    return client.post(
        "/api/v1/medical-institutions/",
        json={"name": "Audit Hospital", "mfl_code": "AUD-1"},
        headers=headers,
    )


def audit_rows(db, entity_type):
    from server.models.audit_log import AuditLogModel

    return db.query(AuditLogModel).filter_by(entity_type=entity_type).all()


def test_changes_made_with_a_token_are_recorded_against_that_user(
    raw_client, db, private_key
):
    response = post_institution(raw_client, bearer(make_token(private_key)))

    assert response.status_code == status.HTTP_201_CREATED
    (row,) = audit_rows(db, "medical_institution")
    assert (row.action, row.entity_id) == ("create", response.json()["id"])
    assert (row.actor_id, row.actor_username) == ("ba-user-1", "kraig")
    assert row.snapshot["name"] == "Audit Hospital"


def test_changes_made_with_an_api_key_are_recorded_against_the_key_owner(
    raw_client, db, fake_api_key_http
):
    db.add(UserModel(id="owner-1", username="owner", password="x"))
    db.commit()
    fake_api_key_http.payload = {"valid": True, "key": {"referenceId": "owner-1"}}

    response = post_institution(raw_client, {"x-api-key": "key-1"})

    assert response.status_code == status.HTTP_201_CREATED
    (row,) = audit_rows(db, "medical_institution")
    assert (row.actor_id, row.actor_username) == ("owner-1", "owner")


def test_each_request_gets_its_own_audit_group(raw_client, db, private_key):
    headers = bearer(make_token(private_key))
    post_institution(raw_client, headers)
    raw_client.post(
        "/api/v1/medical-institutions/",
        json={"name": "Second", "mfl_code": "AUD-2"},
        headers=headers,
    )

    groups = {row.group_id for row in audit_rows(db, "medical_institution")}
    assert len(groups) == 2
