from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from shamba_signal.datasets.nipfn import (
    canonicalize_nipfn_record,
    read_nipfn_workbook,
)
from shamba_signal.datasets.nipfn_publication import build_nipfn_publication
from shamba_signal.datasets.target import load_county_registry
from shamba_signal.datasets.target_build import PilotGatePolicy


def registry():
    return load_county_registry(Path("tests/fixtures/county_profiles.json"))


def write_workbook(
    path: Path,
    *,
    headers: tuple[str, ...] = ("County", "Year", "Indicator", "Value"),
) -> None:
    shared_strings = [*headers, "Busia", "2012", "Area (HA)", "Production (MT)", "Yield(MT/HA)"]
    shared_xml = "".join(f"<si><t>{value}</t></si>" for value in shared_strings)
    def string_cell(reference: str, index: int) -> str:
        return f'<c r="{reference}" t="s"><v>{index}</v></c>'

    def numeric_cell(reference: str, value: int) -> str:
        return f'<c r="{reference}"><v>{value}</v></c>'

    def row(number: int, cells: list[str]) -> str:
        return f'<row r="{number}">{"".join(cells)}</row>'

    sheet_xml = "".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
            "<sheetData>",
            row(
                1,
                [
                    string_cell("A1", 0),
                    string_cell("B1", 1),
                    string_cell("C1", 2),
                    string_cell("D1", 3),
                ],
            ),
            row(
                2,
                [
                    string_cell("A2", 4),
                    string_cell("B2", 5),
                    string_cell("C2", 6),
                    numeric_cell("D2", 10),
                ],
            ),
            row(
                3,
                [
                    string_cell("A3", 4),
                    string_cell("B3", 5),
                    string_cell("C3", 7),
                    numeric_cell("D3", 20),
                ],
            ),
            row(
                4,
                [
                    string_cell("A4", 4),
                    string_cell("B4", 5),
                    string_cell("C4", 8),
                    numeric_cell("D4", 2),
                ],
            ),
            "</sheetData></worksheet>",
        ]
    )
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("xl/sharedStrings.xml", f"<sst xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">{shared_xml}</sst>")
        archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def test_read_nipfn_workbook_uses_the_verified_tidy_sheet(tmp_path: Path) -> None:
    path = tmp_path / "maize.xlsx"
    write_workbook(path)

    records = read_nipfn_workbook(path)

    assert records == (
        {"County": "Busia", "Year": "2012", "Indicator": "Area (HA)", "Value": 10.0},
        {"County": "Busia", "Year": "2012", "Indicator": "Production (MT)", "Value": 20.0},
        {"County": "Busia", "Year": "2012", "Indicator": "Yield(MT/HA)", "Value": 2.0},
    )


def test_read_nipfn_workbook_rejects_a_schema_that_drifted(tmp_path: Path) -> None:
    path = tmp_path / "maize.xlsx"
    write_workbook(path, headers=("County", "Year", "Indicator", "Amount"))

    with pytest.raises(ValueError, match="County, Year, Indicator, Value"):
        read_nipfn_workbook(path)


@pytest.mark.parametrize(
    ("indicator", "element", "unit"),
    [
        ("Area (HA)", "harvested_area", "ha"),
        ("Production (MT)", "production", "tonnes"),
        ("Yield(MT/HA)", "reported_yield", "tonnes per hectare"),
    ],
)
def test_nipfn_adapter_maps_verified_indicators(
    indicator: str, element: str, unit: str
) -> None:
    item = canonicalize_nipfn_record(
        {"County": " Busia ", "Year": "2012", "Indicator": indicator, "Value": 2},
        registry=registry(),
        snapshot_id="snapshot:nipfn",
    )

    assert item.key.county_id == "busia"
    assert item.key.period_id == "2012"
    assert item.element == element
    assert item.normalized_unit == {"ha": "ha", "tonnes": "t", "tonnes per hectare": "t/ha"}[unit]
    assert item.original_fields == {
        "County": " Busia ",
        "Year": "2012",
        "Indicator": indicator,
        "Value": 2,
    }


def test_nipfn_adapter_rejects_unknown_indicators() -> None:
    with pytest.raises(ValueError, match="unsupported NIPFN indicator"):
        canonicalize_nipfn_record(
            {"County": "Busia", "Year": "2012", "Indicator": "Price", "Value": 2},
            registry=registry(),
            snapshot_id="snapshot:nipfn",
        )


def test_nipfn_publication_binds_target_rows_to_the_verified_snapshot(tmp_path: Path) -> None:
    workbook = tmp_path / "maize.xlsx"
    write_workbook(workbook)
    manifest = tmp_path / "snapshot.json"
    manifest.write_text(
        json.dumps(
            {
                "source_id": "nipfn-maize-2012-2020",
                "sha256": sha256(workbook.read_bytes()).hexdigest(),
                "storage_uri": "snapshot://raw/nipfn-maize/example.xlsx",
            }
        ),
        encoding="utf-8",
    )

    publication = build_nipfn_publication(
        workbook_path=workbook,
        snapshot_manifest_path=manifest,
        county_registry_path=Path("tests/fixtures/county_profiles.json"),
        primary_county_id="busia",
        fallback_county_id="trans_nzoia",
        policy=PilotGatePolicy(
            minimum_periods=1,
            minimum_yield_coverage=1,
            maximum_review_required_fraction=0,
            maximum_divergent_fraction=0,
        ),
    )

    assert publication.target.report.target_rows == 1
    assert publication.target.rows[0].reconciliation_status == "consistent"
    assert publication.decision.status == "confirmed"
    assert publication.snapshot_id == "snapshot://raw/nipfn-maize/example.xlsx"
