import json
from pathlib import Path


def load_catalog() -> dict:
    return json.loads(Path("data/catalog/datasets.yaml").read_text(encoding="utf-8"))


def test_dataset_catalog_has_approved_selection_and_candidate_sources() -> None:
    catalog = load_catalog()
    pilot = catalog["pilot_selection"]
    weights = pilot["weights"]
    assert weights == {
        "yield_label_quality": 35,
        "historical_depth": 20,
        "spatial_resolution": 15,
        "satellite_usability": 10,
        "license_and_redistribution": 10,
        "access_stability": 10,
    }
    assert pilot["selected_crop"] == "maize"
    assert pilot["selected_county"] == "busia"
    assert pilot["fallback_county"] == "trans_nzoia"
    assert pilot["selection_record"] == "data/feasibility/selection.json"
    assert pilot["decision_report"] == "docs/data/pilot-selection-decision.md"

    source_ids = {source["id"] for source in catalog["sources"]}
    assert {
        "kilimostat-county-crops",
        "nipfn-maize-2012-2020",
        "fsd-maize-yield",
        "africultures-crop-calendar",
        "plantvillage-kenya",
        "nasa-busia-crop-map",
        "sentinel-2-l2a",
        "chirps-v3",
        "soilgrids",
        "icpac-admin1",
    }.issubset(source_ids)
    for source in catalog["sources"]:
        assert source["license_status"] in {"verified", "review-required", "blocked"}
        assert source["access_url"].startswith("https://")
        assert source["publisher"].strip()
        assert source["dataset_title"].strip()
        assert source["spatial_coverage"].strip()
        assert source["temporal_coverage"].strip()
        assert source["access_method"].strip()


def test_unlicensed_sources_are_not_marked_verified() -> None:
    catalog = load_catalog()
    statuses = {source["id"]: source["license_status"] for source in catalog["sources"]}
    assert statuses["icpac-cropland-2015"] == "blocked"
    assert statuses["nasa-busia-crop-map"] == "review-required"
    assert statuses["nipfn-maize-2012-2020"] == "review-required"
