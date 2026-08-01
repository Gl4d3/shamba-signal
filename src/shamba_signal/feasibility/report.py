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


def load_profiles(path: Path) -> tuple[dict[str, Any], list[CandidateProfile]]:
    payload = _load_json(path)
    candidates = [CandidateProfile.from_mapping(item) for item in payload["crops"]]
    template = payload["county_template"]
    overrides = payload.get("county_overrides", {})
    for county in payload["counties"]:
        values = {
            "candidate_id": county["candidate_id"],
            "candidate_type": "county",
            "name": county["name"],
            **template,
            **overrides.get(county["candidate_id"], {}),
        }
        candidates.append(CandidateProfile.from_mapping(values))
    return payload, candidates


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


def _human_join(values: list[str]) -> str:
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return f"{', '.join(values[:-1])}, and {values[-1]}"


def generate_artifacts(
    *,
    evidence_path: Path,
    profiles_path: Path,
    output_dir: Path,
    report_path: Path | None = None,
) -> SelectionResult:
    evidence = _load_json(evidence_path)
    profile_payload, profiles = load_profiles(profiles_path)
    evidence_by_id = {item["id"]: item for item in evidence["evidence"]}
    evidence_ids = set(evidence_by_id)
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
    fallback_county = county_ranking[1]
    selection = {
        "selection_version": "0.1.0",
        "weights": weights.as_dict(),
        "selected_crop": _candidate_record(selected_crop),
        "selected_county": _candidate_record(selected_county),
        "runner_up_crop": _candidate_record(crop_ranking[1]),
        "runner_up_county": _candidate_record(fallback_county),
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
    score_sentence = (
        f"The approved weighted score selects {selected_crop.profile.name} at "
        f"**{selected_crop.score:.2f}/100** and {selected_county.profile.name} at "
        f"**{selected_county.score:.2f}/100**."
    )
    crop_reason = (
        f"{selected_crop.profile.name} has the strongest combination of county-level "
        "yield history, current official dashboard coverage, crop-calendar support, "
        "and compatibility with open satellite and crop-mask evidence."
    )
    county_evidence_sets = [set(item.profile.evidence_refs) for item in county_ranking]
    shared_county_evidence = set.intersection(*county_evidence_sets)
    selected_distinct_refs = [
        ref
        for ref in selected_county.profile.evidence_refs
        if ref not in shared_county_evidence
    ]
    selected_distinct_titles = [
        str(evidence_by_id[ref].get("title", ref)) for ref in selected_distinct_refs
    ]
    if selected_distinct_titles:
        county_reason = (
            f"{selected_county.profile.name} adds distinct registered evidence: "
            f"{_human_join(selected_distinct_titles)}. It also retains the shared "
            "county-yield, climate, soil, boundary, calendar, and satellite evidence "
            "used to compare all counties."
        )
    else:
        county_reason = (
            f"{selected_county.profile.name} ranks highest on the registered feasibility "
            "dimensions, but the current register contains no county-exclusive source "
            "for it. Slice 2 must therefore validate the shared evidence directly."
        )
    fallback_reason = (
        f"{fallback_county.profile.name} remains the first fallback at "
        f"**{fallback_county.score:.2f}/100**. Its profile retains the shared evidence "
        "set and becomes the pilot if the selected county fails the measured gates."
    )
    evidence_sentence = (
        "The machine-readable evidence register records publisher, URL, coverage, access "
        "method, licensing status and unresolved work."
    )
    scenario_labels = {
        "approved": "Approved weights",
        "labels_heavy": "Labels-heavy",
        "spatial_heavy": "Spatial-heavy",
        "governance_heavy": "Governance-heavy",
    }
    profile_names = {profile.candidate_id: profile.name for profile in profiles}
    sensitivity_rows = "\n".join(
        (
            f"- {scenario_labels[scenario]}: "
            f"{profile_names[crop_sensitivity.winners[scenario]].lower()} + "
            f"{profile_names[county_sensitivity.winners[scenario]]}"
        )
        for scenario in scenarios
    )
    if crop_sensitivity.stable and county_sensitivity.stable:
        sensitivity_intro = (
            "The winner remains unchanged in all four registered scenarios:"
        )
    else:
        sensitivity_intro = (
            "At least one registered sensitivity scenario changes the selected pair:"
        )
    switch_instruction = (
        f"5. Switch to {fallback_county.profile.name} if "
        f"{selected_county.profile.name} fails label completeness, geographic overlap "
        "or observation thresholds."
    )
    report = f"""# Pilot Selection Decision

## Decision

- **MVP crop:** {selected_crop.profile.name}
- **Deep-dive county:** {selected_county.profile.name}
- **Fallback county:** {fallback_county.profile.name}
- **Decision status:** selected for Slice 2, subject to snapshot-level completeness checks

{score_sentence}

## Crop ranking

| Rank | Crop | Score |
|---:|---|---:|
{top_crops}

## County ranking

| Rank | County | Score |
|---:|---|---:|
{top_counties}

## Why this pair

{crop_reason}

{county_reason}

{fallback_reason}

## Sensitivity

{sensitivity_intro}

{sensitivity_rows}

The exact profiles and scenario weights are versioned in `data/feasibility/`.

## Source evidence

The audit records twelve public sources, including:

- KilimoSTAT county crop statistics and metadata
- KNBS/NIPFN maize production by county, 2012–2020
- Kenya Food Systems Dashboard maize and beans yield indicators
- Kenya Space Agency/AfriCultuReS crop calendars
- PlantVillage Crop Type Kenya
- NASA Harvest crop maps
- Sentinel-2 Level-2A
- CHIRPS v3
- SoilGrids
- ICPAC county boundaries

{evidence_sentence}

## Required validation before modelling

1. Download and checksum the official maize county records.
2. Profile county-year completeness, flags, units and reported-versus-derived yield.
3. Measure Sentinel-2 and Sentinel-1 observation availability by forecast cutoff.
4. Confirm the exact spatial overlap and class distribution of the western Kenya crop-type labels.
{switch_instruction}

## Scientific limits

- The scorecard ranks **data feasibility**, not expected model accuracy.
- The validated target remains **county × crop × season**.
- Pixel and ward products remain **relative yield potential** and **crop-stress indicators**.
- No source with unresolved redistribution terms is bundled into the repository.
- County label scores are metadata-level estimates until Slice 2 profiles the downloaded records.
"""
    destination = report_path or output_dir / "pilot-selection-decision.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(report, encoding="utf-8")
    return SelectionResult(
        selected_crop=selected_crop.profile.candidate_id,
        selected_county=selected_county.profile.candidate_id,
    )
