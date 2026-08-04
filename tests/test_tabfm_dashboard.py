from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_dashboard_bootstraps_optional_tabfm_study_module() -> None:
    client = TestClient(create_app())

    bootstrap = client.get("/static/search-state.js")
    study = client.get("/static/tabfm-study.js")
    styles = client.get("/static/tabfm-study.css")

    assert bootstrap.status_code == 200
    assert "import('/static/tabfm-study.js?v=1')" in bootstrap.text
    assert study.status_code == 200
    assert styles.status_code == 200


def test_tabfm_study_renders_optional_evidence_and_unavailable_state() -> None:
    client = TestClient(create_app())
    script = client.get("/static/tabfm-study.js").text

    assert "fetch('/api/v1/tabfm-evaluation')" in script
    assert "renderTabfmStudy" in script
    assert "renderTabfmModelComparison" in script
    assert "renderTabfmFoldChart" in script
    assert "Exploratory extension" in script
    assert "2023 is post-hoc" in script
    assert "tabfm-non-commercial-v1.0" in script
    assert "Foundation model" in script
    assert "tabfm-study" in script


def test_tabfm_study_styles_are_responsive_and_accessible() -> None:
    client = TestClient(create_app())
    styles = client.get("/static/tabfm-study.css").text

    assert ".tabfm-study" in styles
    assert ".tabfm-fold-chart" in styles
    assert ":focus-visible" in styles
    assert "@media (max-width: 760px)" in styles
    assert "prefers-reduced-motion" in styles
