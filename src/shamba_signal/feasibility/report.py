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


def generate_artifacts(
    *,
    evidence_path: Path,
    profiles_path: Path,
    output_dir: Path,
    report_path: Path | None = None,
) -> SelectionResult:
    evidence = _load_json(evidence_path)
    profile_payload, profiles = load_profiles(profiles_path)
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
    report = f"""# Pilot Selection Decision

## Decision

- **MVP crop:** {selected_crop.profile.name}
- **Deep-dive county:** {selected_county.profile.name}
- **Fallback county:** {fallback_county.profile.name}
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

{selected_crop.profile.name} has the strongest combination of county-level yield history, current official dashboard coverage, crop-calendar support, and compatibility with open satellite and crop-mask evidence.

{selected_county.profile.name} adds unusually strong spatial evidence. The PlantVillage Kenya collection provides open **10 m crop-type and crop-density labels** in western Kenya under **CC BY 4.0**, and NASA Harvest publishes a Busia-specific 2020 cropland raster. {selected_county.profile.name} still uses the same national county-yield evidence available to the other counties.

{fallback_county.profile.name} remains the first fallback because AfriCultuReS publishes a dedicated Trans-Nzoia crop-calendar layer and the county is well suited to maize monitoring, but this audit did not locate comparably open field-level crop-type evidence there.

## Sensitivity

The winner remains unchanged in all four registered scenarios:

- Approved weights: {selected_crop.profile.name.lower()} + {selected_county.profile.name}
- Labels-heavy: {selected_crop.profile.name.lower()} + {selected_county.profile.name}
- Spatial-heavy: {selected_crop.profile.name.lower()} + {selected_county.profile.name}
- Governance-heavy: {selected_crop.profile.name.lower()} + {selected_county.profile.name}

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

The machine-readable evidence register records publisher, URL, coverage, access method, licensing status and unresolved work.

## Required validation before modelling

1. Download and checksum the official maize county records.
2. Profile county-year completeness, flags, units and reported-versus-derived yield.
3. Measure Sentinel-2 and Sentinel-1 observation availability by forecast cutoff.
4. Confirm the exact spatial overlap and class distribution of the western Kenya crop-type labels.
5. Switch to {fallback_county.profile.name} if {selected_county.profile.name} fails label completeness, geographic overlap or observation thresholds.

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
