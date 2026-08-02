import json
from pathlib import Path

import pytest

from shamba_signal.datasets.target import (
    CanonicalObservation,
    CountyRegistry,
    derive_yield,
    index_observations,
    load_county_registry,
    reconcile_yield,
)


def write_profiles(tmp_path: Path) -> Path:
    path = tmp_path / "profiles.json"
    path.write_text(
        json.dumps(
            {
                "counties": [
                    {"candidate_id": "busia", "name": "Busia"},
                    {"candidate_id": "taita_taveta", "name": "Taita-Taveta"},
                    {"candidate_id": "muranga", "name": "Murang'a"},
                    {"candidate_id": "nairobi_city", "name": "Nairobi City"},
                ]
            }
        ),
        encoding="utf-8",
    )
    return path


def observation(
    registry: CountyRegistry,
    *,
    county: str = "Busia",
    crop: str = "maize",
    period: str = "2023",
    element: str,
    value: float,
    unit: str,
    snapshot_id: str = "snapshot-a",
) -> CanonicalObservation:
    return CanonicalObservation.create(
        registry=registry,
        county=county,
        crop=crop,
        period_id=period,
        element=element,
        value=value,
        unit=unit,
        source_name="fixture",
        source_flag="E",
        quality_class="flagged",
        snapshot_id=snapshot_id,
    )


def test_county_registry_maps_official_names_and_safe_aliases(tmp_path: Path) -> None:
    registry = load_county_registry(write_profiles(tmp_path))

    assert registry.resolve("Busia").county_id == "busia"
    assert registry.resolve("taita taveta").county_id == "taita_taveta"
    assert registry.resolve("Muranga").county_id == "muranga"
    assert registry.resolve("Nairobi").county_id == "nairobi_city"


def test_county_registry_rejects_unknown_county(tmp_path: Path) -> None:
    registry = load_county_registry(write_profiles(tmp_path))

    with pytest.raises(ValueError, match="unknown county"):
        registry.resolve("Atlantis")


def test_county_registry_rejects_non_string_identifiers() -> None:
    with pytest.raises(ValueError, match="candidate_id"):
        CountyRegistry.from_records([{"candidate_id": None, "name": "Busia"}])


def test_county_registry_rejects_colliding_aliases() -> None:
    with pytest.raises(ValueError, match="ambiguous county alias"):
        CountyRegistry.from_records(
            [
                {"candidate_id": "alpha", "name": "A-B"},
                {"candidate_id": "beta", "name": "A B"},
            ]
        )


@pytest.mark.parametrize(
    ("element", "value", "unit", "expected_value", "expected_unit"),
    [
        ("production", 2500, "kg", 2.5, "t"),
        ("production", 2.5, "tonnes", 2.5, "t"),
        ("harvested_area", 10, "acres", 4.0468564224, "ha"),
        ("harvested_area", 10, "ha", 10, "ha"),
        ("reported_yield", 2500, "kg/ha", 2.5, "t/ha"),
        ("reported_yield", 2.5, "tonnes per hectare", 2.5, "t/ha"),
    ],
)
def test_canonical_observation_normalizes_units_and_preserves_originals(
    tmp_path: Path,
    element: str,
    value: float,
    unit: str,
    expected_value: float,
    expected_unit: str,
) -> None:
    registry = load_county_registry(write_profiles(tmp_path))

    item = observation(
        registry,
        element=element,
        value=value,
        unit=unit,
    )

    assert item.normalized_value == pytest.approx(expected_value)
    assert item.normalized_unit == expected_unit
    assert item.original_value == value
    assert item.original_unit == unit
    assert item.source_flag == "E"
    assert item.quality_class == "flagged"


def test_canonical_observation_rejects_invalid_quality_class(tmp_path: Path) -> None:
    registry = load_county_registry(write_profiles(tmp_path))

    with pytest.raises(ValueError, match="quality_class"):
        CanonicalObservation.create(
            registry=registry,
            county="Busia",
            crop="maize",
            period_id="2023",
            element="production",
            value=10,
            unit="t",
            source_name="fixture",
            source_flag=None,
            quality_class="perfect",
            snapshot_id="snapshot-a",
        )


def test_canonical_observation_rejects_unknown_units(tmp_path: Path) -> None:
    registry = load_county_registry(write_profiles(tmp_path))

    with pytest.raises(ValueError, match="unsupported unit"):
        observation(registry, element="production", value=10, unit="bags")


def test_canonical_observation_rejects_negative_values(tmp_path: Path) -> None:
    registry = load_county_registry(write_profiles(tmp_path))

    with pytest.raises(ValueError, match="non-negative"):
        observation(registry, element="production", value=-1, unit="t")


