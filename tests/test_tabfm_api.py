from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from shamba_signal.api.app import create_app


def test_tabfm_endpoint_is_nonfatal_and_precise_when_fixture_is_absent(
    tmp_path: Path,
) -> None:
    client = TestClient(
        create_app(tabfm_fixture_path=tmp_path / "missing-tabfm-fixture.json")
    )

    response = client.get("/api/v1/tabfm-evaluation")

    assert response.status_code == 503
    assert "TabFM" in response.json()["detail"]
    assert "isolated experiment" in response.json()["detail"]
    assert client.get("/healthz").status_code == 200


def test_tabfm_endpoint_serves_valid_versioned_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "dashboard_fixture.json"
    fixture.write_text(
        json.dumps(
            {
                "schema_version": "tabfm-experiment-v1",
                "study_type": "exploratory_rolling_temporal",
                "aggregate": {},
                "folds": [],
                "decision": {"code": "no_go"},
            }
        ),
        encoding="utf-8",
    )
    client = TestClient(create_app(tabfm_fixture_path=fixture))

    response = client.get("/api/v1/tabfm-evaluation")

    assert response.status_code == 200
    assert response.json()["schema_version"] == "tabfm-experiment-v1"


def test_tabfm_endpoint_rejects_wrong_schema_version(tmp_path: Path) -> None:
    fixture = tmp_path / "dashboard_fixture.json"
    fixture.write_text(
        json.dumps({"schema_version": "wrong", "study_type": "something_else"}),
        encoding="utf-8",
    )
    client = TestClient(create_app(tabfm_fixture_path=fixture))

    response = client.get("/api/v1/tabfm-evaluation")

    assert response.status_code == 503
    assert "invalid" in response.json()["detail"].lower()
