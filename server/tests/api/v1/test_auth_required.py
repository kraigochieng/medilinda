import re

import pytest
from fastapi.routing import APIRoute
from server.main import app

API_PREFIX = "/api/v1"


def api_routes():
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path.startswith(API_PREFIX):
            for method in sorted(route.methods - {"HEAD", "OPTIONS"}):
                yield method, route.path


ROUTES = sorted(set(api_routes()))


def test_every_api_route_was_found():
    # Guards the parametrised test below against silently testing nothing.
    assert len(ROUTES) > 40
    assert ("DELETE", "/api/v1/adrs/{id}") in ROUTES
    assert ("POST", "/api/v1/sms-messages-actions/send-individual-alert") in ROUTES


@pytest.mark.parametrize("method,path", ROUTES, ids=[f"{m} {p}" for m, p in ROUTES])
def test_route_requires_login(anon_client, method, path):
    url = re.sub(r"\{[^}]+\}", "some-id", path)

    response = anon_client.request(method, url)

    assert response.status_code == 401, (
        f"{method} {path} answered {response.status_code} without credentials"
    )


def test_bad_token_is_rejected_on_a_destructive_route(anon_client):
    response = anon_client.delete(
        f"{API_PREFIX}/adrs/some-id", headers={"Authorization": "Bearer not-a-token"}
    )
    assert response.status_code == 401


def test_bad_api_key_is_rejected_on_a_destructive_route(anon_client, monkeypatch):
    from server.utils import auth as auth_utils

    class NoKeyHttp:
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
                    return {"valid": False, "key": None}

            return Response()

    monkeypatch.setattr(auth_utils.httpx, "AsyncClient", NoKeyHttp)

    response = anon_client.delete(
        f"{API_PREFIX}/adrs/some-id", headers={"x-api-key": "wrong"}
    )
    assert response.status_code == 401
