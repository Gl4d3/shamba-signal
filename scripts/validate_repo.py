from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

CATALOG_RELATIVE_PATH = Path("data/catalog/datasets.yaml")
FEASIBILITY_PROFILES_PATH = Path("data/feasibility/candidate_profiles.json")
FEASIBILITY_EVIDENCE_PATH = Path("data/feasibility/evidence.json")
FEASIBILITY_SCORECARD_PATH = Path("data/feasibility/scorecard.csv")
FEASIBILITY_SELECTION_PATH = Path("data/feasibility/selection.json")
FEASIBILITY_REPORT_PATH = Path("docs/data/pilot-selection-decision.md")
APPROVED_WEIGHTS = {
    "yield_label_quality": 35,
    "historical_depth": 20,
    "spatial_resolution": 15,
    "satellite_usability": 10,
    "license_and_redistribution": 10,
    "access_stability": 10,
}
EXPECTED_WEIGHT_KEYS = set(APPROVED_WEIGHTS)
ALLOWED_LICENSE_STATES = {"verified", "review-required", "restricted", "unknown", "blocked"}
REQUIRED_SOURCE_KEYS = {
    "id",
    "publisher",
    "dataset_title",
    "access_url",
    "access_method",
    "spatial_coverage",
    "temporal_coverage",
    "license_status",
}
REQUIRED_SOURCE_TEXT_FIELDS = {
    "id",
    "publisher",
    "dataset_title",
    "access_method",
    "spatial_coverage",
    "temporal_coverage",
}
REQUIRED_FILES = (
    Path("README.md"),
    Path("docs/product/PRD.md"),
    Path("docs/product/MVP.md"),
    Path("docs/architecture/ARCHITECTURE.md"),
    Path("docs/roadmap/IMPLEMENTATION_SLICES.md"),
    Path("docs/data/data-source-register.md"),
    CATALOG_RELATIVE_PATH,
    FEASIBILITY_PROFILES_PATH,
    FEASIBILITY_EVIDENCE_PATH,
    FEASIBILITY_SCORECARD_PATH,
    FEASIBILITY_SELECTION_PATH,
    FEASIBILITY_REPORT_PATH,
    Path("docs/superpowers/specs/2026-07-29-shamba-signal-foundation-design.md"),
    Path("docs/superpowers/plans/2026-07-29-shamba-signal-foundation.md"),
    Path(".github/workflows/ci.yml"),
    Path(".github/ISSUE_TEMPLATE/implementation-slice.yml"),
    Path(".github/ISSUE_TEMPLATE/research-evidence.yml"),
    Path(".github/pull_request_template.md"),
    Path("uv.lock"),
)


def validate_required_files(root: Path = Path(".")) -> list[str]:
    return [
        f"missing required file: {path.as_posix()}"
        for path in REQUIRED_FILES
        if not (root / path).is_file()
    ]


