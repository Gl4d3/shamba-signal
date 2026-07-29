from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_health_endpoint_reports_service_identity() -> None:
    client = TestClient(create_app())

    response = client.get('/healthz')

    assert response.status_code == 200
    assert response.json() == {
        'status': 'ok',
        'service': 'shamba-signal-api',
        'release': 'foundation-v0',
    }
