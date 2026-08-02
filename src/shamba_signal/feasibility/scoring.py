from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .models import CandidateProfile, ScoreWeights


@dataclass(frozen=True)
class RankedCandidate:
    profile: CandidateProfile
    score: float


@dataclass(frozen=True)
class SensitivityResult:
    winners: Mapping[str, str]
    stable: bool


def score_candidate(profile: CandidateProfile, weights: ScoreWeights) -> float:
    total = sum(
        float(profile.dimensions[name]) * weight
        for name, weight in weights.as_dict().items()
    )
    return round(total / 100, 4)


def rank_candidates(
    profiles: Iterable[CandidateProfile], weights: ScoreWeights
) -> list[RankedCandidate]:
    ranked = [
        RankedCandidate(profile=item, score=score_candidate(item, weights))
        for item in profiles
    ]
    return sorted(ranked, key=lambda item: (-item.score, item.profile.candidate_id))


def run_sensitivity_analysis(
    profiles: Iterable[CandidateProfile], scenarios: Mapping[str, ScoreWeights]
) -> SensitivityResult:
    materialized = tuple(profiles)
    winners = {
        scenario: rank_candidates(materialized, weights)[0].profile.candidate_id
        for scenario, weights in scenarios.items()
    }
    return SensitivityResult(winners=winners, stable=len(set(winners.values())) == 1)
