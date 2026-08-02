import json
from pathlib import Path

from scripts.validate_slice2 import validate_slice2


REQUIRED_PATHS = (
    "data/sources/maize_sources.json",
    "data/sources/fallback_candidates.json",
    "docs/data/fallback-source-investigation.md",
    "docs/data/slice-2-acquisition-status.md",
    "docs/data/target-observation-contract.md",
    "docs/superpowers/plans/2026-07-30-slice-2-target-dataset.md",
    "scripts/acquire_source.py",
    "scripts/probe_sources.py",
    "src/shamba_signal/datasets/acquisition.py",
    "src/shamba_signal/datasets/adapters.py",
    "src/shamba_signal/datasets/manifest.py",
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


def test_slice2_validator_reports_missing_artifacts(tmp_path: Path) -> None:
    errors = validate_slice2(tmp_path)

    assert "missing Slice 2 file: data/sources/maize_sources.json" in errors
    assert "missing Slice 2 file: scripts/probe_sources.py" in errors


def test_slice2_validator_rejects_missing_primary_source(tmp_path: Path) -> None:
    copy_required_tree(tmp_path)
    path = tmp_path / "data/sources/maize_sources.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["sources"] = [
        item for item in payload["sources"] if item["source_id"] != "fsd-maize-yield"
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
