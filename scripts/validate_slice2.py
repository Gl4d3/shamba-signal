from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shamba_signal.datasets.registry import load_source_registry

SOURCE_REGISTRY_PATH = Path("data/sources/maize_sources.json")
FALLBACK_REGISTRY_PATH = Path("data/sources/fallback_candidates.json")
REQUIRED_SOURCE_IDS = {
    "nipfn-maize-2012-2020",
}
ALLOWED_FALLBACK_STATUSES = {
    "rejected-for-yield-target",
    "research-only-candidate",
}
REQUIRED_SLICE2_FILES = (
    SOURCE_REGISTRY_PATH,
    FALLBACK_REGISTRY_PATH,
    Path("docs/data/fallback-source-investigation.md"),
    Path("docs/data/slice-2-acquisition-status.md"),
    Path("docs/data/slice-2b-forecast-readiness-decision.md"),
    Path("docs/data/target-observation-contract.md"),
    Path("docs/roadmap/IMPLEMENTATION_SLICES.md"),
    Path("data/sources/slice2b_source_audit.json"),
    Path("docs/superpowers/plans/2026-07-30-slice-2-target-dataset.md"),
    Path("scripts/acquire_source.py"),
    Path("scripts/build_nipfn_target.py"),
    Path("scripts/probe_sources.py"),
    Path("src/shamba_signal/datasets/acquisition.py"),
    Path("src/shamba_signal/datasets/adapters.py"),
    Path("src/shamba_signal/datasets/manifest.py"),
    Path("src/shamba_signal/datasets/nipfn.py"),
    Path("src/shamba_signal/datasets/nipfn_publication.py"),
    Path("src/shamba_signal/datasets/probe.py"),
    Path("src/shamba_signal/datasets/registry.py"),
    Path("src/shamba_signal/datasets/target.py"),
    Path("src/shamba_signal/datasets/target_build.py"),
)


def _load_object(path: Path, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, []
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, [f"{label} is not valid JSON"]
    if not isinstance(payload, dict):
        return None, [f"{label} root must be an object"]
    return payload, []


def _validate_primary_sources(root: Path) -> list[str]:
    path = root / SOURCE_REGISTRY_PATH
    if not path.is_file():
        return []
    try:
        registry = load_source_registry(path)
    except ValueError as exc:
        return [f"source registry invalid: {exc}"]

    errors: list[str] = []
    if registry.selected_crop != "maize":
        errors.append("source registry selected_crop must remain maize for Slice 2")
    if registry.target_grain != "county x crop x year":
        errors.append("source registry target_grain must remain county x crop x year")
    source_ids = {source.source_id for source in registry.sources}
    missing = sorted(REQUIRED_SOURCE_IDS - source_ids)
    if missing:
        errors.append(f"source registry missing required source IDs: {missing}")
    if "nipfn-maize-2012-2020" not in source_ids:
        return errors
    nipfn = registry.source("nipfn-maize-2012-2020")
    if nipfn.expected_fields != ("County", "Year", "Indicator", "Value"):
        errors.append("NIPFN source must retain its verified tidy worksheet schema")
    if "2019 is absent" not in nipfn.temporal_coverage:
        errors.append("NIPFN source must disclose the missing 2019 annual observation")
    return errors


def _validate_fallbacks(root: Path) -> list[str]:
    payload, errors = _load_object(
        root / FALLBACK_REGISTRY_PATH,
        "fallback candidate registry",
    )
    if payload is None:
        return errors
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return [*errors, "fallback candidate registry must contain candidates"]

    seen: set[str] = set()
    for index, item in enumerate(candidates):
        label = f"fallback candidate[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        candidate_id = item.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            errors.append(f"{label} candidate_id must be a non-empty string")
        elif candidate_id in seen:
            errors.append(f"duplicate fallback candidate_id: {candidate_id}")
        else:
            seen.add(candidate_id)
            label = f"fallback candidate {candidate_id}"
        if item.get("status") not in ALLOWED_FALLBACK_STATUSES:
            errors.append(f"{label} has invalid status: {item.get('status')!r}")
        if item.get("may_replace_selected_target") is not False:
            errors.append(f"{label} must not replace the selected target")
        landing_url = item.get("landing_url")
        if not isinstance(landing_url, str) or not landing_url.startswith("https://"):
            errors.append(f"{label} landing_url must use HTTPS")
        for field in ("observed_fields", "blocking_gaps", "evidence_urls"):
            value = item.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"{label} {field} must be a non-empty list")
    return errors


def _validate_slice_split_docs(root: Path) -> list[str]:
    errors: list[str] = []
    roadmap = (
        (root / "docs/roadmap/IMPLEMENTATION_SLICES.md").read_text(encoding="utf-8")
        if (root / "docs/roadmap/IMPLEMENTATION_SLICES.md").is_file()
        else ""
    )
    if "Slice 2A" not in roadmap or "Slice 2B" not in roadmap:
        errors.append("roadmap must define Slice 2A annual snapshot and Slice 2B reconciliation")
    status = (
        (root / "docs/data/slice-2-acquisition-status.md").read_text(encoding="utf-8")
        if (root / "docs/data/slice-2-acquisition-status.md").is_file()
        else ""
    )
    if "acquisition blocked" in status.lower():
        errors.append("acquisition status must not present the accepted annual snapshot as blocked")
    if "busia has not been evaluated" in status.lower():
        errors.append("acquisition status must not state that Busia has never been evaluated")
    return errors


