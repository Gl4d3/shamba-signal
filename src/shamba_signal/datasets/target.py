from __future__ import annotations

import json
import math
import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ObservationElement = Literal["production", "harvested_area", "reported_yield"]
ObservationQuality = Literal["accepted", "flagged", "review-required"]
ReconciliationStatus = Literal[
    "reported_only",
    "derived_only",
    "consistent",
    "divergent",
]

_ALLOWED_ELEMENTS = {"production", "harvested_area", "reported_yield"}
_ALLOWED_QUALITY_CLASSES = {"accepted", "flagged", "review-required"}
_ACRE_TO_HECTARE = 0.40468564224
_EXPLICIT_ALIASES = {
    "muranga": "muranga",
    "nairobi": "nairobi_city",
}


def _require_text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _normalise_token(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return " ".join(re.findall(r"[a-z0-9]+", ascii_value.casefold()))


@dataclass(frozen=True)
class CountyIdentity:
    county_id: str
    county_name: str


class CountyRegistry:
    def __init__(
        self,
        *,
        counties_by_id: Mapping[str, CountyIdentity],
        aliases: Mapping[str, str],
    ) -> None:
        self._counties_by_id = dict(counties_by_id)
        self._aliases = dict(aliases)

    @classmethod
    def from_records(cls, records: Sequence[Mapping[str, object]]) -> CountyRegistry:
        if not records:
            raise ValueError("county registry must contain at least one county")
        counties_by_id: dict[str, CountyIdentity] = {}
        aliases: dict[str, str] = {}
        for index, raw in enumerate(records):
            county_id = _require_text("candidate_id", raw.get("candidate_id"))
            county_name = _require_text("name", raw.get("name"))
            if county_id in counties_by_id:
                raise ValueError(f"duplicate county id: {county_id}")
            identity = CountyIdentity(county_id=county_id, county_name=county_name)
            counties_by_id[county_id] = identity
            candidates = {
                _normalise_token(county_name),
                _normalise_token(county_id.replace("_", " ")),
            }
            if not all(candidates):
                raise ValueError(f"county record {index} contains an invalid alias")
            for alias in candidates:
                existing = aliases.get(alias)
                if existing and existing != county_id:
                    raise ValueError(f"ambiguous county alias: {alias}")
                aliases[alias] = county_id

        for alias, county_id in _EXPLICIT_ALIASES.items():
            if county_id not in counties_by_id:
                continue
            existing = aliases.get(alias)
            if existing and existing != county_id:
                raise ValueError(f"ambiguous county alias: {alias}")
            aliases[alias] = county_id
        return cls(counties_by_id=counties_by_id, aliases=aliases)

    def resolve(self, value: str) -> CountyIdentity:
        alias = _normalise_token(_require_text("county", value))
        county_id = self._aliases.get(alias)
        if not county_id:
            raise ValueError(f"unknown county: {value}")
        return self._counties_by_id[county_id]

    def __len__(self) -> int:
        return len(self._counties_by_id)


def load_county_registry(path: Path) -> CountyRegistry:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load county profiles: {path}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("counties"), list):
        raise ValueError("county profiles must contain a counties list")
    return CountyRegistry.from_records(payload["counties"])


@dataclass(frozen=True)
class TargetKey:
    county_id: str
    crop_id: str
    period_id: str


@dataclass(frozen=True)
class CanonicalObservation:
    key: TargetKey
    county_name: str
    element: ObservationElement
    original_value: float
    original_unit: str
    normalized_value: float
    normalized_unit: str
    source_name: str
    source_flag: str | None
    quality_class: ObservationQuality
    snapshot_id: str
    original_fields: Mapping[str, object] | None = None
    calendar_source: str | None = None

    @classmethod
    def create(
        cls,
        *,
        registry: CountyRegistry,
        county: str,
        crop: str,
        period_id: str,
        element: ObservationElement,
        value: float,
        unit: str,
        source_name: str,
        source_flag: str | None,
        quality_class: ObservationQuality,
        snapshot_id: str,
        original_fields: Mapping[str, object] | None = None,
        calendar_source: str | None = None,
    ) -> CanonicalObservation:
        if element not in _ALLOWED_ELEMENTS:
            raise ValueError(f"unsupported observation element: {element}")
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ValueError("observation value must be numeric")
        numeric_value = float(value)
        if not math.isfinite(numeric_value):
            raise ValueError("observation value must be finite")
        if numeric_value < 0:
            raise ValueError("observation value must be non-negative")
        identity = registry.resolve(county)
        crop_id = _normalise_token(_require_text("crop", crop)).replace(" ", "_")
        period = _require_text("period_id", period_id)
        source = _require_text("source_name", source_name)
        if source_flag is not None and not isinstance(source_flag, str):
            raise ValueError("source_flag must be a string or None")
        if quality_class not in _ALLOWED_QUALITY_CLASSES:
            raise ValueError(f"unsupported quality_class: {quality_class}")
        snapshot = _require_text("snapshot_id", snapshot_id)
        original_unit = _require_text("unit", unit)
        normalized_value, normalized_unit = _normalise_value(
            element=element,
            value=numeric_value,
            unit=original_unit,
        )
        return cls(
            key=TargetKey(
                county_id=identity.county_id,
                crop_id=crop_id,
                period_id=period,
            ),
            county_name=identity.county_name,
            element=element,
            original_value=numeric_value,
            original_unit=original_unit,
            normalized_value=normalized_value,
            normalized_unit=normalized_unit,
            source_name=source,
            source_flag=source_flag,
            quality_class=quality_class,
            snapshot_id=snapshot,
            original_fields=dict(original_fields) if original_fields is not None else None,
            calendar_source=(
                _require_text("calendar_source", calendar_source)
                if calendar_source is not None
                else None
            ),
        )


