from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from scripts.validate_repo import validate_repository
from shamba_signal.feasibility.models import DIMENSIONS
from shamba_signal.feasibility.report import generate_artifacts

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data/feasibility/evidence.json"
PROFILES_PATH = ROOT / "data/feasibility/candidate_profiles.json"


def test_validation_checklist_uses_selected_crop(tmp_path: Path) -> None:
    payload = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    for crop in payload["crops"]:
        score = 100 if crop["candidate_id"] == "beans" else 0
        crop["dimensions"] = {name: score for name in DIMENSIONS}
    profiles_path = tmp_path / "candidate_profiles.json"
    profiles_path.write_text(json.dumps(payload), encoding="utf-8")
    report_path = tmp_path / "pilot-selection-decision.md"

    result = generate_artifacts(
        evidence_path=EVIDENCE_PATH,
        profiles_path=profiles_path,
        output_dir=tmp_path / "data",
        report_path=report_path,
    )

    report = report_path.read_text(encoding="utf-8")
    assert result.selected_crop == "beans"
    assert "Download and checksum the official beans county records" in report
    assert "official maize county records" not in report


@pytest.mark.parametrize(
    "field,value",
    [
        ("selected_crop", None),
        ("selected_county", "busia"),
        ("runner_up_county", []),
        ("selected_crop", {}),
    ],
)
def test_repository_validator_handles_malformed_selection_records(
    tmp_path: Path, field: str, value: object
) -> None:
    for relative in (
        Path("data/catalog/datasets.yaml"),
        Path("data/feasibility/candidate_profiles.json"),
        Path("data/feasibility/evidence.json"),
        Path("data/feasibility/scorecard.csv"),
        Path("data/feasibility/selection.json"),
    ):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)

    selection_path = tmp_path / "data/feasibility/selection.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    selection[field] = value
    selection_path.write_text(json.dumps(selection), encoding="utf-8")

    errors = validate_repository(root=tmp_path)

    assert any(f"selection record {field}" in error for error in errors)
