from __future__ import annotations

import io
import re
from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from shamba_signal.datasets.target import CanonicalObservation, CountyRegistry

KNBS_REPORT_SHA256 = "7d86dc4cbfa1d0b5204e2428fb8d84c3bada0fc1775bf0b7d557dfebcc4d70eb"
KNBS_ANNEX_PAGE_INDEXES = (113, 114)
_EXPECTED_YEARS = frozenset(range(2019, 2024))
_EXPECTED_TOTALS = {
    2019: (2_207_325, 3_960_385),
    2020: (2_171_697, 3_795_175),
    2021: (2_168_603, 3_304_430),
    2022: (2_113_520, 3_087_220),
    2023: (2_430_013, 4_285_206),
}
_COUNTY_TEXT_CORRECTIONS = {"Kiliif": "Kilifi"}


@dataclass(frozen=True, order=True)
class KnbsAnnualMaizeRecord:
    county: str
    year: int
    harvested_area_ha: int
    production_tonnes: int
    provisional: bool


def _restore_text(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("KNBS annex contains an empty rotated-text cell")
    return " ".join(value[::-1].split())


def _restore_integer(value: object) -> int:
    restored = _restore_text(value).replace(",", "")
    if not re.fullmatch(r"[0-9]+", restored):
        raise ValueError(f"KNBS annex contains a non-integer value: {restored!r}")
    return int(restored)


def parse_knbs_annex_tables(
    tables: Sequence[Sequence[Sequence[object]]],
) -> tuple[KnbsAnnualMaizeRecord, ...]:
    """Restore county-year records from the report's rotated annex tables."""
    records: list[KnbsAnnualMaizeRecord] = []
    for table in tables:
        if len(table) < 3 or (len(table) - 1) % 2:
            raise ValueError("KNBS annex table must contain area/production row pairs")
        county_row = table[-1]
        if len(county_row) < 3 or _restore_text(county_row[1]) != "County":
            raise ValueError("KNBS annex table is missing its county row")
        for production_row, area_row in zip(table[:-1:2], table[1:-1:2], strict=True):
            if _restore_text(production_row[1]) != "(Tonnes) Production":
                raise ValueError("KNBS annex production row label is invalid")
            if _restore_text(area_row[1]) != "Area(Ha)":
                raise ValueError("KNBS annex area row label is invalid")
            year = _restore_integer(area_row[0])
            for column, raw_county in enumerate(county_row[2:], start=2):
                if raw_county is None:
                    continue
                county = _restore_text(raw_county)
                county = _COUNTY_TEXT_CORRECTIONS.get(county, county)
                if county == "Total":
                    continue
                if column >= len(production_row) or column >= len(area_row):
                    raise ValueError("KNBS annex table contains an incomplete county column")
                records.append(
                    KnbsAnnualMaizeRecord(
                        county=county,
                        year=year,
                        harvested_area_ha=_restore_integer(area_row[column]),
                        production_tonnes=_restore_integer(production_row[column]),
                        provisional=year == 2023,
                    )
                )
    return tuple(sorted(records, key=lambda item: (item.year, item.county)))


def validate_knbs_annex_records(records: Sequence[KnbsAnnualMaizeRecord]) -> None:
    """Fail closed unless extraction matches the published national panel."""
    if len(records) != 47 * 5:
        raise ValueError("KNBS annex must contain exactly 47 counties x 5 years")
    keys = {(record.county, record.year) for record in records}
    if len(keys) != len(records):
        raise ValueError("KNBS annex contains duplicate county-year records")
    years = {record.year for record in records}
    counties = {record.county for record in records}
    if years != _EXPECTED_YEARS or len(counties) != 47:
        raise ValueError("KNBS annex coverage does not match 47 counties x 2019-2023")
    for year, expected_totals in _EXPECTED_TOTALS.items():
        year_records = [record for record in records if record.year == year]
        actual_totals = (
            sum(record.harvested_area_ha for record in year_records),
            sum(record.production_tonnes for record in year_records),
        )
        if actual_totals != expected_totals:
            raise ValueError(
                f"KNBS annex {year} totals do not match the published national totals"
            )
        if any(record.provisional != (year == 2023) for record in year_records):
            raise ValueError("KNBS annex provisional flags do not match the report")


def canonicalize_knbs_maize_record(
    record: KnbsAnnualMaizeRecord,
    *,
    registry: CountyRegistry,
    snapshot_id: str,
) -> tuple[CanonicalObservation, CanonicalObservation]:
    """Map one report row into canonical area and production observations."""
    common = {
        "registry": registry,
        "county": record.county,
        "crop": "maize",
        "period_id": str(record.year),
        "source_name": "KNBS National Agriculture Production Report 2024",
        "source_flag": "provisional" if record.provisional else None,
        "quality_class": "accepted",
        "snapshot_id": snapshot_id,
    }
    return (
        CanonicalObservation.create(
            **common,
            element="harvested_area",
            value=record.harvested_area_ha,
            unit="ha",
            original_fields={"report_year": record.year, "provisional": record.provisional},
        ),
        CanonicalObservation.create(
            **common,
            element="production",
            value=record.production_tonnes,
            unit="tonnes",
            original_fields={"report_year": record.year, "provisional": record.provisional},
        ),
    )


def read_knbs_maize_annex(path: Path) -> tuple[KnbsAnnualMaizeRecord, ...]:
    """Verify and extract the 2019-2023 county maize annex from the KNBS report."""
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"could not read KNBS report PDF: {path}") from exc
    if sha256(payload).hexdigest() != KNBS_REPORT_SHA256:
        raise ValueError("KNBS report bytes do not match the accepted private candidate")

    try:
        import pdfplumber
    except ImportError as exc:  # pragma: no cover - dependency contract
        raise RuntimeError("pdfplumber is required to extract the KNBS annex") from exc

    with pdfplumber.open(io.BytesIO(payload)) as report:
        tables: list[Sequence[Sequence[Any]]] = []
        for page_index in KNBS_ANNEX_PAGE_INDEXES:
            extracted = report.pages[page_index].extract_tables()
            if len(extracted) != 1:
                raise ValueError(
                    f"KNBS annex page {page_index + 1} must contain exactly one table"
                )
            tables.append(extracted[0])
    records = parse_knbs_annex_tables(tables)
    validate_knbs_annex_records(records)
    return records