def _validate_source_audit(root: Path) -> list[str]:
    payload, errors = _load_object(
        root / "data/sources/slice2b_source_audit.json", "Slice 2B source audit"
    )
    if payload is None:
        return errors

    expected = {
        "audit_version": ("1.0", "audit version is incorrect"),
        "accepted_snapshot.source_id": (
            "nipfn-maize-2012-2020",
            "accepted snapshot source ID is incorrect",
        ),
        "accepted_snapshot.sha256": (
            "15a47b6fdc634fab7a69cd7576974d2f9eeb550218389d4a1526dd8123a92ab8",
            "accepted snapshot SHA-256 is incorrect",
        ),
        "accepted_snapshot.status": (
            "accepted-source-bound-private",
            "accepted snapshot status is incorrect",
        ),
        "accepted_snapshot.coverage": (
            "annual county area, production, and reported yield for 2012-2018 and 2020",
            "accepted snapshot coverage is incorrect",
        ),
        "candidate_revision.direct_url": (
            "https://www.knbs.or.ke/wp-content/uploads/2025/01/National-Agriculture-Production-Report-2024.pdf",
            "candidate direct URL is incorrect",
        ),
        "candidate_revision.publisher": (
            "Kenya National Bureau of Statistics",
            "candidate publisher is incorrect",
        ),
        "candidate_revision.title": (
            "National Agriculture Production Report 2024",
            "candidate title is incorrect",
        ),
        "candidate_revision.byte_size": (12398810, "candidate byte size is incorrect"),
        "candidate_revision.sha256": (
            "7d86dc4cbfa1d0b5204e2428fb8d84c3bada0fc1775bf0b7d557dfebcc4d70eb",
            "candidate SHA-256 is incorrect",
        ),
        "candidate_revision.status": (
            "private-candidate-not-accepted-or-merged",
            "candidate status is incorrect",
        ),
        "candidate_revision.terms_and_redistribution": (
            "review-required",
            "candidate terms are incorrect",
        ),
        "candidate_revision.coverage": (
            "annual county harvested area and production for 2019-2023; 2023 is provisional; "
            "no reported yield field",
            "candidate coverage is incorrect",
        ),
        "overlap_comparison.relative_difference_threshold": (
            0.001,
            "overlap threshold is incorrect",
        ),
        "overlap_comparison.year": (2020, "overlap year is incorrect"),
        "overlap_comparison.materially_different_counties": (
            24,
            "material overlap count is incorrect",
        ),
        "overlap_comparison.overlapping_counties": (47, "overlap county count is incorrect"),
        "overlap_comparison.Busia": (
            "matches within rounding",
            "Busia overlap finding is incorrect",
        ),
        "overlap_comparison.Trans Nzoia.accepted_workbook": (
            "area 18,591 ha / production 11,251.1 t",
            "Trans Nzoia workbook finding is incorrect",
        ),
        "overlap_comparison.Trans Nzoia.candidate_report": (
            "area 104,850 ha / production 489,056 t",
            "Trans Nzoia report finding is incorrect",
        ),
        "source_contracts.KilimoSTAT": (
            "removed from critical path: no current verified response contract is accessible",
            "KilimoSTAT critical-path decision is incorrect",
        ),
        "source_contracts.Food Systems Dashboard": (
            "removed from critical path: no current verified response contract is accessible",
            "Food Systems Dashboard critical-path decision is incorrect",
        ),
        "decision.supported_target_grain": ("county-year", "supported target grain is incorrect"),
        "decision.county_season": ("evidence-insufficient", "county-season decision is incorrect"),
        "decision.annual_disaggregation": (
            "no crop calendar may disaggregate annual totals",
            "annual disaggregation decision is incorrect",
        ),
        "decision.next_gate": (
            "reconcile source vintages and extend the annual panel before modelling",
            "next gate decision is incorrect",
        ),
    }
    for dotted_path, (expected_value, message) in expected.items():
        value: Any = payload
        for key in dotted_path.split("."):
            value = value.get(key) if isinstance(value, dict) else None
        if value != expected_value:
            errors.append(message)
    return errors


def _validate_decision_document(root: Path) -> list[str]:
    path = root / "docs/data/slice-2b-forecast-readiness-decision.md"
    if not path.is_file():
        return []
    document = path.read_text(encoding="utf-8")
    required_phrases = (
        "source-bound, private annual snapshot package, not a model-ready dataset",
        "supported target grain is **county-year**",
        "County-season is therefore an evidence-insufficiency result",
        "no crop calendar may disaggregate annual totals",
        "reconcile official annual source vintages and extend the annual panel before any "
        "modelling decision",
    )
    if all(phrase in document for phrase in required_phrases):
        return []
    return ["forecast-readiness decision document is missing required boundary phrases"]


def validate_slice2(root: Path = Path(".")) -> list[str]:
    errors = [
        f"missing Slice 2 file: {path.as_posix()}"
        for path in REQUIRED_SLICE2_FILES
        if not (root / path).is_file()
    ]
    errors.extend(_validate_primary_sources(root))
    errors.extend(_validate_fallbacks(root))
    errors.extend(_validate_slice_split_docs(root))
    errors.extend(_validate_source_audit(root))
    errors.extend(_validate_decision_document(root))
    return errors


def main() -> None:
    errors = validate_slice2()
    if errors:
        raise SystemExit("Slice 2 validation failed:\n- " + "\n- ".join(errors))
    print("Slice 2 contract valid")


if __name__ == "__main__":
    main()
