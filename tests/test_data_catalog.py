import json
from pathlib import Path


def test_dataset_catalog_has_selection_criteria_and_candidate_sources() -> None:
    catalog = json.loads(Path("data/catalog/datasets.yaml").read_text())
    weights = catalog["pilot_selection"]["weights"]
    assert sum(weights.values()) == 100
    assert weights["yield_label_quality"] == 35
    source_ids = {source["id"] for source in catalog["sources"]}
    assert {
        "kilimostat-crops",
        "sentinel-2-l2a",
        "chirps-v3",
        "soilgrids",
        "icpac-admin1",
    }.issubset(source_ids)
    for source in catalog["sources"]:
        assert source["license_status"] in {"verified", "review-required", "blocked"}
        assert source["access_url"].startswith("https://")
        assert source["publisher"]
        assert source["dataset_title"]
        assert source["spatial_coverage"]
        assert source["temporal_coverage"]


def test_unlicensed_cropland_source_is_blocked() -> None:
    catalog = json.loads(Path("data/catalog/datasets.yaml").read_text())
    statuses = {source["id"]: source["license_status"] for source in catalog["sources"]}
    assert statuses["icpac-cropland-2015"] == "blocked"
