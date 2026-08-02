from __future__ import annotations

import csv
import io
import json
import math
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from typing import Literal

from shamba_signal.datasets.target import (
    CanonicalObservation,
    ObservationQuality,
    ReconciliationStatus,
    TargetKey,
    derive_yield,
    index_observations,
    reconcile_yield,
)

TargetStatus = ReconciliationStatus | Literal["missing"]
PilotStatus = Literal["confirmed", "fallback", "insufficient"]
_CANONICAL_UNITS = {
    "production": "t",
    "harvested_area": "ha",
    "reported_yield": "t/ha",
}
_QUALITY_ORDER: dict[ObservationQuality, int] = {
    "accepted": 0,
    "flagged": 1,
    "review-required": 2,
}


@dataclass(frozen=True)
class TargetRow:
    key: TargetKey
    county_name: str
    production_t: float | None
    harvested_area_ha: float | None
    reported_yield_t_per_ha: float | None
    derived_yield_t_per_ha: float | None
    reconciliation_status: TargetStatus
    absolute_difference_t_per_ha: float | None
    quality_class: ObservationQuality
    source_flags: tuple[str, ...]
    snapshot_ids: tuple[str, ...]
    publishable_label: bool


@dataclass(frozen=True)
class CountyQuality:
    county_id: str
    target_rows: int
    periods: tuple[str, ...]
    rows_with_label: int
    review_required_rows: int
    divergent_rows: int

    @property
    def yield_coverage(self) -> float:
        return self.rows_with_label / self.target_rows if self.target_rows else 0.0

    @property
    def review_required_fraction(self) -> float:
        return self.review_required_rows / self.target_rows if self.target_rows else 0.0

    @property
    def divergent_fraction(self) -> float:
        return self.divergent_rows / self.target_rows if self.target_rows else 0.0


@dataclass(frozen=True)
class QualityReport:
    total_observations: int
    target_rows: int
    rows_with_reported_yield: int
    rows_with_derived_yield: int
    rows_missing_yield: int
    rows_consistent: int
    rows_divergent: int
    quality_counts: dict[str, int]
    source_flag_counts: dict[str, int]
    canonical_units: dict[str, str]
    duplicate_policy: str
    county_quality: tuple[CountyQuality, ...]


@dataclass(frozen=True)
class TargetDatasetBuild:
    rows: tuple[TargetRow, ...]
    report: QualityReport


def _row_quality(observations: Sequence[CanonicalObservation]) -> ObservationQuality:
    return max(
        (item.quality_class for item in observations),
        key=lambda value: _QUALITY_ORDER[value],
    )


def build_target_dataset(
    observations: Iterable[CanonicalObservation],
) -> TargetDatasetBuild:
    items = tuple(observations)
    indexed = index_observations(items)
    keys = sorted(
        {key for key, _ in indexed},
        key=lambda key: (key.county_id, key.crop_id, key.period_id),
    )
    rows: list[TargetRow] = []
    for key in keys:
        group = [item for item in items if item.key == key]
        production = indexed.get((key, "production"))
        area = indexed.get((key, "harvested_area"))
        reported = indexed.get((key, "reported_yield"))
        derived = derive_yield(production, area) if production and area else None
        if reported is None and derived is None:
            status: TargetStatus = "missing"
            reported_value = None
            derived_value = None
            difference = None
        else:
            reconciliation = reconcile_yield(reported=reported, derived=derived)
            status = reconciliation.status
            reported_value = reconciliation.reported_yield_t_per_ha
            derived_value = reconciliation.derived_yield_t_per_ha
            difference = reconciliation.absolute_difference_t_per_ha
        rows.append(
            TargetRow(
                key=key,
                county_name=group[0].county_name,
                production_t=production.normalized_value if production else None,
                harvested_area_ha=area.normalized_value if area else None,
                reported_yield_t_per_ha=reported_value,
                derived_yield_t_per_ha=derived_value,
                reconciliation_status=status,
                absolute_difference_t_per_ha=difference,
                quality_class=_row_quality(group),
                source_flags=tuple(
                    sorted({item.source_flag for item in group if item.source_flag})
                ),
                snapshot_ids=tuple(sorted({item.snapshot_id for item in group})),
                publishable_label=status
                in {"reported_only", "derived_only", "consistent"},
            )
        )
    report = _quality_report(items, rows)
    return TargetDatasetBuild(rows=tuple(rows), report=report)


