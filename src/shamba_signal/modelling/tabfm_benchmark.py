"""Dependency-free contracts for the exploratory TabFM temporal benchmark.

The real TabFM, pandas, PyTorch, and Hugging Face dependencies live only in the
isolated experiment environment. This module owns leakage-safe folds, metrics,
and deterministic scientific decisions.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TypeAlias

import numpy as np

from shamba_signal.modelling.temporal_baselines import (
    PanelExample,
    build_lagged_examples,
)
from shamba_signal.modelling.weather_experiment import WeatherFeature

FeatureValue: TypeAlias = str | int | float

TEMPORAL_COLUMNS = (
    "county_id",
    "year",
    "lag_1_yield",
    "trailing_3_mean",
)
WEATHER_COLUMNS = (
    "precipitation_total_mm",
    "wet_day_count",
    "mean_temperature_c",
    "max_temperature_c",
)
DEFAULT_EVALUATION_YEARS = (2018, 2019, 2020, 2021, 2022, 2023)


@dataclass(frozen=True)
class BenchmarkRow:
    """One leakage-safe county-year row exposed to a benchmark model."""

    county_id: str
    year: int
    yield_t_per_ha: float
    provisional: bool
    temporal_features: Mapping[str, FeatureValue]
    weather_features: Mapping[str, FeatureValue]

    def features(self, *, include_weather: bool) -> Mapping[str, FeatureValue]:
        if not include_weather:
            return self.temporal_features
        return {**self.temporal_features, **self.weather_features}


@dataclass(frozen=True)
class TemporalFold:
    """Expanding-window temporal context and one evaluation year."""

    evaluation_year: int
    training: tuple[BenchmarkRow, ...]
    evaluation: tuple[BenchmarkRow, ...]
    county_means: Mapping[str, float]


@dataclass(frozen=True)
class ExtendedMetrics:
    mae: float
    rmse: float
    median_absolute_error: float
    mean_error: float
    worst_absolute_error: float
    counties_beating_county_mean: int
    evaluated_counties: int


@dataclass(frozen=True)
class AggregateModelResult:
    pooled: ExtendedMetrics
    mean_fold_mae: float
    median_fold_mae: float
    fold_wins_vs_county_mean: int
    county_win_rate: float


@dataclass(frozen=True)
class AggregateResult:
    models: Mapping[str, AggregateModelResult]

    @classmethod
    def from_test_values(
        cls,
        *,
        county_mean: ExtendedMetrics,
        tabfm_temporal: ExtendedMetrics,
        tabfm_weather: ExtendedMetrics,
        tabfm_weather_fold_wins: int,
    ) -> "AggregateResult":
        """Build a compact aggregate fixture for decision-rule unit tests."""

        def model(metric: ExtendedMetrics, wins: int = 0) -> AggregateModelResult:
            return AggregateModelResult(
                pooled=metric,
                mean_fold_mae=metric.mae,
                median_fold_mae=metric.mae,
                fold_wins_vs_county_mean=wins,
                county_win_rate=(
                    metric.counties_beating_county_mean / metric.evaluated_counties
                    if metric.evaluated_counties
                    else 0.0
                ),
            )

        return cls(
            models={
                "county_mean": model(county_mean),
                "tabfm_temporal": model(tabfm_temporal),
                "tabfm_weather": model(tabfm_weather, tabfm_weather_fold_wins),
            }
        )


@dataclass(frozen=True)
class BenchmarkDecision:
    code: str
    headline: str
    rationale: str


def _row_from_lagged(row: object, feature: WeatherFeature) -> BenchmarkRow:
    county_id = str(getattr(row, "county_id"))
    year = int(getattr(row, "year"))
    return BenchmarkRow(
        county_id=county_id,
        year=year,
        yield_t_per_ha=float(getattr(row, "yield_t_per_ha")),
        provisional=bool(getattr(row, "provisional")),
        temporal_features={
            "county_id": county_id,
            "year": year,
            "lag_1_yield": float(getattr(row, "lag_1_yield")),
            "trailing_3_mean": float(getattr(row, "trailing_3_mean")),
        },
        weather_features={
            "precipitation_total_mm": float(feature.precipitation_total_mm),
            "wet_day_count": int(feature.wet_day_count),
            "mean_temperature_c": float(feature.mean_temperature_c),
            "max_temperature_c": float(feature.max_temperature_c),
        },
    )


def _county_means_from_examples(
    examples: Sequence[PanelExample], evaluation_year: int
) -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for row in examples:
        if row.year < evaluation_year:
            grouped.setdefault(row.county_id, []).append(row.yield_t_per_ha)
    return {county: float(np.mean(values)) for county, values in grouped.items()}


def build_temporal_folds(
    examples: Sequence[PanelExample],
    weather_features: Sequence[WeatherFeature],
    *,
    evaluation_years: Sequence[int] = DEFAULT_EVALUATION_YEARS,
) -> tuple[TemporalFold, ...]:
    """Build deterministic expanding-window folds without future labels."""

    years = tuple(sorted(set(int(year) for year in evaluation_years)))
    if not years:
        raise ValueError("at least one evaluation year is required")

    lagged = build_lagged_examples(examples)
    weather_by_key = {
        (feature.county_id, feature.year): feature for feature in weather_features
    }
    selected = tuple(row for row in lagged if row.year <= years[-1])
    missing = sorted(
        {
            (row.county_id, row.year)
            for row in selected
            if (row.county_id, row.year) not in weather_by_key
        }
    )
    if missing:
        raise ValueError(f"weather features are missing county-year rows: {missing[:3]}")

    rows = tuple(
        _row_from_lagged(row, weather_by_key[(row.county_id, row.year)])
        for row in selected
    )
    folds: list[TemporalFold] = []
    for year in years:
        training = tuple(row for row in rows if row.year < year)
        evaluation = tuple(row for row in rows if row.year == year)
        if not training:
            raise ValueError(f"evaluation year {year} has no historical context")
        if not evaluation:
            raise ValueError(f"evaluation year {year} has no evaluation rows")
        county_means = _county_means_from_examples(examples, year)
        missing_means = sorted({row.county_id for row in evaluation} - set(county_means))
        if missing_means:
            raise ValueError(
                f"county means are missing evaluation counties: {missing_means}"
            )
        folds.append(
            TemporalFold(
                evaluation_year=year,
                training=training,
                evaluation=evaluation,
                county_means=county_means,
            )
        )
    return tuple(folds)


def metrics(
    *,
    actual: Sequence[float],
    predicted: Sequence[float],
    county_mean: Sequence[float],
) -> ExtendedMetrics:
    """Calculate the complete metric contract for one aligned prediction set."""

    if not actual or len(actual) != len(predicted) or len(actual) != len(county_mean):
        raise ValueError("metric inputs must be non-empty and equally sized")
    actual_values = np.asarray(actual, dtype=float)
    predicted_values = np.asarray(predicted, dtype=float)
    county_values = np.asarray(county_mean, dtype=float)
    if not (
        np.isfinite(actual_values).all()
        and np.isfinite(predicted_values).all()
        and np.isfinite(county_values).all()
    ):
        raise ValueError("metric inputs must be finite")
    errors = predicted_values - actual_values
    absolute_errors = np.abs(errors)
    county_absolute_errors = np.abs(county_values - actual_values)
    return ExtendedMetrics(
        mae=float(np.mean(absolute_errors)),
        rmse=float(np.sqrt(np.mean(errors**2))),
        median_absolute_error=float(np.median(absolute_errors)),
        mean_error=float(np.mean(errors)),
        worst_absolute_error=float(np.max(absolute_errors)),
        counties_beating_county_mean=int(
            np.count_nonzero(absolute_errors < county_absolute_errors)
        ),
        evaluated_counties=len(actual_values),
    )


def classify_decision(aggregate: AggregateResult) -> BenchmarkDecision:
    """Apply the approved deterministic TabFM evidence decision rules."""

    try:
        county = aggregate.models["county_mean"].pooled
        temporal = aggregate.models["tabfm_temporal"].pooled
        weather_model = aggregate.models["tabfm_weather"]
    except KeyError as exc:
        raise ValueError(f"aggregate result is missing model: {exc.args[0]}") from exc
    weather = weather_model.pooled

    if temporal.mae < county.mae and weather.mae >= temporal.mae:
        return BenchmarkDecision(
            code="model_go_weather_no_go",
            headline="TabFM improved the temporal model, but weather did not add value.",
            rationale=(
                "The lag-only TabFM benchmark beat county mean while the weather variant "
                "did not improve on lag-only TabFM."
            ),
        )

    if weather.mae < county.mae:
        stable = weather_model.fold_wins_vs_county_mean >= 4
        weather_adds_value = weather.mae < temporal.mae
        tail_limit = county.worst_absolute_error * 1.2
        tail_is_controlled = weather.worst_absolute_error <= tail_limit
        if stable and weather_adds_value and tail_is_controlled:
            return BenchmarkDecision(
                code="strong_go",
                headline="TabFM Weather produced a stable exploratory improvement.",
                rationale=(
                    "It beat county mean on pooled MAE, won at least four folds, "
                    "improved on lag-only TabFM, and kept tail error within the rule."
                ),
            )
        return BenchmarkDecision(
            code="inconclusive",
            headline="TabFM improved pooled error, but the evidence was not stable enough.",
            rationale=(
                "At least one stability, incremental-weather, or tail-error "
                "requirement failed."
            ),
        )

    if temporal.mae < county.mae:
        return BenchmarkDecision(
            code="model_go_weather_no_go",
            headline="TabFM improved the temporal model, but weather did not add value.",
            rationale="Only the lag-only TabFM variant beat county mean on pooled MAE.",
        )

    return BenchmarkDecision(
        code="no_go",
        headline="TabFM did not beat the county historical mean.",
        rationale=(
            "Neither TabFM variant improved pooled MAE over the strongest simple "
            "baseline."
        ),
    )
