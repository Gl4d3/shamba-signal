from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_home_page_exposes_the_earthy_research_dashboard_shell() -> None:
    client = TestClient(create_app())
    response = client.get("/")

    assert response.status_code == 200
    assert "Shamba Signal" in response.text
    assert 'class="app-shell"' in response.text
    assert 'class="sidebar"' in response.text
    assert 'href="#overview"' in response.text
    assert 'href="#models"' in response.text
    assert 'href="#counties"' in response.text
    assert 'href="#method"' in response.text
    assert 'href="#quality"' in response.text
    assert 'id="service-status"' in response.text
    assert 'id="retry-button"' in response.text
    assert 'id="metric-mae"' in response.text
    assert 'id="metric-rmse"' in response.text
    assert 'id="county-search"' in response.text
    assert 'id="county-options"' in response.text
    assert 'id="export-county"' in response.text
    assert 'id="export-evaluation"' in response.text
    assert "provisional" in response.text.lower()
    assert "operational forecast" in response.text.lower()
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/api/v1/platform/status").status_code == 200


def test_dashboard_script_uses_real_apis_and_functional_controls() -> None:
    client = TestClient(create_app())
    script = client.get("/static/app.js").text

    assert "fetch('/api/v1/evaluation')" in script
    assert "fetch('/api/v1/platform/status')" in script
    assert "fetch('/healthz')" in script
    assert "Promise.allSettled" in script
    assert "renderModelComparison" in script
    assert "renderModelBattlecard" in script
    assert "renderCounty" in script
    assert "renderHistoryChart" in script
    assert "filterCounties" in script
    assert "downloadCountyCsv" in script
    assert "downloadEvaluationJson" in script
    assert "previous_year" in script
    assert "county_mean" in script
    assert "ridge" in script
    assert "weather_ridge" in script
    assert "IntersectionObserver" in script
    assert "private evaluation fixture" in script


def test_dashboard_styles_cover_earthy_tokens_accessibility_and_responsiveness() -> None:
    client = TestClient(create_app())
    styles = client.get("/static/styles.css").text

    assert "--forest-950" in styles
    assert "--sand-50" in styles
    assert "--olive-500" in styles
    assert ".sidebar" in styles
    assert ".hero" in styles
    assert ".model-bars" in styles
    assert ".county-workspace" in styles
    assert ":focus-visible" in styles
    assert "prefers-reduced-motion" in styles
    assert "@media (max-width: 760px)" in styles