def _normalise_unit(unit: str) -> str:
    decomposed = unicodedata.normalize("NFKD", unit)
    ascii_value = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    normalized = ascii_value.casefold().strip()
    normalized = re.sub(r"\s+per\s+", "/", normalized)
    normalized = re.sub(r"\s*/\s*", "/", normalized)
    return re.sub(r"[\s._-]+", "", normalized)


def _normalise_value(
    *,
    element: ObservationElement,
    value: float,
    unit: str,
) -> tuple[float, str]:
    normalized_unit = _normalise_unit(unit)
    if element == "production":
        if normalized_unit in {"t", "ton", "tons", "tonne", "tonnes", "metrictonnes"}:
            return value, "t"
        if normalized_unit in {"kg", "kilogram", "kilograms"}:
            return value / 1000.0, "t"
    elif element == "harvested_area":
        if normalized_unit in {"ha", "hectare", "hectares"}:
            return value, "ha"
        if normalized_unit in {"acre", "acres"}:
            return value * _ACRE_TO_HECTARE, "ha"
    elif element == "reported_yield":
        if normalized_unit in {
            "t/ha",
            "ton/ha",
            "tons/ha",
            "tonne/ha",
            "tonnes/ha",
            "tonnes/hectare",
        }:
            return value, "t/ha"
        if normalized_unit in {"kg/ha", "kilogram/ha", "kilograms/ha"}:
            return value / 1000.0, "t/ha"
    raise ValueError(f"unsupported unit {unit!r} for element {element}")


@dataclass(frozen=True)
class DerivedYield:
    key: TargetKey
    value_t_per_ha: float
    method: str
    source_snapshot_ids: tuple[str, ...]


def _require_element(observation: CanonicalObservation, expected: ObservationElement) -> None:
    if observation.element != expected:
        raise ValueError(f"expected {expected} observation, got {observation.element}")


def derive_yield(
    production: CanonicalObservation,
    harvested_area: CanonicalObservation,
) -> DerivedYield:
    _require_element(production, "production")
    _require_element(harvested_area, "harvested_area")
    if production.key.county_id != harvested_area.key.county_id:
        raise ValueError("production and harvested area must use the same county")
    if production.key.crop_id != harvested_area.key.crop_id:
        raise ValueError("production and harvested area must use the same crop")
    if production.key.period_id != harvested_area.key.period_id:
        raise ValueError("production and harvested area must use the same period")
    if production.normalized_unit != "t" or harvested_area.normalized_unit != "ha":
        raise ValueError("production and harvested area must use compatible normalized units")
    if harvested_area.normalized_value <= 0:
        raise ValueError("harvested area must be greater than zero")
    snapshot_ids = tuple(sorted({production.snapshot_id, harvested_area.snapshot_id}))
    return DerivedYield(
        key=production.key,
        value_t_per_ha=production.normalized_value / harvested_area.normalized_value,
        method="production_tonnes / harvested_area_ha",
        source_snapshot_ids=snapshot_ids,
    )


@dataclass(frozen=True)
class YieldReconciliation:
    key: TargetKey
    reported_yield_t_per_ha: float | None
    derived_yield_t_per_ha: float | None
    absolute_difference_t_per_ha: float | None
    status: ReconciliationStatus
    selected_yield_t_per_ha: None = None


def reconcile_yield(
    *,
    reported: CanonicalObservation | None,
    derived: DerivedYield | None,
    relative_tolerance: float = 0.05,
    absolute_tolerance: float = 0.05,
) -> YieldReconciliation:
    if reported is None and derived is None:
        raise ValueError("reported or derived yield is required")
    for name, value in (
        ("relative_tolerance", relative_tolerance),
        ("absolute_tolerance", absolute_tolerance),
    ):
        if (
            isinstance(value, bool)
            or not isinstance(value, int | float)
            or not math.isfinite(value)
        ):
            raise ValueError(f"{name} must be a finite number")
        if value < 0:
            raise ValueError(f"{name} must be non-negative")

    if reported is not None:
        _require_element(reported, "reported_yield")
        key = reported.key
        reported_value = reported.normalized_value
    else:
        assert derived is not None
        key = derived.key
        reported_value = None

    if derived is not None and derived.key != key:
        raise ValueError("reported and derived yield must use the same target key")
    derived_value = derived.value_t_per_ha if derived is not None else None

    if reported_value is None:
        status: ReconciliationStatus = "derived_only"
        difference = None
    elif derived_value is None:
        status = "reported_only"
        difference = None
    else:
        difference = abs(reported_value - derived_value)
        status = (
            "consistent"
            if math.isclose(
                reported_value,
                derived_value,
                rel_tol=float(relative_tolerance),
                abs_tol=float(absolute_tolerance),
            )
            else "divergent"
        )
    return YieldReconciliation(
        key=key,
        reported_yield_t_per_ha=reported_value,
        derived_yield_t_per_ha=derived_value,
        absolute_difference_t_per_ha=difference,
        status=status,
    )


def index_observations(
    observations: Iterable[CanonicalObservation],
) -> dict[tuple[TargetKey, ObservationElement], CanonicalObservation]:
    indexed: dict[tuple[TargetKey, ObservationElement], CanonicalObservation] = {}
    for observation in observations:
        key = (observation.key, observation.element)
        if key in indexed:
            raise ValueError(
                "duplicate canonical observation for "
                f"{observation.key.county_id}/{observation.key.crop_id}/"
                f"{observation.key.period_id}/{observation.element}"
            )
        indexed[key] = observation
    return indexed
