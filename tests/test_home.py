from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_home_page_describes_current_boundary_and_loads_dependencies() -> None:
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert "Shamba Signal" in response.text
    assert "No farm-level yield prediction" in response.text
    assert "no trained forecast model" in response.text.lower()
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/api/v1/platform/status").status_code == 200


def test_status_script_selects_next_capability_by_status() -> None:
    client = TestClient(create_app())
    script = client.get("/static/app.js").text
    assert ".find(" in script
    assert "capability.status === 'next'" in script
    assert "capabilities[0]" not in script
    assert "temporarily unavailable" in script
