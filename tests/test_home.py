from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_home_page_describes_current_boundary_and_loads_dependencies() -> None:
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert "Shamba Signal" in response.text
    assert "No farm-level yield prediction" in response.text
    assert "Slice 2 source acquisition is blocked" in response.text
    assert "Maize is the metadata-selected crop" in response.text
    assert "No official source snapshot has passed" in response.text
    assert "Official source acquisition is currently blocked" in response.text
    assert "Foundation shell implemented" not in response.text
    assert "Data feasibility is next" not in response.text
    assert "no downloaded canonical target dataset" in response.text.lower()
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/api/v1/platform/status").status_code == 200


def test_status_script_surfaces_a_blocked_capability_before_the_next_capability() -> None:
    client = TestClient(create_app())
    script = client.get("/static/app.js").text
    assert ".find(" in script
    assert "capability.status === 'blocked'" in script
    assert "capability.status === 'next'" in script
    assert "capabilities[0]" not in script
    assert "temporarily unavailable" in script
