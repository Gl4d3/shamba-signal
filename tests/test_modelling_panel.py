from __future__ import annotations

from shamba_signal.datasets.modelling_panel import (
    build_modelling_panel,
    compare_revision_year,
    render_modelling_panel_csv,
)
from shamba_signal.datasets.target import CanonicalObservation, CountyRegistry


def _observations(
    *,
    registry: CountyRegistry,
    county: str,
    year: int,
    production: float,
    area: float,
    source_name: str,
    snapshot_id: str,
    reported_yield: float | None = None,
    provisional: bool = False,
) -> tuple[CanonicalObservation, ...]:
    common = {
        "registry": registry,
        "county": county,
        "crop": "maize",
        "period_id": str(year),
        "source_name": source_name,
        "source_flag": "provisional" if provisional else None,
        "quality_class": "accepted",
        "snapshot_id": snapshot_id,
    }
    items = [
        CanonicalObservation.create(
            **common, element="production", value=production, unit="t"
        ),
        CanonicalObservation.create(
            **common, element="harvested_area", value=area, unit="ha"
        ),
    ]
    if reported_yield is not None:
        items.append(
            CanonicalObservation.create(
                **common,
                element="reported_yield",
                value=reported_yield,
                unit="t/ha",
            )
        )
    return tuple(items)


def test_build_modelling_panel_uses_report_revision_from_2019_onward() -> None:
    registry = CountyRegistry.from_records(
        [{"candidate_id": "busia", "name": "Busia"}]
    )
    historical = (
        *_observations(
            registry=registry,
            county="Busia",
            year=2018,
            production=20,
            area=10,
            reported_yield=2,
            source_name="NIPFN workbook",
            snapshot_id="snapshot://workbook",
        ),
        *_observations(
            registry=registry,
            county="Busia",
            year=2020,
            production=10,
            area=10,
            reported_yield=1,
            source_name="NIPFN workbook",
            snapshot_id="snapshot://workbook",
        ),
    )
    report = tuple(
        item
        for year in range(2019, 2024)
        for item in _observations(
            registry=registry,
            county="Busia",
            year=year,
            production=(year - 2016) * 10,
            area=10,
            source_name="KNBS report",
            snapshot_id="snapshot://report",
            provisional=year == 2023,
        )
    )

    rows = build_modelling_panel(historical, report)

    assert [row.year for row in rows] == [2018, 2019, 2020, 2021, 2022, 2023]
    assert next(row for row in rows if row.year == 2020).active_yield_t_per_ha == 4
    assert next(row for row in rows if row.year == 2020).source_vintage == "knbs-report-2024"
    assert [(row.year, row.split) for row in rows[-3:]] == [
        (2021, "train"),
        (2022, "validation"),
        (2023, "test"),
    ]
    assert rows[-1].provisional is True
    assert rows[-1].label_method == "derived"
    assert "county_id,county_name,year" in render_modelling_panel_csv(rows)


def test_compare_revision_year_flags_only_material_differences() -> None:
    registry = CountyRegistry.from_records(
        [
            {"candidate_id": "busia", "name": "Busia"},
            {"candidate_id": "trans_nzoia", "name": "Trans Nzoia"},
        ]
    )
    historical = (
        *_observations(
            registry=registry,
            county="Busia",
            year=2020,
            production=69_450,
            area=48_150,
            source_name="NIPFN workbook",
            snapshot_id="snapshot://workbook",
        ),
        *_observations(
            registry=registry,
            county="Trans Nzoia",
            year=2020,
            production=11_251.1,
            area=18_591,
            source_name="NIPFN workbook",
            snapshot_id="snapshot://workbook",
        ),
    )
    report = (
        *_observations(
            registry=registry,
            county="Busia",
            year=2020,
            production=69_450,
            area=48_150,
            source_name="KNBS report",
            snapshot_id="snapshot://report",
        ),
        *_observations(
            registry=registry,
            county="Trans Nzoia",
            year=2020,
            production=489_056,
            area=104_850,
            source_name="KNBS report",
            snapshot_id="snapshot://report",
        ),
    )

    comparisons = compare_revision_year(historical, report, year=2020)

    assert [(item.county_id, item.materially_different) for item in comparisons] == [
        ("busia", False),
        ("trans_nzoia", True),
    ]
