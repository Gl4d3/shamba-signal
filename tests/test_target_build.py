import json
from pathlib import Path

import pytest

from shamba_signal.datasets.target import CanonicalObservation, load_county_registry
from shamba_signal.datasets.target_build import (
    PilotGatePolicy,
    build_target_dataset,
    evaluate_pilot,
    render_quality_json,
    render_target_csv,
)


def registry():
    return load_county_registry(Path("tests/fixtures/county_profiles.json"))


def obs(
    *,
    county: str,
    period: str,
    element: str,
    value: float,
    unit: str,
    quality: str = "accepted",
    snapshot: str = "snapshot-a",
) -> CanonicalObservation:
    return CanonicalObservation.create(
        registry=registry(),
        county=county,
        crop="maize",
        period_id=period,
        element=element,
        value=value,
        unit=unit,
        source_name="fixture",
        source_flag=None,
        quality_class=quality,
        snapshot_id=snapshot,
    )


def complete_period(county: str, period: str, *, quality: str = "accepted"):
    return [
        obs(
            county=county,
            period=period,
            element="production",
            value=20,
            unit="t",
            quality=quality,
        ),
        obs(
            county=county,
            period=period,
            element="harvested_area",
            value=10,
            unit="ha",
            quality=quality,
        ),
        obs(
            county=county,
            period=period,
            element="reported_yield",
            value=2.0,
            unit="t/ha",
            quality=quality,
        ),
    ]


def test_build_target_dataset_groups_observations_and_reports_quality() -> None:
    observations = [
        *complete_period("Busia", "2022"),
        *complete_period("Busia", "2023", quality="flagged"),
        obs(county="Trans Nzoia", period="2023", element="production", value=30, unit="t"),
    ]

    result = build_target_dataset(observations)

    assert [row.key.period_id for row in result.rows if row.key.county_id == "busia"] == [
        "2022",
        "2023",
    ]
    busia_2023 = next(
        row
        for row in result.rows
        if row.key.period_id == "2023" and row.key.county_id == "busia"
    )
    assert busia_2023.reported_yield_t_per_ha == pytest.approx(2.0)
    assert busia_2023.derived_yield_t_per_ha == pytest.approx(2.0)
    assert busia_2023.reconciliation_status == "consistent"
    assert busia_2023.quality_class == "flagged"

    missing = next(row for row in result.rows if row.key.county_id == "trans_nzoia")
    assert missing.reconciliation_status == "missing"
    assert missing.publishable_label is False

    assert result.report.total_observations == 7
    assert result.report.target_rows == 3
    assert result.report.rows_with_reported_yield == 2
    assert result.report.rows_with_derived_yield == 2
    assert result.report.rows_missing_yield == 1


def test_rendered_artifacts_are_deterministic_and_sorted() -> None:
    observations = [
        *complete_period("Trans Nzoia", "2023"),
        *complete_period("Busia", "2022"),
    ]
    first = build_target_dataset(observations)
    second = build_target_dataset(reversed(observations))

    assert render_target_csv(first.rows) == render_target_csv(second.rows)
    assert render_quality_json(first.report) == render_quality_json(second.report)
    assert render_target_csv(first.rows).splitlines()[1].startswith("busia,")
    parsed = json.loads(render_quality_json(first.report))
    assert parsed["target_rows"] == 2


def test_build_target_dataset_rejects_duplicate_elements() -> None:
    observations = [
        obs(county="Busia", period="2023", element="production", value=20, unit="t"),
        obs(county="Busia", period="2023", element="production", value=21, unit="t"),
    ]

    with pytest.raises(ValueError, match="duplicate canonical observation"):
        build_target_dataset(observations)


def test_pilot_gate_confirms_primary_only_when_explicit_policy_passes() -> None:
    observations = []
    for year in range(2019, 2024):
        observations.extend(complete_period("Busia", str(year)))
    result = build_target_dataset(observations)

    decision = evaluate_pilot(
        result.report,
        primary_county_id="busia",
        fallback_county_id="trans_nzoia",
        policy=PilotGatePolicy(
            minimum_periods=5,
            minimum_yield_coverage=0.8,
            maximum_review_required_fraction=0.2,
            maximum_divergent_fraction=0.2,
        ),
    )

    assert decision.status == "confirmed"
    assert decision.selected_county_id == "busia"


def test_pilot_gate_uses_fallback_when_primary_fails() -> None:
    observations = [
        obs(
            county="Busia",
            period="2023",
            element="reported_yield",
            value=2.0,
            unit="t/ha",
            quality="review-required",
        )
    ]
    for year in range(2019, 2024):
        observations.extend(complete_period("Trans Nzoia", str(year)))
    result = build_target_dataset(observations)

    decision = evaluate_pilot(
        result.report,
        primary_county_id="busia",
        fallback_county_id="trans_nzoia",
        policy=PilotGatePolicy(
            minimum_periods=5,
            minimum_yield_coverage=0.8,
            maximum_review_required_fraction=0.2,
            maximum_divergent_fraction=0.2,
        ),
    )

    assert decision.status == "fallback"
    assert decision.selected_county_id == "trans_nzoia"
    assert decision.primary_failures


def test_pilot_gate_returns_insufficient_when_neither_county_passes() -> None:
    result = build_target_dataset(
        [
            obs(
                county="Busia",
                period="2023",
                element="reported_yield",
                value=2,
                unit="t/ha",
            ),
            obs(
                county="Trans Nzoia",
                period="2023",
                element="reported_yield",
                value=2,
                unit="t/ha",
            ),
        ]
    )

    decision = evaluate_pilot(
        result.report,
        primary_county_id="busia",
        fallback_county_id="trans_nzoia",
        policy=PilotGatePolicy(
            minimum_periods=5,
            minimum_yield_coverage=0.8,
            maximum_review_required_fraction=0.2,
            maximum_divergent_fraction=0.2,
        ),
    )

    assert decision.status == "insufficient"
    assert decision.selected_county_id is None
    assert decision.primary_failures
    assert decision.fallback_failures