def _quality_report(
    observations: Sequence[CanonicalObservation],
    rows: Sequence[TargetRow],
) -> QualityReport:
    quality_counts = {quality: 0 for quality in _QUALITY_ORDER}
    for row in rows:
        quality_counts[row.quality_class] += 1
    county_ids = sorted({row.key.county_id for row in rows})
    counties: list[CountyQuality] = []
    for county_id in county_ids:
        county_rows = [row for row in rows if row.key.county_id == county_id]
        counties.append(
            CountyQuality(
                county_id=county_id,
                target_rows=len(county_rows),
                periods=tuple(sorted({row.key.period_id for row in county_rows})),
                rows_with_label=sum(row.publishable_label for row in county_rows),
                review_required_rows=sum(
                    row.quality_class == "review-required" for row in county_rows
                ),
                divergent_rows=sum(
                    row.reconciliation_status == "divergent" for row in county_rows
                ),
            )
        )
    source_flag_counts: dict[str, int] = {}
    for item in observations:
        if item.source_flag:
            source_flag_counts[item.source_flag] = (
                source_flag_counts.get(item.source_flag, 0) + 1
            )
    return QualityReport(
        total_observations=len(observations),
        target_rows=len(rows),
        rows_with_reported_yield=sum(
            row.reported_yield_t_per_ha is not None for row in rows
        ),
        rows_with_derived_yield=sum(
            row.derived_yield_t_per_ha is not None for row in rows
        ),
        rows_missing_yield=sum(row.reconciliation_status == "missing" for row in rows),
        rows_consistent=sum(row.reconciliation_status == "consistent" for row in rows),
        rows_divergent=sum(row.reconciliation_status == "divergent" for row in rows),
        quality_counts=quality_counts,
        source_flag_counts=dict(sorted(source_flag_counts.items())),
        canonical_units=dict(_CANONICAL_UNITS),
        duplicate_policy="fail",
        county_quality=tuple(counties),
    )


def _format_number(value: float | None) -> str:
    return "" if value is None else format(value, ".12g")


def render_target_csv(rows: Sequence[TargetRow]) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        [
            "county_id",
            "county_name",
            "crop_id",
            "period_id",
            "production_t",
            "harvested_area_ha",
            "reported_yield_t_per_ha",
            "derived_yield_t_per_ha",
            "reconciliation_status",
            "quality_class",
            "publishable_label",
            "source_flags",
            "snapshot_ids",
        ]
    )
    for row in sorted(
        rows,
        key=lambda item: (item.key.county_id, item.key.crop_id, item.key.period_id),
    ):
        writer.writerow(
            [
                row.key.county_id,
                row.county_name,
                row.key.crop_id,
                row.key.period_id,
                _format_number(row.production_t),
                _format_number(row.harvested_area_ha),
                _format_number(row.reported_yield_t_per_ha),
                _format_number(row.derived_yield_t_per_ha),
                row.reconciliation_status,
                row.quality_class,
                str(row.publishable_label).lower(),
                "|".join(row.source_flags),
                "|".join(row.snapshot_ids),
            ]
        )
    return output.getvalue()


def render_quality_json(report: QualityReport) -> str:
    return json.dumps(asdict(report), indent=2, sort_keys=True) + "\n"


@dataclass(frozen=True)
class PilotGatePolicy:
    minimum_periods: int
    minimum_yield_coverage: float
    maximum_review_required_fraction: float
    maximum_divergent_fraction: float

    def __post_init__(self) -> None:
        if isinstance(self.minimum_periods, bool) or self.minimum_periods <= 0:
            raise ValueError("minimum_periods must be a positive integer")
        for name in (
            "minimum_yield_coverage",
            "maximum_review_required_fraction",
            "maximum_divergent_fraction",
        ):
            value = getattr(self, name)
            if (
                isinstance(value, bool)
                or not isinstance(value, int | float)
                or not math.isfinite(value)
                or not 0 <= value <= 1
            ):
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True)
class PilotDecision:
    status: PilotStatus
    selected_county_id: str | None
    primary_failures: tuple[str, ...]
    fallback_failures: tuple[str, ...]


def _gate_failures(
    county: CountyQuality | None,
    policy: PilotGatePolicy,
) -> tuple[str, ...]:
    if county is None:
        return ("county has no target rows",)
    failures: list[str] = []
    if len(county.periods) < policy.minimum_periods:
        failures.append(
            f"periods {len(county.periods)} below minimum {policy.minimum_periods}"
        )
    if county.yield_coverage < policy.minimum_yield_coverage:
        failures.append(
            "yield coverage "
            f"{county.yield_coverage:.3f} below {policy.minimum_yield_coverage:.3f}"
        )
    if county.review_required_fraction > policy.maximum_review_required_fraction:
        failures.append(
            "review-required fraction "
            f"{county.review_required_fraction:.3f} above "
            f"{policy.maximum_review_required_fraction:.3f}"
        )
    if county.divergent_fraction > policy.maximum_divergent_fraction:
        failures.append(
            "divergent fraction "
            f"{county.divergent_fraction:.3f} above "
            f"{policy.maximum_divergent_fraction:.3f}"
        )
    return tuple(failures)


def evaluate_pilot(
    report: QualityReport,
    *,
    primary_county_id: str,
    fallback_county_id: str,
    policy: PilotGatePolicy,
) -> PilotDecision:
    counties = {item.county_id: item for item in report.county_quality}
    primary_failures = _gate_failures(counties.get(primary_county_id), policy)
    fallback_failures = _gate_failures(counties.get(fallback_county_id), policy)
    if not primary_failures:
        return PilotDecision(
            status="confirmed",
            selected_county_id=primary_county_id,
            primary_failures=(),
            fallback_failures=fallback_failures,
        )
    if not fallback_failures:
        return PilotDecision(
            status="fallback",
            selected_county_id=fallback_county_id,
            primary_failures=primary_failures,
            fallback_failures=(),
        )
    return PilotDecision(
        status="insufficient",
        selected_county_id=None,
        primary_failures=primary_failures,
        fallback_failures=fallback_failures,
    )
