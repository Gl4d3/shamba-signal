from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_platform_status_exposes_completed_evidence_product_contract() -> None:
    client = TestClient(create_app())
    response = client.get("/api/v1/platform/status")

    assert response.status_code == 200
    body = response.json()
    assert body["product"] == "Shamba Signal"
    assert body["release"] == "county-year-weather-evidence-v1"
    assert body["primary_output"] == "retrospective county-year maize model evidence"
    assert body["forecast_timing"] == "retrospective end-of-year backtest only"
    assert body["architecture"] == (
        "local FastAPI evidence dashboard backed by a versioned evaluation fixture"
    )
    assert body["refresh_modes"] == ["manual reproducible experiment run"]
    assert "47 Kenya counties" in body["geography"]
    assert "2023 is provisional" in body["crop_scope"]


def test_platform_status_reports_every_delivered_evidence_capability_as_ready() -> None:
    client = TestClient(create_app())
    capabilities = client.get("/api/v1/platform/status").json()["capabilities"]
    statuses = {item["id"]: item["status"] for item in capabilities}

    assert statuses == {
        "official-panel": "ready",
        "temporal-baselines": "ready",
        "weather-value-test": "ready",
        "evidence-dashboard": "ready",
    }
    weather_test = next(item for item in capabilities if item["id"] == "weather-value-test")
    assert "did not beat the county historical mean" in weather_test["outcome"]
    dashboard = next(item for item in capabilities if item["id"] == "evidence-dashboard")
    assert "predictions and errors" in dashboard["outcome"]
    assert "limitations" in dashboard["outcome"]


def test_openapi_declares_platform_status_response_schema_and_enums() -> None:
    client = TestClient(create_app())
    schema = client.get("/openapi.json").json()
    response_schema = schema["paths"]["/api/v1/platform/status"]["get"]["responses"]["200"][
        "content"
    ]["application/json"]["schema"]
    assert response_schema == {"$ref": "#/components/schemas/PlatformStatus"}
    assert schema["components"]["schemas"]["CapabilityStatus"]["enum"] == [
        "ready",
        "blocked",
        "next",
        "planned",
    ]
    assert schema["info"]["description"] == (
        "Kenya county-year maize evidence and retrospective model evaluation; "
        "no operational forecast or decision support."
    )
