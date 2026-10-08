import pytest
from fastapi import status

# Every dashboard route, with the query or path parameters it needs.
DASHBOARD_ROUTES = [
    ("/summary", {}),
    ("/reviewed-unreviewed", {}),
    ("/causality-distribution", {}),
    ("/approval-status", {}),
    ("/categorical-field/patient_gender", {}),
    ("/top-institutions", {}),
    ("/adrs-weekly", {}),
    ("/adrs-monthly", {}),
    ("/adr-monitoring", {"start": "2025-01-01", "end": "2025-12-31"}),
    ("/sms-summary", {}),
    ("/sms-status", {}),
    ("/sms-type", {}),
    ("/sms-weekly", {}),
    ("/sms-monthly", {}),
    ("/sms-monthly/individual-alert", {}),
    ("/sms-monthly/additional-info", {}),
]


@pytest.mark.parametrize(
    "path,params", DASHBOARD_ROUTES, ids=[path for path, _ in DASHBOARD_ROUTES]
)
def test_dashboard_endpoint_responds_on_an_empty_database(client, path, params):
    response = client.get(f"/api/v1/dashboard{path}", params=params)

    assert response.status_code == status.HTTP_200_OK, response.text


def test_summary_counts_adrs(client):
    response = client.get("/api/v1/dashboard/summary")

    assert response.json() == {"total_adrs": 0, "total_institutions": 0}


def test_every_dashboard_route_is_covered():
    from fastapi.routing import APIRoute
    from server.main import app

    actual = {
        route.path.removeprefix("/api/v1/dashboard")
        for route in app.routes
        if isinstance(route, APIRoute) and route.path.startswith("/api/v1/dashboard")
    }
    covered = {path.replace("patient_gender", "{field_name}") for path, _ in DASHBOARD_ROUTES}

    assert actual == covered
