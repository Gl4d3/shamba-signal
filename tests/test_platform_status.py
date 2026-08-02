from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_platform_status_exposes_approved_product_contract() -> None:
    client = TestClient(create_app())
    response = client.get("/api/v1/platform/status")
    assert response.status_code == 200
    body = response.json()
    assert body["product"] == "Shamba Signal"
    assert body["release"] == "slice-2a-annual-snapshot-v1"
    assert body["primary_output"] == "county-year baseline feasibility"
    assert body["forecast_timing"] == "not scheduled"
    assert body["architecture"] == "modular decision-intelligence platform"
    assert body["refresh_modes"] == ["scheduled", "analyst-triggered"]
    assert "Busia" in body["geography"]
    assert "Trans Nzoia" in body["geography"]
    assert "source-bound" in body["crop_scope"]


def test_platform_status_reports_verified_annual_target_without_seasonal_model_claim() -> None:
    client = TestClient(create_app())
    statuses = {
        item["id"]: item["status"]
        for item in client.get("/api/v1/platform/status").json()["capabilities"]
    }
    assert statuses == {
        "data-feasibility": "ready",
        "annual-snapshot": "ready",
        "annual-label-reconciliation": "next",
        "county-year-baseline": "planned",
        "stress-attribution": "planned",
        "guardrailed-advisory": "planned",
    }
    target_dataset = next(
        item
        for item in client.get("/api/v1/platform/status").json()["capabilities"]
        if item["id"] == "annual-snapshot"
    )
    assert "source-bound" in target_dataset["outcome"]
    assert "not model-ready" in target_dataset["outcome"]
    reconciliation = next(
        item
        for item in client.get("/api/v1/platform/status").json()["capabilities"]
        if item["id"] == "annual-label-reconciliation"
    )
    assert "conflicting official 2020 vintages" in reconciliation["outcome"]


def test_openapi_declares_platform_status_response_schema_and_enums() -> None:
    client = TestClient(create_app())
    schema = client.get("/openapi.json").json()
    response_schema = (
        schema["paths"]["/api/v1/platform/status"]["get"]["responses"]["200"]
        ["content"]["application/json"]["schema"]
    )
    assert response_schema == {"$ref": "#/components/schemas/PlatformStatus"}
    assert schema["components"]["schemas"]["CapabilityStatus"]["enum"] == [
        "ready",
        "blocked",
        "next",
        "planned",
    ]
