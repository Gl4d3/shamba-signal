from __future__ import annotations

import math

import numpy as np
import pytest

from shamba_signal.modelling.tabfm_benchmark import (
    WEATHER_COLUMNS,
    AggregateResult,
    ExtendedMetrics,
    build_temporal_folds,
    classify_decision,
    metrics,
)
from shamba_signal.modelling.temporal_baselines import PanelExample
from shamba_signal.modelling.weather_experiment import WeatherFeature


def _examples() -> tuple[PanelExample, ...]:
    rows = []
    for year in range(2012, 2020):
        split = "train" if year < 2018 else "validation" if year == 2018 else "test"
        for county, offset in (("alpha", 0.0), ("beta", 1.0)):
            rows.append(
                PanelExample(
                    county_id=county,
                    year=year,
                    yield_t_per_ha=1.0 + offset + (year - 2012) * 0.1,
                    split=split,
                    provisional=year == 2019,
                )
            )
    return tuple(rows)


def _weather() -> tuple[WeatherFeature, ...]:
    return tuple(
        WeatherFeature(
            county_id=county,
            year=year,
            precipitation_total_mm=500.0 + year,
            wet_day_count=70 + year % 3,
            mean_temperature_c=20.0 + offset,
            max_temperature_c=30.0 + offset,
        )
        for year in range(2012, 2020)
        for county, offset in (("alpha", 0.0), ("beta", 1.0))
    )


def test_build_temporal_folds_never_places_future_rows_in_context() -> None:
    folds = build_temporal_folds(_examples(), _weather(), evaluation_years=(2018, 2019))

    assert [fold.evaluation_year for fold in folds] == [2018, 2019]
    assert all(row.year < fold.evaluation_year for fold in folds for row in fold.training)
    assert all(row.year == fold.evaluation_year for fold in folds for row in fold.evaluation)
    assert [len(fold.evaluation) for fold in folds] == [2, 2]


def test_tabfm_rows_preserve_county_as_categorical_text() -> None:
    fold = build_temporal_folds(_examples(), _weather(), evaluation_years=(2019,))[0]
    row = fold.training[0]

    assert row.temporal_features["county_id"] in {"alpha", "beta"}
    assert isinstance(row.temporal_features["county_id"], str)
    assert tuple(row.weather_features) == WEATHER_COLUMNS
    assert row.features(include_weather=False) == row.temporal_features
    assert set(row.features(include_weather=True)) == (
        set(row.temporal_features) | set(WEATHER_COLUMNS)
    )


def test_missing_weather_row_is_rejected() -> None:
    with pytest.raises(ValueError, match="weather features are missing"):
        build_temporal_folds(_examples(), _weather()[:-1], evaluation_years=(2019,))


def test_metrics_match_hand_calculated_values() -> None:
    result = metrics(
        actual=(1.0, 3.0),
        predicted=(2.0, 1.0),
        county_mean=(1.5, 3.5),
    )

    assert result.mae == 1.5
    assert result.rmse == pytest.approx(math.sqrt(2.5))
    assert result.median_absolute_error == 1.5
    assert result.mean_error == -0.5
    assert result.worst_absolute_error == 2.0
    assert result.counties_beating_county_mean == 0
    assert result.evaluated_counties == 2


def _metric(mae: float, *, worst: float = 1.0) -> ExtendedMetrics:
    return ExtendedMetrics(
        mae=mae,
        rmse=mae,
        median_absolute_error=mae,
        mean_error=0.0,
        worst_absolute_error=worst,
        counties_beating_county_mean=1,
        evaluated_counties=2,
    )


def _aggregate(
    county: float,
    temporal: float,
    weather: float,
    *,
    weather_wins: int,
    weather_worst: float = 1.0,
    county_worst: float = 1.0,
) -> AggregateResult:
    return AggregateResult.from_test_values(
        county_mean=_metric(county, worst=county_worst),
        tabfm_temporal=_metric(temporal),
        tabfm_weather=_metric(weather, worst=weather_worst),
        tabfm_weather_fold_wins=weather_wins,
    )


def test_decision_is_strong_go_for_stable_weather_win() -> None:
    assert classify_decision(_aggregate(0.40, 0.35, 0.30, weather_wins=4)).code == (
        "strong_go"
    )


def test_decision_is_model_go_weather_no_go_when_weather_adds_nothing() -> None:
    decision = classify_decision(_aggregate(0.40, 0.32, 0.34, weather_wins=4))
    assert decision.code == "model_go_weather_no_go"


def test_decision_is_inconclusive_for_unstable_or_bad_tail_win() -> None:
    result = _aggregate(0.40, 0.39, 0.35, weather_wins=2, weather_worst=1.3)
    assert classify_decision(result).code == "inconclusive"


def test_decision_is_no_go_when_tabfm_does_not_beat_county_mean() -> None:
    assert classify_decision(_aggregate(0.30, 0.35, 0.34, weather_wins=1)).code == (
        "no_go"
    )


def test_metrics_accept_numpy_arrays() -> None:
    result = metrics(
        actual=np.array([1.0, 2.0]),
        predicted=np.array([1.1, 1.9]),
        county_mean=np.array([1.2, 2.2]),
    )

    assert result.mae == pytest.approx(0.1)
