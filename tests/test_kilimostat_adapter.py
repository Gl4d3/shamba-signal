from pathlib import Path

import pytest

from shamba_signal.datasets.adapters import canonicalize_kilimostat_record
from shamba_signal.datasets.target import load_county_registry


def registry():
    return load_county_registry(Path("tests/fixtures/county_profiles.json"))


def record(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "County": "Busia",
        "Domain": "Crops",
        "Subdomain": "Cereals",
        "Element": "Production",
        "Item": "Maize",
        "Value": "2,500",
        "Unit": "tonnes",
        "Year": 2023,
        "Source": "KilimoSTAT fixture",
        "Flag": "E",
    }
    values.update(overrides)
    return values


def test_kilimostat_adapter_maps_documented_fields_and_preserves_originals() -> None:
    item = canonicalize_kilimostat_record(
        record(),
        registry=registry(),
        snapshot_id="snapshot-1",
        flag_quality={"E": "flagged"},
    )

    assert item.key.county_id == "busia"
    assert item.key.crop_id == "maize"
    assert item.key.period_id == "2023"
    assert item.element == "production"
    assert item.normalized_value == pytest.approx(2500)
    assert item.normalized_unit == "t"
    assert item.source_flag == "E"
    assert item.quality_class == "flagged"
    assert item.original_fields == record()


@pytest.mark.parametrize(
    ("source_element", "unit", "expected"),
    [
        ("Production", "tonnes", "production"),
        ("Area harvested", "ha", "harvested_area"),
        ("Harvested Area", "acres", "harvested_area"),
        ("Yield", "kg/ha", "reported_yield"),
    ],
)
def test_kilimostat_adapter_maps_supported_elements(
    source_element: str,
    unit: str,
    expected: str,
) -> None:
    item = canonicalize_kilimostat_record(
        record(Element=source_element, Unit=unit, Value="10"),
        registry=registry(),
        snapshot_id="snapshot-1",
    )

    assert item.element == expected


def test_kilimostat_adapter_keeps_unknown_flags_review_required() -> None:
    item = canonicalize_kilimostat_record(
        record(Flag="Z"),
        registry=registry(),
        snapshot_id="snapshot-1",
        flag_quality={"E": "accepted"},
    )

    assert item.source_flag == "Z"
    assert item.quality_class == "review-required"


def test_kilimostat_adapter_rejects_non_maize_rows() -> None:
    with pytest.raises(ValueError, match="selected crop maize"):
        canonicalize_kilimostat_record(
            record(Item="Beans"),
            registry=registry(),
            snapshot_id="snapshot-1",
        )


def test_kilimostat_adapter_rejects_unsupported_elements() -> None:
    with pytest.raises(ValueError, match="unsupported KilimoSTAT element"):
        canonicalize_kilimostat_record(
            record(Element="Value of production"),
            registry=registry(),
            snapshot_id="snapshot-1",
        )


def test_kilimostat_adapter_rejects_missing_documented_fields() -> None:
    incomplete = record()
    del incomplete["Unit"]

    with pytest.raises(ValueError, match="missing required fields.*Unit"):
        canonicalize_kilimostat_record(
            incomplete,
            registry=registry(),
            snapshot_id="snapshot-1",
        )


def test_kilimostat_adapter_rejects_placeholder_values() -> None:
    with pytest.raises(ValueError, match="numeric"):
        canonicalize_kilimostat_record(
            record(Value="..."),
            registry=registry(),
            snapshot_id="snapshot-1",
        )
