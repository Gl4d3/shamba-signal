from __future__ import annotations

import csv
import io
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from shamba_signal.datasets.target import CanonicalObservation
from shamba_signal.datasets.target_build import TargetRow, build_target_dataset

ModellingSplit = Literal["train", "validation", "test"]
LabelMethod = Literal["reported", "derived", "unusable"]


@dataclass(frozen=True)
class ModellingLabelRow:
    county_id: str
    county_name: str
    year: int
    production_t: float | None
    harvested_area_ha: float | None
    active_yield_t_per_ha: float | None
    label_method: LabelMethod
    reconciliation_status: str
    source_vintage: str
    source_snapshot_id: str
    provisional: bool
    split: ModellingSplit
    usable_for_modelling: bool


@dataclass(frozen=True)
class RevisionComparison:
    county_id: str
    historical_area_ha: float
    revision_area_ha: float
    area_relative_difference: float
    historical_production_t: float
    revision_production_t: float
    production_relative_difference: float
    materially_different: bool


def _year(row: TargetRow) -> int:
    try:
        return int(row.key.period_id)
    except ValueError as exc:
        raise ValueError(f"modelling panel period must be a year: {row.key.period_id}") from exc


def _active_label(row: TargetRow) -> tuple[float | None, LabelMethod]:
    if row.reconciliation_status in {"consistent", "reported_only"}:
        return row.reported_yield_t_per_ha, "reported"
    if row.reconciliation_status == "derived_only":
        return row.derived_yield_t_per_ha, "derived"
    return None, "unusable"


def _split(year: int) -> ModellingSplit:
    if year <= 2021:
        return "train"
    if year == 2022:
        return "validation"
    return "test"


def build_modelling_panel(
    historical_observations: Sequence[CanonicalObservation],
    report_observations: Sequence[CanonicalObservation],
) -> tuple[ModellingLabelRow, ...]:
    """Build the active panel: workbook through 2018, report from 2019 onward."""
    active_observations = tuple(
        item for item in historical_observations if int(item.key.period_id) <= 2018
    ) + tuple(item for item in report_observations if int(item.key.period_id) >= 2019)
    target = build_target_dataset(active_observations)
    rows: list[ModellingLabelRow] = []
    for target_row in target.rows:
        year = _year(target_row)
        if len(target_row.snapshot_ids) != 1:
            raise ValueError("active county-year row must bind to exactly one source snapshot")
        label, method = _active_label(target_row)
        rows.append(
            ModellingLabelRow(
                county_id=target_row.key.county_id,
                county_name=target_row.county_name,
                year=year,
                production_t=target_row.production_t,
                harvested_area_ha=target_row.harvested_area_ha,
                active_yield_t_per_ha=label,
                label_method=method,
                reconciliation_status=target_row.reconciliation_status,
                source_vintage=(
                    "nipfn-workbook-2012-2020" if year <= 2018 else "knbs-report-2024"
                ),
                source_snapshot_id=target_row.snapshot_ids[0],
                provisional="provisional" in target_row.source_flags,
                split=_split(year),
                usable_for_modelling=label is not None,
            )
        )
    return tuple(sorted(rows, key=lambda item: (item.year, item.county_id)))


def _required_value(value: float | None, *, field: str) -> float:
    if value is None:
        raise ValueError(f"revision comparison requires {field}")
    return value


def _relative_difference(original: float, revision: float) -> float:
    if original == 0:
        return 0.0 if revision == 0 else float("inf")
    return abs(revision - original) / abs(original)


def compare_revision_year(
    historical_observations: Sequence[CanonicalObservation],
    report_observations: Sequence[CanonicalObservation],
    *,
    year: int,
    materiality_threshold: float = 0.001,
) -> tuple[RevisionComparison, ...]:
    """Compare overlapping area and production without overwriting either vintage."""
    if materiality_threshold < 0:
        raise ValueError("materiality threshold must be non-negative")
    historical = {
        row.key.county_id: row
        for row in build_target_dataset(
            item for item in historical_observations if item.key.period_id == str(year)
        ).rows
    }
    revision = {
        row.key.county_id: row
        for row in build_target_dataset(
            item for item in report_observations if item.key.period_id == str(year)
        ).rows
    }
    if historical.keys() != revision.keys() or not historical:
        raise ValueError("revision comparison requires matching county coverage")
    comparisons: list[RevisionComparison] = []
    for county_id in sorted(historical):
        old = historical[county_id]
        new = revision[county_id]
        old_area = _required_value(old.harvested_area_ha, field="historical area")
        new_area = _required_value(new.harvested_area_ha, field="revision area")
        old_production = _required_value(old.production_t, field="historical production")
        new_production = _required_value(new.production_t, field="revision production")
        area_difference = _relative_difference(old_area, new_area)
        production_difference = _relative_difference(old_production, new_production)
        comparisons.append(
            RevisionComparison(
                county_id=county_id,
                historical_area_ha=old_area,
                revision_area_ha=new_area,
                area_relative_difference=area_difference,
                historical_production_t=old_production,
                revision_production_t=new_production,
                production_relative_difference=production_difference,
                materially_different=max(area_difference, production_difference)
                > materiality_threshold,
            )
        )
    return tuple(comparisons)


def _format_number(value: float | None) -> str:
    return "" if value is None else format(value, ".12g")


def render_modelling_panel_csv(rows: Sequence[ModellingLabelRow]) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        [
            "county_id",
            "county_name",
            "year",
            "production_t",
            "harvested_area_ha",
            "active_yield_t_per_ha",
            "label_method",
            "reconciliation_status",
            "source_vintage",
            "source_snapshot_id",
            "provisional",
            "split",
            "usable_for_modelling",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row.county_id,
                row.county_name,
                row.year,
                _format_number(row.production_t),
                _format_number(row.harvested_area_ha),
                _format_number(row.active_yield_t_per_ha),
                row.label_method,
                row.reconciliation_status,
                row.source_vintage,
                row.source_snapshot_id,
                str(row.provisional).lower(),
                row.split,
                str(row.usable_for_modelling).lower(),
            ]
        )
    return output.getvalue()
