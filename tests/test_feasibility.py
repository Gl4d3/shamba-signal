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


def test_weights_must_sum_to_100() -> None:
    with pytest.raises(ValueError, match="sum to 100"):
        ScoreWeights(35, 20, 15, 10, 10, 9)


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
    evidence = json.loads((ROOT / "data/feasibility/evidence.json").read_text())
    _, candidates = load_profiles(ROOT / "data/feasibility/candidate_profiles.json")
    evidence_ids = {item["id"] for item in evidence["evidence"]}

    assert len({item.candidate_id for item in candidates}) == len(candidates)
    assert {item.candidate_type for item in candidates} == {"crop", "county"}
    assert len([item for item in candidates if item.candidate_type == "county"]) == 47
    for candidate in candidates:
        assert set(candidate.dimensions) == set(DIMENSIONS)
        assert all(0 <= score <= 100 for score in candidate.dimensions.values())
        assert set(candidate.evidence_refs) <= evidence_ids


def test_generate_artifacts_selects_maize_and_busia(tmp_path: Path) -> None:
    result = generate_artifacts(
        evidence_path=ROOT / "data/feasibility/evidence.json",
        profiles_path=ROOT / "data/feasibility/candidate_profiles.json",
        output_dir=tmp_path,
    )
    selection = json.loads((tmp_path / "selection.json").read_text())
    scorecard = (tmp_path / "scorecard.csv").read_text()
    report = (tmp_path / "pilot-selection-decision.md").read_text()

    assert result.selected_crop == "maize"
    assert result.selected_county == "busia"
    assert selection["selected_crop"]["candidate_id"] == "maize"
    assert selection["selected_county"]["candidate_id"] == "busia"
    assert selection["sensitivity"]["crop_winner_stable"] is True
    assert selection["sensitivity"]["county_winner_stable"] is True
    assert "maize,crop" in scorecard
    assert "busia,county" in scorecard
    assert "Maize" in report and "Busia" in report


def test_artifact_generation_is_byte_stable(tmp_path: Path) -> None:
    kwargs = {
        "evidence_path": ROOT / "data/feasibility/evidence.json",
        "profiles_path": ROOT / "data/feasibility/candidate_profiles.json",
        "output_dir": tmp_path,
    }
    generate_artifacts(**kwargs)
    first = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    generate_artifacts(**kwargs)
    second = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    assert first == second
