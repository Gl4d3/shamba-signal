from __future__ import annotations

import json
import math
from pathlib import Path

from shamba_signal.modelling.temporal_baselines import PanelExample
from shamba_signal.modelling.weather_experiment import (
    OPEN_METEO_DATASET,
    DailyWeather,
    WeatherFeature,
    aggregate_annual_weather,
    features_from_open_meteo_batch,
    fetch_open_meteo_features,
    run_weather_experiment,
)


def test_weather_source_uses_the_era5_model_that_supplies_precipitation() -> None:
    assert OPEN_METEO_DATASET == "era5"


def test_aggregate_annual_weather_returns_documented_annual_features() -> None:
    feature = aggregate_annual_weather(
        county_id="busia",
        year=2022,
        days=(
            DailyWeather("2022-01-01", 0.0, 20.0, 28.0),
            DailyWeather("2022-01-02", 1.2, 21.0, 29.0),
            DailyWeather("2022-01-03", 7.8, 23.0, 31.0),
        ),
    )

    assert feature == WeatherFeature(
        county_id="busia",
        year=2022,
        precipitation_total_mm=9.0,
        wet_day_count=2,
        mean_temperature_c=21.333333333333332,
        max_temperature_c=31.0,
    )


def test_open_meteo_batch_keeps_each_payload_bound_to_its_county() -> None:
    payload = [
        {
            "daily": {
                "time": ["2022-01-01"],
                "precipitation_sum": [2.0],
                "temperature_2m_mean": [20.0],
                "temperature_2m_max": [30.0],
            }
        },
        {
            "daily": {
                "time": ["2022-01-01"],
                "precipitation_sum": [4.0],
                "temperature_2m_mean": [21.0],
                "temperature_2m_max": [31.0],
            }
        },
    ]

    result = features_from_open_meteo_batch(("busia", "bungoma"), payload)

    assert [(row.county_id, row.precipitation_total_mm) for row in result] == [
        ("bungoma", 4.0),
        ("busia", 2.0),
    ]


def test_cached_weather_keeps_the_original_retrieval_timestamp(tmp_path: Path) -> None:
    payload = {
        "daily": {
            "time": ["2022-01-01"],
            "precipitation_sum": [2.0],
            "temperature_2m_mean": [20.0],
            "temperature_2m_max": [30.0],
        }
    }
    cache_path = tmp_path / "open-meteo-era5-batch-2022-2022.json"
    cache_path.write_text(json.dumps(payload), encoding="utf-8")
    cache_path.with_suffix(".metadata.json").write_text(
        json.dumps({"retrieved_at_utc": "2026-08-03T10:21:34+00:00"}),
        encoding="utf-8",
    )

    first = fetch_open_meteo_features(
        county_ids=("busia",), raw_cache_dir=tmp_path, start_year=2022, end_year=2022
    )
    second = fetch_open_meteo_features(
        county_ids=("busia",), raw_cache_dir=tmp_path, start_year=2022, end_year=2022
    )

    assert first == second
    assert first[1]["retrieved_at_utc"] == "2026-08-03T10:21:34+00:00"

def _panel() -> tuple[PanelExample, ...]:
    rows: list[PanelExample] = []
    for county_id, offset in (("a", 0.0), ("b", 1.0), ("c", -0.5)):
        for year in range(2018, 2024):
            precipitation = (year - 2017) * 100.0 + offset * 10.0
            rows.append(
                PanelExample(
                    county_id=county_id,
                    year=year,
                    yield_t_per_ha=1.0 + offset + precipitation / 100.0,
                    split=(
                        "train" if year <= 2021 else "validation" if year == 2022 else "test"
                    ),
                    provisional=year == 2023,
                )
            )
    return tuple(rows)


def _weather() -> tuple[WeatherFeature, ...]:
    rows: list[WeatherFeature] = []
    for county_id, offset in (("a", 0.0), ("b", 1.0), ("c", -0.5)):
        for year in range(2018, 2024):
            precipitation = (year - 2017) * 100.0 + offset * 10.0
            rows.append(
                WeatherFeature(
                    county_id=county_id,
                    year=year,
                    precipitation_total_mm=precipitation,
                    wet_day_count=int(precipitation / 10),
                    mean_temperature_c=20.0 + offset,
                    max_temperature_c=30.0 + offset,
                )
            )
    return tuple(rows)


def test_weather_experiment_selects_on_validation_and_evaluates_test_once() -> None:
    result = run_weather_experiment(
        _panel(), _weather(), alpha_candidates=(0.01, 1.0, 100.0)
    )

    assert result.selected_alpha in {0.01, 1.0, 100.0}
    assert set(result.validation_metrics) == {
        "previous_year",
        "county_mean",
        "ridge",
        "weather_ridge",
    }
    assert set(result.test_metrics) == set(result.validation_metrics)
    assert {item.year for item in result.predictions} == {2022, 2023}
    assert all(math.isfinite(metric.mae) for metric in result.test_metrics.values())
    assert result.test_metrics["weather_ridge"].mae < result.test_metrics["county_mean"].mae
