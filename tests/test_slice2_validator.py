import json
from pathlib import Path

import pytest

from scripts.validate_slice2 import validate_slice2

REQUIRED_PATHS = (
    "data/sources/maize_sources.json",
    "data/sources/fallback_candidates.json",
    "docs/data/fallback-source-investigation.md",
    "docs/data/slice-2-acquisition-status.md",
    "docs/data/slice-2b-forecast-readiness-decision.md",
    "docs/data/target-observation-contract.md",
    "docs/roadmap/IMPLEMENTATION_SLICES.md",
    "data/sources/slice2b_source_audit.json",
    "docs/superpowers/plans/2026-07-30-slice-2-target-dataset.md",
    "scripts/acquire_source.py",
    "scripts/build_nipfn_target.py",
    "scripts/probe_sources.py",
    "src/shamba_signal/datasets/acquisition.py",
    "src/shamba_signal/datasets/adapters.py",
    "src/shamba_signal/datasets/manifest.py",
    "src/shamba_signal/datasets/nipfn.py",
    "src/shamba_signal/datasets/nipfn_publication.py",
    "src/shamba_signal/datasets/probe.py",
    "src/shamba_signal/datasets/registry.py",
    "src/shamba_signal/datasets/target.py",
    "src/shamba_signal/datasets/target_build.py",
)


def copy_required_tree(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    for relative in REQUIRED_PATHS:
        source = root / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())


def test_slice2_validator_accepts_current_contract(tmp_path: Path) -> None:
    copy_required_tree(tmp_path)

    assert validate_slice2(tmp_path) == []


def test_slice2_validator_requires_county_year_as_the_supported_target_grain(
    tmp_path: Path,
) -> None:
    copy_required_tree(tmp_path)
    path = tmp_path / "data/sources/maize_sources.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["target_grain"] = "county x crop x season"
    path.write_text(json.dumps(payload), encoding="utf-8")

    errors = validate_slice2(tmp_path)

    assert "source registry target_grain must remain county x crop x year" in errors


def test_slice2_validator_reports_missing_artifacts(tmp_path: Path) -> None:
    errors = validate_slice2(tmp_path)

    assert "missing Slice 2 file: data/sources/maize_sources.json" in errors
    assert "missing Slice 2 file: scripts/probe_sources.py" in errors
    assert "missing Slice 2 file: scripts/build_nipfn_target.py" in errors


def test_slice2_validator_rejects_missing_primary_source(tmp_path: Path) -> None:
    copy_required_tree(tmp_path)
    path = tmp_path / "data/sources/maize_sources.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["sources"] = [
        item for item in payload["sources"] if item["source_id"] != "nipfn-maize-2012-2020"
    ]
    path.write_text(json.dumps(payload), encoding="utf-8")

    errors = validate_slice2(tmp_path)

    assert any("missing required source IDs" in error for error in errors)


def test_slice2_validator_rejects_silent_fallback_replacement(tmp_path: Path) -> None:
    copy_required_tree(tmp_path)
    path = tmp_path / "data/sources/fallback_candidates.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["candidates"][1]["may_replace_selected_target"] = True
    path.write_text(json.dumps(payload), encoding="utf-8")

    errors = validate_slice2(tmp_path)

    assert any("must not replace the selected target" in error for error in errors)


def test_slice2_validator_requires_slice_2a_2b_split_contract(tmp_path: Path) -> None:
    copy_required_tree(tmp_path)
    audit_path = tmp_path / "data/sources/slice2b_source_audit.json"
    audit_path.unlink()

    errors = validate_slice2(tmp_path)

    assert "missing Slice 2 file: data/sources/slice2b_source_audit.json" in errors


