from __future__ import annotations

import pytest

from shamba_signal.datasets.knbs_report import (
    KnbsAnnualMaizeRecord,
    canonicalize_knbs_maize_record,
    parse_knbs_annex_tables,
    validate_knbs_annex_records,
)
from shamba_signal.datasets.target import CountyRegistry


def test_parse_knbs_annex_tables_restores_rotated_county_values() -> None:
    table = [
        ["", "noitcudorP )sennoT(", "054,96", "650,984", "581,955,3"],
        ["0202", ")aH(aerA", "051,84", "058,401", "796,171,2"],
        ["", "ytnuoC", "aisuB", "aiozN\nsnarT", "latoT"],
    ]

    records = parse_knbs_annex_tables([table])

    assert records == (
        KnbsAnnualMaizeRecord(
            county="Busia",
            year=2020,
            harvested_area_ha=48_150,
            production_tonnes=69_450,
            provisional=False,
        ),
        KnbsAnnualMaizeRecord(
            county="Trans Nzoia",
            year=2020,
            harvested_area_ha=104_850,
            production_tonnes=489_056,
            provisional=False,
        ),
    )


def test_parse_knbs_annex_tables_marks_only_2023_as_provisional() -> None:
    table = [
        ["", "noitcudorP )sennoT(", "732,17"],
        ["3202", ")aH(aerA", "790,44"],
        ["", "noitcudorP )sennoT(", "544,76"],
        ["9102", ")aH(aerA", "058,16"],
        ["", "ytnuoC", "aisuB"],
    ]

    records = parse_knbs_annex_tables([table])

    assert [(record.year, record.provisional) for record in records] == [
        (2019, False),
        (2023, True),
    ]


def test_parse_knbs_annex_tables_corrects_verified_kilifi_text_order() -> None:
    table = [
        ["", "noitcudorP )sennoT(", "585,44"],
        ["0202", ")aH(aerA", "287,17"],
        ["", "ytnuoC", "fiiliK"],
    ]

    records = parse_knbs_annex_tables([table])

    assert records[0].county == "Kilifi"


def test_validate_knbs_annex_records_rejects_incomplete_national_panel() -> None:
    with pytest.raises(ValueError, match="47 counties x 5 years"):
        validate_knbs_annex_records(
            (
                KnbsAnnualMaizeRecord(
                    county="Busia",
                    year=2020,
                    harvested_area_ha=48_150,
                    production_tonnes=69_450,
                    provisional=False,
                ),
            )
        )


def test_canonicalize_knbs_record_produces_area_and_production_observations() -> None:
    registry = CountyRegistry.from_records(
        [{"candidate_id": "busia", "name": "Busia"}]
    )

    observations = canonicalize_knbs_maize_record(
        KnbsAnnualMaizeRecord(
            county="Busia",
            year=2023,
            harvested_area_ha=44_097,
            production_tonnes=71_237,
            provisional=True,
        ),
        registry=registry,
        snapshot_id="snapshot://knbs-report-2024.pdf",
    )

    assert [item.element for item in observations] == ["harvested_area", "production"]
    assert [item.normalized_value for item in observations] == [44_097, 71_237]
    assert all(item.source_flag == "provisional" for item in observations)
    assert all(item.quality_class == "accepted" for item in observations)
