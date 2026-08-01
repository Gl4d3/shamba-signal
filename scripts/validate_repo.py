from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

CATALOG_RELATIVE_PATH = Path("data/catalog/datasets.yaml")
EXPECTED_WEIGHT_KEYS = {
    "yield_label_quality",
    "historical_depth",
    "spatial_resolution",
    "satellite_usability",
    "license_and_redistribution",
    "access_stability",
}
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


def _load_catalog(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.is_file():
        return None, [f"missing required file: {CATALOG_RELATIVE_PATH.as_posix()}"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, ["data catalog is not valid JSON"]
    if not isinstance(payload, dict):
        return None, ["data catalog root must be an object"]
    return payload, []


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
        valid_source_id = isinstance(source_id, str) and bool(source_id.strip())
        if valid_source_id:
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


def validate_repository(root: Path = Path(".")) -> list[str]:
    errors = validate_required_files(root)
    catalog_path = root / CATALOG_RELATIVE_PATH
    if catalog_path.is_file():
        errors.extend(validate_catalog(catalog_path))
    return errors


def main() -> None:
    errors = validate_repository()
    if errors:
        raise SystemExit("Repository validation failed:\n- " + "\n- ".join(errors))
    print("Repository contract valid")


if __name__ == "__main__":
    main()
