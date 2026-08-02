import json
from pathlib import Path

ALLOWED_STATUSES = {
    "rejected-for-yield-target",
    "research-only-candidate",
}


def load_candidates() -> dict[str, object]:
    return json.loads(
        Path("data/sources/fallback_candidates.json").read_text(encoding="utf-8")
    )


def test_fallback_candidate_registry_is_explicit_and_nonempty() -> None:
    payload = load_candidates()
    assert payload["registry_version"] == "0.1.0"
    candidates = payload["candidates"]
    assert isinstance(candidates, list)
    assert candidates
    assert len({item["candidate_id"] for item in candidates}) == len(candidates)
    for item in candidates:
        assert item["status"] in ALLOWED_STATUSES
        assert item["publisher"]
        assert item["dataset_title"]
        assert item["landing_url"].startswith("https://")
        assert item["observed_fields"]
        assert item["blocking_gaps"]
        assert item["next_action"]
        assert item["evidence_urls"]


def test_kchsp_crop_output_is_rejected_for_yield_target() -> None:
    candidates = {
        item["candidate_id"]: item for item in load_candidates()["candidates"]
    }
    item = candidates["kenada-kchsp-2020-q1-q2-crop-output"]

    assert item["status"] == "rejected-for-yield-target"
    assert "quantity_sold" in item["observed_fields"]
    gaps = " ".join(item["blocking_gaps"]).lower()
    assert "production" in gaps
    assert "harvested area" in gaps


def test_kihbs_is_research_only_not_a_silent_target_replacement() -> None:
    candidates = {
        item["candidate_id"]: item for item in load_candidates()["candidates"]
    }
    item = candidates["kenada-kihbs-2005-2006-agriculture"]

    assert item["status"] == "research-only-candidate"
    assert {
        "crop_code",
        "crop_area_acres",
        "quantity_harvested",
        "unit_harvested",
    }.issubset(item["observed_fields"])
    assert item["may_replace_selected_target"] is False
    gaps = " ".join(item["blocking_gaps"]).lower()
    assert "2005-2006" in gaps
    assert "county-season" in gaps
