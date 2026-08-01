from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_platform_status_exposes_approved_product_contract() -> None:
    client = TestClient(create_app())
    response = client.get("/api/v1/platform/status")
    assert response.status_code == 200
    body = response.json()
    assert body["product"] == "Shamba Signal"
    assert body["primary_output"] == "county-season yield forecast"
    assert body["forecast_timing"] == "mid-season"
    assert body["architecture"] == "modular decision-intelligence platform"
    assert body["refresh_modes"] == ["scheduled", "analyst-triggered"]


def test_foundation_only_marks_data_feasibility_next() -> None:
    client = TestClient(create_app())
    statuses = {
        item["id"]: item["status"]
        for item in client.get("/api/v1/platform/status").json()["capabilities"]
    }
    assert statuses == {
        "data-feasibility": "next",
        "yield-forecasting": "planned",
        "stress-attribution": "planned",
        "guardrailed-advisory": "planned",
    }


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
        "next",
        "planned",
    ]
