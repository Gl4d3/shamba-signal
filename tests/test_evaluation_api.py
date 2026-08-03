from __future__ import annotations

import json

from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_evaluation_endpoint_serves_the_generated_local_fixture(tmp_path) -> None:
    fixture = tmp_path / "evaluation_fixture.json"
    fixture.write_text(
        json.dumps(
            {
                "fixture_version": "county-year-evaluation-v1",
                "result": "no-go",
                "provisional_test_year": 2023,
                "models": [{"id": "county_mean", "mae_t_per_ha": 0.2998}],
                "counties": [{"county_id": "busia", "history": [], "test": {}}],
            }
        ),
        encoding="utf-8",
    )

    response = TestClient(create_app(evaluation_fixture_path=fixture)).get("/api/v1/evaluation")

    assert response.status_code == 200
    assert response.json()["result"] == "no-go"
    assert response.json()["counties"][0]["county_id"] == "busia"


def test_evaluation_endpoint_is_explicit_when_private_fixture_is_absent(tmp_path) -> None:
    response = TestClient(
        create_app(evaluation_fixture_path=tmp_path / "missing.json")
    ).get("/api/v1/evaluation")

    assert response.status_code == 503
    assert "private evaluation fixture" in response.json()["detail"]
