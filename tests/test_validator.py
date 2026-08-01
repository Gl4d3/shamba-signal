import json
from pathlib import Path

import pytest

from scripts.validate_repo import validate_catalog, validate_repository


def write_catalog(tmp_path: Path, payload: object) -> Path:
    path = tmp_path / "datasets.yaml"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def valid_catalog() -> dict:
    return {
        "catalog_version": "0.1.0",
        "country": "KEN",
        "pilot_selection": {
            "weights": {
                "yield_label_quality": 35,
                "historical_depth": 20,
                "spatial_resolution": 15,
                "satellite_usability": 10,
                "license_and_redistribution": 10,
                "access_stability": 10,
            }
        },
        "sources": [
            {
                "id": "source",
                "publisher": "Publisher",
                "dataset_title": "Dataset",
                "access_url": "https://example.test/data",
                "access_method": "download",
                "spatial_coverage": "Kenya",
                "temporal_coverage": "2020-2024",
                "license_status": "verified",
            }
        ],
    }


def test_missing_catalog_returns_actionable_error(tmp_path: Path) -> None:
    errors = validate_catalog(tmp_path / "missing.yaml")
    assert errors == ["missing required file: data/catalog/datasets.yaml"]


def test_invalid_json_is_reported_without_traceback(tmp_path: Path) -> None:
    path = tmp_path / "datasets.yaml"
    path.write_text("{broken", encoding="utf-8")
    assert validate_catalog(path) == ["data catalog is not valid JSON"]


@pytest.mark.parametrize("value", [True, -1, float("inf"), "35"])
def test_invalid_weight_values_are_rejected(tmp_path: Path, value: object) -> None:
    payload = valid_catalog()
    payload["pilot_selection"]["weights"]["yield_label_quality"] = value
    errors = validate_catalog(write_catalog(tmp_path, payload))
    assert any("weights must be finite non-negative numbers" in error for error in errors)


def test_missing_weight_key_is_reported(tmp_path: Path) -> None:
    payload = valid_catalog()
    del payload["pilot_selection"]["weights"]["historical_depth"]
    errors = validate_catalog(write_catalog(tmp_path, payload))
    assert any("weight keys" in error for error in errors)


def test_malformed_source_shape_is_reported(tmp_path: Path) -> None:
    payload = valid_catalog()
    payload["sources"] = "not-a-list"
    assert validate_catalog(write_catalog(tmp_path, payload)) == [
        "data catalog sources must be a list"
    ]


def test_source_required_fields_url_and_license_are_validated(tmp_path: Path) -> None:
    payload = valid_catalog()
    payload["sources"][0].pop("publisher")
    payload["sources"][0]["access_url"] = "http://example.test"
    payload["sources"][0]["license_status"] = "bogus"
    errors = validate_catalog(write_catalog(tmp_path, payload))
    assert any("missing required keys" in error for error in errors)
    assert any("must use HTTPS" in error for error in errors)
    assert any("invalid license status" in error for error in errors)


def test_repository_validation_does_not_parse_missing_catalog(tmp_path: Path) -> None:
    errors = validate_repository(root=tmp_path)
    assert "missing required file: data/catalog/datasets.yaml" in errors


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", ""),
        ("publisher", "   "),
        ("dataset_title", ""),
        ("access_method", "\t"),
        ("spatial_coverage", ""),
        ("temporal_coverage", "   "),
    ],
)
def test_required_source_text_fields_reject_empty_values(
    tmp_path: Path, field: str, value: str
) -> None:
    payload = valid_catalog()
    payload["sources"][0][field] = value
    errors = validate_catalog(write_catalog(tmp_path, payload))
    assert any(f"{field} must be a non-empty string" in error for error in errors)


def test_changed_weight_distribution_is_rejected_even_when_total_is_100(
    tmp_path: Path,
) -> None:
    payload = valid_catalog()
    payload["pilot_selection"]["weights"] = {
        "yield_label_quality": 34,
        "historical_depth": 21,
        "spatial_resolution": 15,
        "satellite_usability": 10,
        "license_and_redistribution": 10,
        "access_stability": 10,
    }
    errors = validate_catalog(write_catalog(tmp_path, payload))
    assert "pilot-selection weights must match approved values" in errors


def test_fractional_weight_total_uses_tolerance(tmp_path: Path) -> None:
    payload = valid_catalog()
    payload["pilot_selection"]["weights"] = {
        "yield_label_quality": 73.9,
        "historical_depth": 22.1,
        "spatial_resolution": 0.2,
        "satellite_usability": 1.5,
        "license_and_redistribution": 0.1,
        "access_stability": 2.2,
    }
    errors = validate_catalog(write_catalog(tmp_path, payload))
    assert "pilot-selection weights must total 100" not in errors
    assert "pilot-selection weights must match approved values" in errors


def test_repository_validation_handles_malformed_pilot_without_traceback(
    tmp_path: Path,
) -> None:
    catalog_path = tmp_path / "data/catalog/datasets.yaml"
    catalog_path.parent.mkdir(parents=True)
    payload = valid_catalog()
    payload["pilot_selection"] = "not-an-object"
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")

    errors = validate_repository(root=tmp_path)

    assert "data catalog pilot_selection must be an object" in errors
