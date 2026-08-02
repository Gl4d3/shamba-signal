from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shamba_signal.datasets.registry import load_source_registry

SOURCE_REGISTRY_PATH = Path("data/sources/maize_sources.json")
FALLBACK_REGISTRY_PATH = Path("data/sources/fallback_candidates.json")
REQUIRED_SOURCE_IDS = {
    "kilimostat-county-crops",
    "fsd-maize-yield",
    "fsd-maize-production",
    "fsd-maize-area",
    "nipfn-maize-2012-2020",
}
EXPECTED_FSD_INDICATORS = {
    "fsd-maize-yield": "16",
    "fsd-maize-production": "277",
    "fsd-maize-area": "133",
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
    Path("docs/data/target-observation-contract.md"),
    Path("docs/superpowers/plans/2026-07-30-slice-2-target-dataset.md"),
    Path("scripts/acquire_source.py"),
    Path("scripts/probe_sources.py"),
    Path("src/shamba_signal/datasets/acquisition.py"),
    Path("src/shamba_signal/datasets/adapters.py"),
    Path("src/shamba_signal/datasets/manifest.py"),
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
    if registry.target_grain != "county x crop x season":
        errors.append("source registry target_grain must be county x crop x season")
    source_ids = {source.source_id for source in registry.sources}
    missing = sorted(REQUIRED_SOURCE_IDS - source_ids)
    unexpected = sorted(source_ids - REQUIRED_SOURCE_IDS)
    if missing:
        errors.append(f"source registry missing required source IDs: {missing}")
    if unexpected:
        errors.append(f"source registry has unexpected source IDs: {unexpected}")
    for source_id, indicator_id in EXPECTED_FSD_INDICATORS.items():
        if source_id not in source_ids:
            continue
        source = registry.source(source_id)
        if f"/indicators/{indicator_id}/" not in source.acquisition_url:
            errors.append(f"{source_id} must use FSD indicator {indicator_id}")
        if source.network_acquisition_ready:
            errors.append(
                f"{source_id} must remain network-disabled until a valid schema is frozen"
            )
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


def validate_slice2(root: Path = Path(".")) -> list[str]:
    errors = [
        f"missing Slice 2 file: {path.as_posix()}"
        for path in REQUIRED_SLICE2_FILES
        if not (root / path).is_file()
    ]
    errors.extend(_validate_primary_sources(root))
    errors.extend(_validate_fallbacks(root))
    return errors


def main() -> None:
    errors = validate_slice2()
    if errors:
        raise SystemExit("Slice 2 validation failed:\n- " + "\n- ".join(errors))
    print("Slice 2 contract valid")


if __name__ == "__main__":
    main()