def test_slice2_validator_rejects_pre_split_or_contradictory_slice_2_docs(
    tmp_path: Path,
) -> None:
    copy_required_tree(tmp_path)
    roadmap_path = tmp_path / "docs/roadmap/IMPLEMENTATION_SLICES.md"
    roadmap_path.write_text(
        "## Slice 2 — Reproducible county-season target dataset\n",
        encoding="utf-8",
    )
    status_path = tmp_path / "docs/data/slice-2-acquisition-status.md"
    status_path.write_text("acquisition blocked\nBusia has not been evaluated\n", encoding="utf-8")

    errors = validate_slice2(tmp_path)

    assert "roadmap must define Slice 2A annual snapshot and Slice 2B reconciliation" in errors
    assert "acquisition status must not present the accepted annual snapshot as blocked" in errors
    assert "acquisition status must not state that Busia has never been evaluated" in errors


@pytest.mark.parametrize(
    ("path", "value", "expected"),
    [
        ("accepted_snapshot.sha256", "bad", "accepted snapshot SHA-256 is incorrect"),
        ("accepted_snapshot.status", "accepted", "accepted snapshot status is incorrect"),
        ("accepted_snapshot.coverage", "unknown", "accepted snapshot coverage is incorrect"),
        (
            "candidate_revision.direct_url",
            "https://example.com",
            "candidate direct URL is incorrect",
        ),
        ("candidate_revision.byte_size", 1, "candidate byte size is incorrect"),
        ("candidate_revision.sha256", "bad", "candidate SHA-256 is incorrect"),
        ("candidate_revision.status", "accepted", "candidate status is incorrect"),
        (
            "candidate_revision.terms_and_redistribution",
            "accepted",
            "candidate terms are incorrect",
        ),
        ("candidate_revision.coverage", "unknown", "candidate coverage is incorrect"),
        ("overlap_comparison.relative_difference_threshold", 0.1, "overlap threshold is incorrect"),
        (
            "overlap_comparison.materially_different_counties",
            1,
            "material overlap count is incorrect",
        ),
        ("overlap_comparison.overlapping_counties", 1, "overlap county count is incorrect"),
        ("overlap_comparison.Busia", "untested", "Busia overlap finding is incorrect"),
        (
            "overlap_comparison.Trans Nzoia.accepted_workbook",
            "unknown",
            "Trans Nzoia workbook finding is incorrect",
        ),
        (
            "overlap_comparison.Trans Nzoia.candidate_report",
            "unknown",
            "Trans Nzoia report finding is incorrect",
        ),
        ("source_contracts.KilimoSTAT", "active", "KilimoSTAT critical-path decision is incorrect"),
        (
            "source_contracts.Food Systems Dashboard",
            "active",
            "Food Systems Dashboard critical-path decision is incorrect",
        ),
        ("decision.supported_target_grain", "county-season", "supported target grain is incorrect"),
        ("decision.county_season", "supported", "county-season decision is incorrect"),
        (
            "decision.annual_disaggregation",
            "allowed",
            "annual disaggregation decision is incorrect",
        ),
        ("decision.next_gate", "model", "next gate decision is incorrect"),
    ],
)
def test_slice2_validator_rejects_corrupted_source_audit_facts(
    tmp_path: Path, path: str, value: object, expected: str
) -> None:
    copy_required_tree(tmp_path)
    audit_path = tmp_path / "data/sources/slice2b_source_audit.json"
    payload = json.loads(audit_path.read_text(encoding="utf-8"))
    target = payload
    *parents, leaf = path.split(".")
    for parent in parents:
        target = target[parent]
    target[leaf] = value
    audit_path.write_text(json.dumps(payload), encoding="utf-8")

    assert expected in validate_slice2(tmp_path)


def test_slice2_validator_requires_decision_document_boundary_phrases(tmp_path: Path) -> None:
    copy_required_tree(tmp_path)
    decision_path = tmp_path / "docs/data/slice-2b-forecast-readiness-decision.md"
    decision_path.write_text("# Decision\n", encoding="utf-8")

    assert (
        "forecast-readiness decision document is missing required boundary phrases"
        in validate_slice2(tmp_path)
    )