def test_derive_yield_uses_positive_same_grain_inputs(tmp_path: Path) -> None:
    registry = load_county_registry(write_profiles(tmp_path))
    production = observation(registry, element="production", value=20, unit="t")
    area = observation(registry, element="harvested_area", value=10, unit="ha")

    derived = derive_yield(production, area)

    assert derived.value_t_per_ha == pytest.approx(2.0)
    assert derived.method == "production_tonnes / harvested_area_ha"
    assert derived.source_snapshot_ids == ("snapshot-a",)


def test_derive_yield_rejects_zero_area(tmp_path: Path) -> None:
    registry = load_county_registry(write_profiles(tmp_path))
    production = observation(registry, element="production", value=20, unit="t")
    area = observation(registry, element="harvested_area", value=0, unit="ha")

    with pytest.raises(ValueError, match="greater than zero"):
        derive_yield(production, area)


@pytest.mark.parametrize(
    ("field", "replacement", "message"),
    [
        ("county", "Taita Taveta", "same county"),
        ("crop", "beans", "same crop"),
        ("period", "2022", "same period"),
    ],
)
def test_derive_yield_rejects_mismatched_grain(
    tmp_path: Path,
    field: str,
    replacement: str,
    message: str,
) -> None:
    registry = load_county_registry(write_profiles(tmp_path))
    kwargs = {"county": "Busia", "crop": "maize", "period": "2023"}
    production = observation(
        registry,
        element="production",
        value=20,
        unit="t",
        **kwargs,
    )
    kwargs[field] = replacement
    area = observation(
        registry,
        element="harvested_area",
        value=10,
        unit="ha",
        **kwargs,
    )

    with pytest.raises(ValueError, match=message):
        derive_yield(production, area)


def test_reconcile_yield_keeps_reported_and_derived_values_separate(tmp_path: Path) -> None:
    registry = load_county_registry(write_profiles(tmp_path))
    reported = observation(
        registry,
        element="reported_yield",
        value=2.05,
        unit="t/ha",
        snapshot_id="reported-snapshot",
    )
    production = observation(
        registry,
        element="production",
        value=20,
        unit="t",
        snapshot_id="production-snapshot",
    )
    area = observation(
        registry,
        element="harvested_area",
        value=10,
        unit="ha",
        snapshot_id="area-snapshot",
    )

    result = reconcile_yield(reported=reported, derived=derive_yield(production, area))

    assert result.reported_yield_t_per_ha == pytest.approx(2.05)
    assert result.derived_yield_t_per_ha == pytest.approx(2.0)
    assert result.status == "consistent"
    assert result.selected_yield_t_per_ha is None


def test_reconcile_yield_marks_divergence_without_overwriting_reported(tmp_path: Path) -> None:
    registry = load_county_registry(write_profiles(tmp_path))
    reported = observation(
        registry,
        element="reported_yield",
        value=4.0,
        unit="t/ha",
    )
    production = observation(registry, element="production", value=20, unit="t")
    area = observation(registry, element="harvested_area", value=10, unit="ha")

    result = reconcile_yield(
        reported=reported,
        derived=derive_yield(production, area),
        relative_tolerance=0.05,
        absolute_tolerance=0.05,
    )

    assert result.status == "divergent"
    assert result.reported_yield_t_per_ha == pytest.approx(4.0)
    assert result.derived_yield_t_per_ha == pytest.approx(2.0)
    assert result.selected_yield_t_per_ha is None


def test_index_observations_rejects_duplicate_target_elements(tmp_path: Path) -> None:
    registry = load_county_registry(write_profiles(tmp_path))
    first = observation(registry, element="production", value=20, unit="t")
    second = observation(
        registry,
        element="production",
        value=21,
        unit="t",
        snapshot_id="snapshot-b",
    )

    with pytest.raises(ValueError, match="duplicate canonical observation"):
        index_observations([first, second])


def test_reconcile_yield_supports_reported_only_without_selecting_a_value(tmp_path: Path) -> None:
    registry = load_county_registry(write_profiles(tmp_path))
    reported = observation(
        registry,
        element="reported_yield",
        value=2.2,
        unit="t/ha",
    )

    result = reconcile_yield(reported=reported, derived=None)

    assert result.status == "reported_only"
    assert result.reported_yield_t_per_ha == pytest.approx(2.2)
    assert result.derived_yield_t_per_ha is None
    assert result.selected_yield_t_per_ha is None


def test_reconcile_yield_supports_derived_only_without_selecting_a_value(tmp_path: Path) -> None:
    registry = load_county_registry(write_profiles(tmp_path))
    production = observation(registry, element="production", value=20, unit="t")
    area = observation(registry, element="harvested_area", value=10, unit="ha")

    result = reconcile_yield(reported=None, derived=derive_yield(production, area))

    assert result.status == "derived_only"
    assert result.reported_yield_t_per_ha is None
    assert result.derived_yield_t_per_ha == pytest.approx(2.0)
    assert result.selected_yield_t_per_ha is None