def _load_json(path: Path, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.is_file():
        return None, [f"missing required file: {path.as_posix()}"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, [f"{label} is not valid JSON"]
    if not isinstance(payload, dict):
        return None, [f"{label} root must be an object"]
    return payload, []


def _load_catalog(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    return _load_json(path, "data catalog")


def validate_catalog(path: Path = CATALOG_RELATIVE_PATH) -> list[str]:
    catalog, errors = _load_catalog(path)
    if catalog is None:
        return errors

    pilot = catalog.get("pilot_selection")
    if not isinstance(pilot, dict):
        errors.append("data catalog pilot_selection must be an object")
        return errors
    weights = pilot.get("weights")
    if not isinstance(weights, dict):
        errors.append("data catalog pilot_selection.weights must be an object")
    else:
        actual_keys = set(weights)
        if actual_keys != EXPECTED_WEIGHT_KEYS:
            missing = sorted(EXPECTED_WEIGHT_KEYS - actual_keys)
            unexpected = sorted(actual_keys - EXPECTED_WEIGHT_KEYS)
            errors.append(
                "pilot-selection weight keys must match the approved dimensions "
                f"(missing={missing}, unexpected={unexpected})"
            )
        values_are_valid = True
        for key, value in weights.items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                errors.append(
                    f"pilot-selection weights must be finite non-negative numbers: {key}={value!r}"
                )
                values_are_valid = False
        if values_are_valid and not math.isclose(
            sum(weights.values()), 100.0, rel_tol=0.0, abs_tol=1e-9
        ):
            errors.append("pilot-selection weights must total 100")
        if (
            values_are_valid
            and actual_keys == EXPECTED_WEIGHT_KEYS
            and weights != APPROVED_WEIGHTS
        ):
            errors.append("pilot-selection weights must match approved values")

    sources = catalog.get("sources")
    if not isinstance(sources, list):
        errors.append("data catalog sources must be a list")
        return errors
    seen_ids: set[str] = set()
    for index, source in enumerate(sources):
        label = f"source[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be an object")
            continue
        source_id = source.get("id")
        if isinstance(source_id, str) and source_id.strip():
            source_id = source_id.strip()
            label = f"source {source_id}"
            if source_id in seen_ids:
                errors.append(f"duplicate source id: {source_id}")
            seen_ids.add(source_id)
        missing_keys = sorted(REQUIRED_SOURCE_KEYS - set(source))
        if missing_keys:
            errors.append(f"{label} missing required keys: {missing_keys}")
        for field in sorted(REQUIRED_SOURCE_TEXT_FIELDS & set(source)):
            value = source.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label} {field} must be a non-empty string")
        access_url = source.get("access_url")
        if not isinstance(access_url, str) or not access_url.startswith("https://"):
            errors.append(f"{label} access_url must use HTTPS")
        license_status = source.get("license_status")
        if license_status not in ALLOWED_LICENSE_STATES:
            errors.append(f"{label} has invalid license status: {license_status!r}")
    if not sources:
        errors.append("data catalog sources must not be empty")
    return errors


def validate_feasibility(root: Path = Path(".")) -> list[str]:
    errors: list[str] = []
    catalog, catalog_errors = _load_catalog(root / CATALOG_RELATIVE_PATH)
    profiles, profile_errors = _load_json(root / FEASIBILITY_PROFILES_PATH, "candidate profiles")
    evidence, evidence_errors = _load_json(root / FEASIBILITY_EVIDENCE_PATH, "evidence register")
    selection, selection_errors = _load_json(root / FEASIBILITY_SELECTION_PATH, "selection record")
    errors.extend(catalog_errors + profile_errors + evidence_errors + selection_errors)
    if any(item is None for item in (catalog, profiles, evidence, selection)):
        return errors

    pilot = catalog["pilot_selection"]
    if profiles.get("weights") != APPROVED_WEIGHTS:
        errors.append("candidate profile weights must match approved values")
    if selection.get("weights") != APPROVED_WEIGHTS:
        errors.append("selection record weights must match approved values")

    counties = profiles.get("counties")
    crops = profiles.get("crops")
    if not isinstance(counties, list) or len(counties) != 47:
        errors.append("candidate profiles must contain all 47 counties")
    if not isinstance(crops, list) or len(crops) != 4:
        errors.append("candidate profiles must contain four crop candidates")

    evidence_rows = evidence.get("evidence")
    evidence_ids = {
        item.get("id")
        for item in evidence_rows
        if isinstance(evidence_rows, list) and isinstance(item, dict)
    } if isinstance(evidence_rows, list) else set()
    if not evidence_ids or None in evidence_ids or len(evidence_ids) != len(evidence_rows or []):
        errors.append("evidence register IDs must be non-empty and unique")

    selected_crop = selection.get("selected_crop", {}).get("candidate_id")
    selected_county = selection.get("selected_county", {}).get("candidate_id")
    fallback_county = selection.get("runner_up_county", {}).get("candidate_id")
    if selected_crop != pilot.get("selected_crop"):
        errors.append("catalog and selection record disagree on selected crop")
    if selected_county != pilot.get("selected_county"):
        errors.append("catalog and selection record disagree on selected county")
    if fallback_county != pilot.get("fallback_county"):
        errors.append("catalog and selection record disagree on fallback county")

    scorecard_path = root / FEASIBILITY_SCORECARD_PATH
    if scorecard_path.is_file():
        with scorecard_path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        keys = [(row.get("candidate_type"), row.get("candidate_id")) for row in rows]
        if len(keys) != len(set(keys)):
            errors.append("feasibility scorecard candidate keys must be unique")
        if len([row for row in rows if row.get("candidate_type") == "county"]) != 47:
            errors.append("feasibility scorecard must contain 47 county rows")
        if len([row for row in rows if row.get("candidate_type") == "crop"]) != 4:
            errors.append("feasibility scorecard must contain four crop rows")
        if ("crop", selected_crop) not in keys or ("county", selected_county) not in keys:
            errors.append("feasibility scorecard must contain the selected crop and county")
    return errors


def validate_repository(root: Path = Path(".")) -> list[str]:
    errors = validate_required_files(root)
    catalog_path = root / CATALOG_RELATIVE_PATH
    if catalog_path.is_file():
        errors.extend(validate_catalog(catalog_path))
    if all((root / path).is_file() for path in (
        CATALOG_RELATIVE_PATH,
        FEASIBILITY_PROFILES_PATH,
        FEASIBILITY_EVIDENCE_PATH,
        FEASIBILITY_SCORECARD_PATH,
        FEASIBILITY_SELECTION_PATH,
    )):
        errors.extend(validate_feasibility(root))
    return errors


def main() -> None:
    errors = validate_repository()
    if errors:
        raise SystemExit("Repository validation failed:\n- " + "\n- ".join(errors))
    print("Repository contract valid")


if __name__ == "__main__":
    main()
