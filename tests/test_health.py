from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_health_endpoint_reports_service_identity() -> None:
    client = TestClient(create_app())
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "shamba-signal-api",
        "release": "slice-2-annual-target-v1",
    }


def test_health_and_platform_status_share_release_identity() -> None:
    client = TestClient(create_app())
    assert client.get("/healthz").json()["release"] == client.get(
        "/api/v1/platform/status"
    ).json()["release"]
