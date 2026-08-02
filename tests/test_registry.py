import json
from pathlib import Path

import pytest

from shamba_signal.datasets.registry import load_source_registry


def registry_payload() -> dict[str, object]:
    return {
        "registry_version": "0.2.0",
        "selected_crop": "maize",
        "target_grain": "county x crop x season",
        "sources": [
            {
                "source_id": "fsd-maize-yield",
                "publisher": "Kenya Ministry of Agriculture and Livestock Development",
                "dataset_title": "Maize yield by county",
                "landing_url": "https://fsd.kilimo.go.ke/indicator",
                "acquisition_url": "https://fsd.kilimo.go.ke/api/maize.csv",
                "acquisition_mode": "direct_csv",
                "access_method": "HTTPS CSV endpoint",
                "spatial_coverage": "Kenya admin level 1 counties",
                "temporal_coverage": "2022-2024",
                "terms_status": "review-required",
                "redistribution_status": "review-required",
                "expected_fields": ["county", "year", "yield"],
                "accepted_media_types": ["text/csv"],
                "network_acquisition_ready": True,
            }
        ],
    }


def write_registry(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "sources.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_load_source_registry_builds_typed_sources(tmp_path: Path) -> None:
    registry = load_source_registry(write_registry(tmp_path, registry_payload()))

    assert registry.selected_crop == "maize"
    assert registry.source("fsd-maize-yield").expected_fields == (
        "county",
        "year",
        "yield",
    )


def test_load_source_registry_rejects_duplicate_ids(tmp_path: Path) -> None:
    payload = registry_payload()
    sources = payload["sources"]
    assert isinstance(sources, list)
    sources.append(dict(sources[0]))

    with pytest.raises(ValueError, match="duplicate source_id"):
        load_source_registry(write_registry(tmp_path, payload))


def test_load_source_registry_rejects_missing_sources(tmp_path: Path) -> None:
    payload = registry_payload()
    payload["sources"] = []

    with pytest.raises(ValueError, match="non-empty sources"):
        load_source_registry(write_registry(tmp_path, payload))


def test_committed_registry_pins_verified_fsd_maize_download_links() -> None:
    registry = load_source_registry(Path("data/sources/maize_sources.json"))

    expected_indicators = {
        "fsd-maize-yield": "16",
        "fsd-maize-production": "277",
        "fsd-maize-area": "133",
    }
    for source_id, indicator_id in expected_indicators.items():
        source = registry.source(source_id)
        assert f"/indicators/{indicator_id}/" in source.acquisition_url
        assert source.network_acquisition_ready is False
        assert source.terms_status == "review-required"
