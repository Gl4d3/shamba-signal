from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_home_page_describes_current_boundary_and_loads_dependencies() -> None:
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert "Shamba Signal" in response.text
    assert "No season labels, forecast, or decision support" in response.text
    assert "crop-stress" not in response.text
    assert "advisory" not in response.text
    assert "Slice 2A annual snapshot is ready" in response.text
    assert "source-bound and not model-ready" in response.text
    assert "Slice 2B official annual label reconciliation is next" in response.text
    assert "conflicting official 2020 vintages" in response.text
    assert "county-year baseline feasibility" in response.text
    assert "Foundation shell implemented" not in response.text
    assert "Data feasibility is next" not in response.text
    assert "No season labels, forecast, or decision support" in response.text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/api/v1/platform/status").status_code == 200


def test_status_script_surfaces_the_current_capability_before_the_next_capability() -> None:
    client = TestClient(create_app())
    script = client.get("/static/app.js").text
    assert ".find(" in script
    assert "capability.status === 'ready'" in script
    assert "capability.id === 'annual-snapshot'" in script
    assert "capability.status === 'next'" in script
    assert "capabilities[0]" not in script
    assert "temporarily unavailable" in script
