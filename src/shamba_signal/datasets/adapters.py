from __future__ import annotations

import math
import re
import unicodedata
from typing import Mapping

from shamba_signal.datasets.target import (
    CanonicalObservation,
    CountyRegistry,
    ObservationElement,
    ObservationQuality,
)

_KILIMOSTAT_FIELDS = {
    "County",
    "Domain",
    "Subdomain",
    "Element",
    "Item",
    "Value",
    "Unit",
    "Year",
    "Source",
    "Flag",
}
_KILIMOSTAT_ELEMENTS: dict[str, ObservationElement] = {
    "production": "production",
    "area harvested": "harvested_area",
    "harvested area": "harvested_area",
    "yield": "reported_yield",
    "yield per hectare": "reported_yield",
}


def _normalise_label(value: object, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return " ".join(re.findall(r"[a-z0-9]+", ascii_value.casefold()))


def _parse_numeric(value: object) -> float:
    if isinstance(value, bool):
        raise ValueError("KilimoSTAT Value must be numeric")
    if isinstance(value, (int, float)):
        parsed = float(value)
    elif isinstance(value, str):
        try:
            parsed = float(value.replace(",", "").strip())
        except ValueError as exc:
            raise ValueError("KilimoSTAT Value must be numeric") from exc
    else:
        raise ValueError("KilimoSTAT Value must be numeric")
    if not math.isfinite(parsed):
        raise ValueError("KilimoSTAT Value must be finite")
    return parsed


def _parse_period(value: object) -> str:
    if isinstance(value, bool):
        raise ValueError("KilimoSTAT Year must be an integer or non-empty string")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError("KilimoSTAT Year must be an integer or non-empty string")


def canonicalize_kilimostat_record(
    record: Mapping[str, object],
    *,
    registry: CountyRegistry,
    snapshot_id: str,
    selected_crop: str = "maize",
    flag_quality: Mapping[str, ObservationQuality] | None = None,
) -> CanonicalObservation:
    missing = sorted(_KILIMOSTAT_FIELDS - set(record))
    if missing:
        raise ValueError(f"KilimoSTAT record missing required fields: {missing}")

    selected_crop_label = _normalise_label(selected_crop, field_name="selected_crop")
    item = _normalise_label(record["Item"], field_name="KilimoSTAT Item")
    if item != selected_crop_label:
        raise ValueError(
            f"KilimoSTAT row is not for selected crop {selected_crop_label}: {item}"
        )

    source_element = _normalise_label(
        record["Element"], field_name="KilimoSTAT Element"
    )
    element = _KILIMOSTAT_ELEMENTS.get(source_element)
    if element is None:
        raise ValueError(f"unsupported KilimoSTAT element: {record['Element']}")

    flag = record["Flag"]
    if flag is not None and not isinstance(flag, str):
        raise ValueError("KilimoSTAT Flag must be a string or None")
    quality: ObservationQuality = "review-required"
    if isinstance(flag, str) and flag_quality is not None:
        quality = flag_quality.get(flag, "review-required")

    source_name = record["Source"]
    if not isinstance(source_name, str) or not source_name.strip():
        raise ValueError("KilimoSTAT Source must be a non-empty string")
    county = record["County"]
    if not isinstance(county, str):
        raise ValueError("KilimoSTAT County must be a string")
    unit = record["Unit"]
    if not isinstance(unit, str):
        raise ValueError("KilimoSTAT Unit must be a string")

    return CanonicalObservation.create(
        registry=registry,
        county=county,
        crop=selected_crop_label,
        period_id=_parse_period(record["Year"]),
        element=element,
        value=_parse_numeric(record["Value"]),
        unit=unit,
        source_name=source_name,
        source_flag=flag,
        quality_class=quality,
        snapshot_id=snapshot_id,
        original_fields=dict(record),
    )
