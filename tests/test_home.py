from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_home_page_describes_the_weather_no_go_and_loads_dependencies() -> None:
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert "Shamba Signal" in response.text
    assert "Weather adds signal." in response.text
    assert "Not enough to win." in response.text
    assert "data-model-metrics" in response.text
    assert "county-selector" in response.text
    assert "Retrospective county-year evidence only" in response.text
    assert "Slice 2A annual snapshot is ready" not in response.text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/api/v1/platform/status").status_code == 200


def test_dashboard_script_loads_evaluation_and_renders_weather_comparison() -> None:
    client = TestClient(create_app())
    script = client.get("/static/app.js").text
    assert "fetch('/api/v1/evaluation')" in script
    assert "weather_ridge" in script
    assert "county-selector" in script
    assert "private evaluation fixture" in script
