from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import CandidateProfile, ScoreWeights
from .scoring import RankedCandidate, rank_candidates, run_sensitivity_analysis


@dataclass(frozen=True)
class SelectionResult:
    selected_crop: str
    selected_county: str


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _scenarios() -> dict[str, ScoreWeights]:
    return {
        "approved": ScoreWeights.approved(),
        "labels_heavy": ScoreWeights(45, 15, 10, 10, 10, 10),
        "spatial_heavy": ScoreWeights(30, 15, 25, 10, 10, 10),
        "governance_heavy": ScoreWeights(30, 15, 15, 10, 15, 15),
    }


def _candidate_record(item: RankedCandidate) -> dict[str, Any]:
    return {
        "candidate_id": item.profile.candidate_id,
        "name": item.profile.name,
        "score": item.score,
        "dimensions": dict(item.profile.dimensions),
        "evidence_refs": list(item.profile.evidence_refs),
        "limitations": list(item.profile.limitations),
    }


def generate_artifacts(
    *, evidence_path: Path, profiles_path: Path, output_dir: Path
) -> SelectionResult:
    evidence = _load_json(evidence_path)
    profile_payload = _load_json(profiles_path)
    profiles = [CandidateProfile.from_mapping(item) for item in profile_payload["candidates"]]
    evidence_ids = {item["id"] for item in evidence["evidence"]}
    for profile in profiles:
        missing = set(profile.evidence_refs) - evidence_ids
        if missing:
            raise ValueError(
                f"unknown evidence references for {profile.candidate_id}: {sorted(missing)}"
            )

    weights = ScoreWeights.from_mapping(profile_payload["weights"])
    crops = [item for item in profiles if item.candidate_type == "crop"]
    counties = [item for item in profiles if item.candidate_type == "county"]
    crop_ranking = rank_candidates(crops, weights)
    county_ranking = rank_candidates(counties, weights)
    scenarios = _scenarios()
    crop_sensitivity = run_sensitivity_analysis(crops, scenarios)
    county_sensitivity = run_sensitivity_analysis(counties, scenarios)

    output_dir.mkdir(parents=True, exist_ok=True)
    scorecard_path = output_dir / "scorecard.csv"
    with scorecard_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "candidate_id",
                "candidate_type",
                "name",
                "weighted_score",
                *weights.as_dict().keys(),
            ]
        )
        ordered = sorted(
            crop_ranking + county_ranking,
            key=lambda row: (row.profile.candidate_type, -row.score, row.profile.candidate_id),
        )
        for item in ordered:
            writer.writerow(
                [
                    item.profile.candidate_id,
                    item.profile.candidate_type,
                    item.profile.name,
                    f"{item.score:.4f}",
                    *[
                        f"{float(item.profile.dimensions[name]):.1f}"
                        for name in weights.as_dict()
                    ],
                ]
            )

    selected_crop = crop_ranking[0]
    selected_county = county_ranking[0]
    selection = {
        "selection_version": "0.1.0",
        "weights": weights.as_dict(),
        "selected_crop": _candidate_record(selected_crop),
        "selected_county": _candidate_record(selected_county),
        "runner_up_crop": _candidate_record(crop_ranking[1]),
        "runner_up_county": _candidate_record(county_ranking[1]),
        "sensitivity": {
            "scenarios": {name: value.as_dict() for name, value in scenarios.items()},
            "crop_winners": dict(crop_sensitivity.winners),
            "county_winners": dict(county_sensitivity.winners),
            "crop_winner_stable": crop_sensitivity.stable,
            "county_winner_stable": county_sensitivity.stable,
        },
        "decision_status": "selected-for-slice-2-with-source-snapshot-validation",
        "non_claims": [
            "This scorecard does not prove model skill.",
            "County yield-label completeness must be re-measured from downloaded source snapshots.",
            "Optical observation usability must be measured before feature production.",
        ],
    }
    (output_dir / "selection.json").write_text(
        json.dumps(selection, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    top_counties = "\n".join(
        f"| {index} | {item.profile.name} | {item.score:.2f} |"
        for index, item in enumerate(county_ranking[:5], start=1)
    )
    top_crops = "\n".join(
        f"| {index} | {item.profile.name} | {item.score:.2f} |"
        for index, item in enumerate(crop_ranking, start=1)
    )
    report = f"""# Pilot Selection Decision

## Decision

- **MVP crop:** {selected_crop.profile.name}
- **Deep-dive county:** {selected_county.profile.name}
- **Decision status:** selected for Slice 2, subject to snapshot-level completeness checks

The approved weighted score selects {selected_crop.profile.name} at **{selected_crop.score:.2f}/100** and {selected_county.profile.name} at **{selected_county.score:.2f}/100**.

## Crop ranking

| Rank | Crop | Score |
|---:|---|---:|
{top_crops}

## County ranking

| Rank | County | Score |
|---:|---|---:|
{top_counties}

## Why this pair

{selected_crop.profile.name} has the strongest combination of county-level yield history, current official dashboard coverage, crop-calendar support, and compatibility with open satellite/crop-mask evidence. {selected_county.profile.name} adds unusually strong spatial evidence: open 10 m crop-type ground truth in western Kenya and a Busia-specific cropland map, while retaining the national county-yield evidence used by the other counties.

## Sensitivity

- Crop winner stable across all scenarios: **{str(crop_sensitivity.stable).lower()}**
- County winner stable across all scenarios: **{str(county_sensitivity.stable).lower()}**
- Crop winners: `{json.dumps(dict(crop_sensitivity.winners), sort_keys=True)}`
- County winners: `{json.dumps(dict(county_sensitivity.winners), sort_keys=True)}`

## Required validation before modelling

1. Download and checksum the official maize county records.
2. Profile county-year completeness, flags, units, and reported-versus-derived yield.
3. Measure Sentinel-2 and Sentinel-1 observation availability by forecast cutoff.
4. Confirm the exact spatial overlap and class distribution of the western Kenya crop-type labels.
5. Retain Trans Nzoia as the first fallback county if Busia fails label or observation thresholds.

## Scientific limits

- The scorecard ranks data feasibility, not expected model accuracy.
- The validated target remains county × crop × season.
- Pixel and ward products remain relative yield potential and crop-stress indicators.
- No source with unresolved redistribution terms is bundled into the repository.
"""
    (output_dir / "pilot-selection-decision.md").write_text(report, encoding="utf-8")
    return SelectionResult(
        selected_crop=selected_crop.profile.candidate_id,
        selected_county=selected_county.profile.candidate_id,
    )
