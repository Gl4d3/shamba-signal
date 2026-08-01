from __future__ import annotations

import json
from pathlib import Path

import pytest

from shamba_signal.feasibility.models import DIMENSIONS, CandidateProfile, ScoreWeights
from shamba_signal.feasibility.report import generate_artifacts, load_profiles
from shamba_signal.feasibility.scoring import (
    rank_candidates,
    run_sensitivity_analysis,
    score_candidate,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data/feasibility/evidence.json"
PROFILES_PATH = ROOT / "data/feasibility/candidate_profiles.json"
CANONICAL_REPORT_PATH = ROOT / "docs/data/pilot-selection-decision.md"


def test_weights_must_sum_to_100() -> None:
    with pytest.raises(ValueError, match="sum to 100"):
        ScoreWeights(35, 20, 15, 10, 10, 9)


def test_weight_mapping_preserves_fractional_values() -> None:
    weights = ScoreWeights.from_mapping(
        {
            "yield_label_quality": 34.5,
            "historical_depth": 20.5,
            "spatial_resolution": 15,
            "satellite_usability": 10,
            "license_and_redistribution": 10,
            "access_stability": 10,
        }
    )
    assert weights.yield_label_quality == 34.5
    assert weights.historical_depth == 20.5


def test_weight_mapping_rejects_boolean_values() -> None:
    with pytest.raises(ValueError, match="must be numeric"):
        ScoreWeights.from_mapping(
            {
                "yield_label_quality": True,
                "historical_depth": 20,
                "spatial_resolution": 15,
                "satellite_usability": 10,
                "license_and_redistribution": 10,
                "access_stability": 10,
            }
        )


def test_score_candidate_applies_approved_weighted_average() -> None:
    weights = ScoreWeights.approved()
    candidate = CandidateProfile(
        candidate_id="maize",
        candidate_type="crop",
        name="Maize",
        dimensions={name: 80 for name in weights.as_dict()},
        evidence_refs=("e1",),
        limitations=("example",),
    )
    assert score_candidate(candidate, weights) == pytest.approx(80.0)


def test_ranking_is_deterministic_for_ties() -> None:
    weights = ScoreWeights.approved()
    profiles = [
        CandidateProfile(
            candidate_id=value,
            candidate_type="crop",
            name=value.upper(),
            dimensions={name: 70 for name in weights.as_dict()},
            evidence_refs=("e1",),
            limitations=(),
        )
        for value in ("b", "a")
    ]
    assert [item.profile.candidate_id for item in rank_candidates(profiles, weights)] == [
        "a",
        "b",
    ]


def test_sensitivity_reports_stable_winner() -> None:
    approved = ScoreWeights.approved()
    profiles = [
        CandidateProfile(
            candidate_id="maize",
            candidate_type="crop",
            name="Maize",
            dimensions={name: 90 for name in approved.as_dict()},
            evidence_refs=("e1",),
            limitations=(),
        ),
        CandidateProfile(
            candidate_id="beans",
            candidate_type="crop",
            name="Beans",
            dimensions={name: 60 for name in approved.as_dict()},
            evidence_refs=("e1",),
            limitations=(),
        ),
    ]
    result = run_sensitivity_analysis(
        profiles,
        {
            "approved": approved,
            "labels_heavy": ScoreWeights(45, 15, 10, 10, 10, 10),
        },
    )
    assert result.winners == {"approved": "maize", "labels_heavy": "maize"}
    assert result.stable is True


def test_evidence_references_and_47_county_contract() -> None:
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    _, candidates = load_profiles(PROFILES_PATH)
    evidence_ids = {item["id"] for item in evidence["evidence"]}

    assert len({item.candidate_id for item in candidates}) == len(candidates)
    assert {item.candidate_type for item in candidates} == {"crop", "county"}
    assert len([item for item in candidates if item.candidate_type == "county"]) == 47
    assert len([item for item in candidates if item.candidate_type == "crop"]) == 4
    for candidate in candidates:
        assert set(candidate.dimensions) == set(DIMENSIONS)
        assert all(0 <= score <= 100 for score in candidate.dimensions.values())
        assert set(candidate.evidence_refs) <= evidence_ids


def test_generate_artifacts_selects_current_data_ranked_pair(tmp_path: Path) -> None:
    report_path = tmp_path / "docs" / "pilot-selection-decision.md"
    result = generate_artifacts(
        evidence_path=EVIDENCE_PATH,
        profiles_path=PROFILES_PATH,
        output_dir=tmp_path / "data",
        report_path=report_path,
    )
    selection = json.loads((tmp_path / "data/selection.json").read_text(encoding="utf-8"))
    scorecard = (tmp_path / "data/scorecard.csv").read_text(encoding="utf-8")
    report = report_path.read_text(encoding="utf-8")

    assert result.selected_crop == "maize"
    assert result.selected_county == "busia"
    assert selection["selected_crop"]["candidate_id"] == result.selected_crop
    assert selection["selected_county"]["candidate_id"] == result.selected_county
    assert selection["sensitivity"]["crop_winner_stable"] is True
    assert selection["sensitivity"]["county_winner_stable"] is True
    assert "maize,crop" in scorecard
    assert "busia,county" in scorecard
    assert "Maize" in report and "Busia" in report
    assert not (tmp_path / "data/pilot-selection-decision.md").exists()


def test_artifact_generation_is_byte_stable(tmp_path: Path) -> None:
    output_dir = tmp_path / "data"
    report_path = tmp_path / "docs" / "pilot-selection-decision.md"
    kwargs = {
        "evidence_path": EVIDENCE_PATH,
        "profiles_path": PROFILES_PATH,
        "output_dir": output_dir,
        "report_path": report_path,
    }
    generate_artifacts(**kwargs)
    first = {
        "scorecard.csv": (output_dir / "scorecard.csv").read_bytes(),
        "selection.json": (output_dir / "selection.json").read_bytes(),
        "pilot-selection-decision.md": report_path.read_bytes(),
    }
    generate_artifacts(**kwargs)
    second = {
        "scorecard.csv": (output_dir / "scorecard.csv").read_bytes(),
        "selection.json": (output_dir / "selection.json").read_bytes(),
        "pilot-selection-decision.md": report_path.read_bytes(),
    }
    assert first == second


def test_committed_artifacts_match_fresh_generation(tmp_path: Path) -> None:
    output_dir = tmp_path / "data"
    report_path = tmp_path / "docs" / "pilot-selection-decision.md"
    generate_artifacts(
        evidence_path=EVIDENCE_PATH,
        profiles_path=PROFILES_PATH,
        output_dir=output_dir,
        report_path=report_path,
    )

    expected_to_generated = {
        ROOT / "data/feasibility/scorecard.csv": output_dir / "scorecard.csv",
        ROOT / "data/feasibility/selection.json": output_dir / "selection.json",
        CANONICAL_REPORT_PATH: report_path,
    }
    for committed, generated in expected_to_generated.items():
        assert committed.read_bytes() == generated.read_bytes(), (
            f"{committed.relative_to(ROOT)} is stale; regenerate it with "
            "scripts/run_feasibility.py"
        )


def test_report_renders_registered_sensitivity_winners_dynamically(
    tmp_path: Path,
) -> None:
    payload = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    crop_dimensions = {
        "maize": {
            "yield_label_quality": 100,
            "historical_depth": 50,
            "spatial_resolution": 0,
            "satellite_usability": 50,
            "license_and_redistribution": 50,
            "access_stability": 50,
        },
        "beans": {
            "yield_label_quality": 50,
            "historical_depth": 50,
            "spatial_resolution": 100,
            "satellite_usability": 50,
            "license_and_redistribution": 50,
            "access_stability": 50,
        },
    }
    for crop in payload["crops"]:
        if crop["candidate_id"] in crop_dimensions:
            crop["dimensions"] = crop_dimensions[crop["candidate_id"]]
        else:
            crop["dimensions"] = {name: 0 for name in DIMENSIONS}
    profiles_path = tmp_path / "candidate_profiles.json"
    profiles_path.write_text(json.dumps(payload), encoding="utf-8")
    output_dir = tmp_path / "data"
    report_path = tmp_path / "pilot-selection-decision.md"

    generate_artifacts(
        evidence_path=EVIDENCE_PATH,
        profiles_path=profiles_path,
        output_dir=output_dir,
        report_path=report_path,
    )

    selection = json.loads((output_dir / "selection.json").read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    _, profiles = load_profiles(profiles_path)
    names = {profile.candidate_id: profile.name for profile in profiles}
    labels = {
        "approved": "Approved weights",
        "labels_heavy": "Labels-heavy",
        "spatial_heavy": "Spatial-heavy",
        "governance_heavy": "Governance-heavy",
    }

    assert selection["sensitivity"]["crop_winner_stable"] is False
    assert "At least one registered sensitivity scenario changes" in report
    for scenario, crop_id in selection["sensitivity"]["crop_winners"].items():
        county_id = selection["sensitivity"]["county_winners"][scenario]
        expected = f"- {labels[scenario]}: {names[crop_id].lower()} + {names[county_id]}"
        assert expected in report
