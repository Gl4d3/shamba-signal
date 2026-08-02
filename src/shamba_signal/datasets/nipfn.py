from __future__ import annotations

import math
import re
from collections.abc import Mapping
from pathlib import Path
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from shamba_signal.datasets.target import (
    CanonicalObservation,
    CountyRegistry,
    ObservationElement,
)

_WORKSHEET_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_REQUIRED_HEADERS = ("County", "Year", "Indicator", "Value")
_NIPFN_INDICATORS: dict[str, tuple[ObservationElement, str]] = {
    "area ha": ("harvested_area", "ha"),
    "production mt": ("production", "tonnes"),
    "yield mt ha": ("reported_yield", "tonnes per hectare"),
}
_FORMULA = object()


def _column_number(reference: str) -> int:
    match = re.match(r"([A-Z]+)", reference)
    if match is None:
        raise ValueError(f"invalid XLSX cell reference: {reference!r}")
    value = 0
    for character in match.group(1):
        value = value * 26 + ord(character) - ord("A") + 1
    return value


def _shared_strings(archive: ZipFile) -> tuple[str, ...]:
    try:
        root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return ()
    except ElementTree.ParseError as exc:
        raise ValueError("NIPFN workbook shared strings are invalid XML") from exc
    return tuple(
        "".join(item.text or "" for item in string.iter(f"{_WORKSHEET_NS}t"))
        for string in root.findall(f"{_WORKSHEET_NS}si")
    )


def _cell_value(cell: ElementTree.Element, strings: tuple[str, ...]) -> object:
    cell_type = cell.get("t")
    raw = cell.findtext(f"{_WORKSHEET_NS}v")
    if cell_type == "s":
        if raw is None:
            raise ValueError("NIPFN workbook has an empty shared-string cell")
        try:
            return strings[int(raw)]
        except (IndexError, ValueError) as exc:
            raise ValueError("NIPFN workbook references an invalid shared string") from exc
    if cell_type == "inlineStr":
        return "".join(item.text or "" for item in cell.iter(f"{_WORKSHEET_NS}t"))
    if cell.find(f"{_WORKSHEET_NS}f") is not None:
        return _FORMULA
    if raw is None:
        return ""
    if cell_type in {"str", "e"}:
        return raw
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"NIPFN workbook contains a non-numeric cell value: {raw!r}") from exc
    if not math.isfinite(value):
        raise ValueError("NIPFN workbook contains a non-finite cell value")
    return value


def _worksheet_rows(payload: bytes, strings: tuple[str, ...]) -> tuple[dict[int, object], ...]:
    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError as exc:
        raise ValueError("NIPFN workbook worksheet is invalid XML") from exc
    rows: list[dict[int, object]] = []
    for row in root.findall(f".//{_WORKSHEET_NS}row"):
        values: dict[int, object] = {}
        for cell in row.findall(f"{_WORKSHEET_NS}c"):
            reference = cell.get("r")
            if reference is None:
                raise ValueError("NIPFN workbook contains a cell without a reference")
            values[_column_number(reference)] = _cell_value(cell, strings)
        if values:
            rows.append(values)
    return tuple(rows)


def _records_from_rows(rows: tuple[dict[int, object], ...]) -> tuple[dict[str, object], ...] | None:
    for index, header_row in enumerate(rows):
        header = tuple(header_row.get(column) for column in range(1, 5))
        has_extra_values = any(column > 4 for column in header_row)
        if header != _REQUIRED_HEADERS or has_extra_values:
            continue
        records: list[dict[str, object]] = []
        for data_row in rows[index + 1 :]:
            if any(column > 4 for column in data_row):
                raise ValueError("NIPFN tidy worksheet has unexpected populated columns")
            if not all(column in data_row for column in range(1, 5)):
                raise ValueError("NIPFN tidy worksheet contains an incomplete record")
            if any(data_row[column] is _FORMULA for column in range(1, 5)):
                raise ValueError("NIPFN tidy worksheet formulas are not accepted as source values")
            records.append(
                dict(
                    zip(
                        _REQUIRED_HEADERS,
                        (data_row[column] for column in range(1, 5)),
                        strict=True,
                    )
                )
            )
        if not records:
            raise ValueError("NIPFN tidy worksheet contains no data records")
        return tuple(records)
    return None


def read_nipfn_workbook(path: Path) -> tuple[dict[str, object], ...]:
    """Read the verified tidy worksheet from the official NIPFN XLSX without mutation."""
    try:
        with ZipFile(path) as archive:
            strings = _shared_strings(archive)
            candidates = [
                candidate
                for name in archive.namelist()
                if re.fullmatch(r"xl/worksheets/sheet[0-9]+\.xml", name)
                if (candidate := _records_from_rows(_worksheet_rows(archive.read(name), strings)))
                is not None
            ]
    except (BadZipFile, OSError) as exc:
        raise ValueError(f"could not read NIPFN XLSX workbook: {path}") from exc
    if len(candidates) != 1:
        raise ValueError(
            "NIPFN workbook must contain exactly one tidy worksheet with headers "
            "County, Year, Indicator, Value"
        )
    return candidates[0]


def _normalise_indicator(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("NIPFN Indicator must be a non-empty string")
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def _parse_numeric(value: object) -> float:
    if isinstance(value, bool):
        raise ValueError("NIPFN Value must be numeric")
    if isinstance(value, int | float):
        parsed = float(value)
    elif isinstance(value, str):
        try:
            parsed = float(value.replace(",", "").strip())
        except ValueError as exc:
            raise ValueError("NIPFN Value must be numeric") from exc
    else:
        raise ValueError("NIPFN Value must be numeric")
    if not math.isfinite(parsed):
        raise ValueError("NIPFN Value must be finite")
    return parsed


def _parse_period(value: object) -> str:
    if isinstance(value, bool):
        raise ValueError("NIPFN Year must be an integer or non-empty string")
    if isinstance(value, int | float):
        if not math.isfinite(float(value)) or float(value) != int(value):
            raise ValueError("NIPFN Year must be an integer or non-empty string")
        return str(int(value))
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError("NIPFN Year must be an integer or non-empty string")


def canonicalize_nipfn_record(
    record: Mapping[str, object],
    *,
    registry: CountyRegistry,
    snapshot_id: str,
    selected_crop: str = "maize",
) -> CanonicalObservation:
    missing = sorted(set(_REQUIRED_HEADERS) - set(record))
    if missing:
        raise ValueError(f"NIPFN record missing required fields: {missing}")
    indicator = _NIPFN_INDICATORS.get(_normalise_indicator(record["Indicator"]))
    if indicator is None:
        raise ValueError(f"unsupported NIPFN indicator: {record['Indicator']}")
    county = record["County"]
    if not isinstance(county, str):
        raise ValueError("NIPFN County must be a string")
    element, unit = indicator
    return CanonicalObservation.create(
        registry=registry,
        county=county.strip(),
        crop=selected_crop,
        period_id=_parse_period(record["Year"]),
        element=element,
        value=_parse_numeric(record["Value"]),
        unit=unit,
        source_name="Kenya National Bureau of Statistics / NIPFN",
        source_flag=None,
        quality_class="accepted",
        snapshot_id=snapshot_id,
        original_fields=dict(record),
    )
