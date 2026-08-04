"""Execution and artifact layer for the exploratory TabFM benchmark."""

from __future__ import annotations

import csv
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

import numpy as np

from shamba_signal.modelling.tabfm_benchmark import (
    AggregateModelResult,
    AggregateResult,
    BenchmarkDecision,
    BenchmarkRow,
    ExtendedMetrics,
    TemporalFold,
    classify_decision,
    metrics,
)

SCHEMA_VERSION = "tabfm-experiment-v1"
MODEL_NAMES = (
    "previous_year",
    "county_mean",
    "ridge",
    "weather_ridge",
    "tabfm_temporal",
    "tabfm_weather",
)


class PredictionProvider(Protocol):
    def predict(
        self,
        *,
        model_name: str,
        training_rows: tuple[BenchmarkRow, ...],
        evaluation_rows: tuple[BenchmarkRow, ...],
    ) -> Sequence[float]: ...


@dataclass(frozen=True)
class FoldResult:
    evaluation_year: int
    provisional: bool
    counties: tuple[str, ...]
    actual: tuple[float, ...]
    county_mean: tuple[float, ...]
    predictions: Mapping[str, tuple[float, ...]]
    metrics: Mapping[str, ExtendedMetrics]


@dataclass(frozen=True)
class BenchmarkResult:
    schema_version: str
    folds: tuple[FoldResult, ...]
    aggregate: AggregateResult
    decision: BenchmarkDecision
    manifest: Mapping[str, object]


def _design_matrix(
    rows: Sequence[BenchmarkRow],
    *,
    counties: Sequence[str],
    include_weather: bool,
) -> np.ndarray:
    values: list[list[float]] = []
    for row in rows:
        temporal = row.temporal_features
        feature_values = [
            float(temporal["year"]) - 2012.0,
            float(temporal["lag_1_yield"]),
            float(temporal["trailing_3_mean"]),
        ]
        if include_weather:
            weather = row.weather_features
            feature_values.extend(
                [
                    float(weather["precipitation_total_mm"]),
                    float(weather["wet_day_count"]),
                    float(weather["mean_temperature_c"]),
                    float(weather["max_temperature_c"]),
                ]
            )
        feature_values.extend(
            1.0 if row.county_id == county else 0.0 for county in counties[1:]
        )
        values.append(feature_values)
    return np.asarray(values, dtype=float)


def _ridge_predict(
    training: Sequence[BenchmarkRow],
    evaluation: Sequence[BenchmarkRow],
    *,
    include_weather: bool,
    alpha: float = 100.0,
) -> tuple[float, ...]:
    counties = tuple(sorted({row.county_id for row in training}))
    unknown = sorted({row.county_id for row in evaluation} - set(counties))
    if unknown:
        raise ValueError(f"ridge evaluation contains unseen counties: {unknown}")
    raw_train = _design_matrix(
        training, counties=counties, include_weather=include_weather
    )
    raw_eval = _design_matrix(
        evaluation, counties=counties, include_weather=include_weather
    )
    means = raw_train.mean(axis=0)
    scales = raw_train.std(axis=0)
    scales[scales == 0] = 1.0
    train_design = np.column_stack(
        [np.ones(len(training)), (raw_train - means) / scales]
    )
    eval_design = np.column_stack(
        [np.ones(len(evaluation)), (raw_eval - means) / scales]
    )
    target = np.asarray([row.yield_t_per_ha for row in training], dtype=float)
    penalty = np.eye(train_design.shape[1])
    penalty[0, 0] = 0.0
    coefficients = np.linalg.solve(
        train_design.T @ train_design + alpha * penalty,
        train_design.T @ target,
    )
    return tuple(float(value) for value in eval_design @ coefficients)


def _validated_predictions(
    values: Sequence[float], *, expected: int, model_name: str
) -> tuple[float, ...]:
    predictions = tuple(float(value) for value in values)
    if len(predictions) != expected:
        raise ValueError(
            f"{model_name} returned {len(predictions)} predictions for {expected} rows"
        )
    if not all(math.isfinite(value) for value in predictions):
        raise ValueError(f"{model_name} returned non-finite predictions")
    return predictions


def _aggregate_fold_results(folds: Sequence[FoldResult]) -> AggregateResult:
    if not folds:
        raise ValueError("at least one fold result is required")
    model_results: dict[str, AggregateModelResult] = {}
    pooled_actual = tuple(value for fold in folds for value in fold.actual)
    pooled_county = tuple(value for fold in folds for value in fold.county_mean)
    for model_name in MODEL_NAMES:
        pooled_prediction = tuple(
            value for fold in folds for value in fold.predictions[model_name]
        )
        pooled = metrics(
            actual=pooled_actual,
            predicted=pooled_prediction,
            county_mean=pooled_county,
        )
        fold_maes = [fold.metrics[model_name].mae for fold in folds]
        wins = sum(
            fold.metrics[model_name].mae < fold.metrics["county_mean"].mae
            for fold in folds
        )
        model_results[model_name] = AggregateModelResult(
            pooled=pooled,
            mean_fold_mae=float(np.mean(fold_maes)),
            median_fold_mae=float(np.median(fold_maes)),
            fold_wins_vs_county_mean=int(wins),
            county_win_rate=(
                pooled.counties_beating_county_mean / pooled.evaluated_counties
                if pooled.evaluated_counties
                else 0.0
            ),
        )
    return AggregateResult(models=model_results)


def run_tabfm_benchmark(
    folds: Sequence[TemporalFold],
    *,
    provider: PredictionProvider,
    manifest: Mapping[str, object],
) -> BenchmarkResult:
    """Run identical rolling folds through baselines and both TabFM variants."""

    results: list[FoldResult] = []
    for fold in folds:
        actual = tuple(row.yield_t_per_ha for row in fold.evaluation)
        county_mean = tuple(
            fold.county_means[row.county_id] for row in fold.evaluation
        )
        predictions: dict[str, tuple[float, ...]] = {
            "previous_year": tuple(
                float(row.temporal_features["lag_1_yield"])
                for row in fold.evaluation
            ),
            "county_mean": county_mean,
            "ridge": _ridge_predict(
                fold.training, fold.evaluation, include_weather=False
            ),
            "weather_ridge": _ridge_predict(
                fold.training, fold.evaluation, include_weather=True
            ),
        }
        for model_name in ("tabfm_temporal", "tabfm_weather"):
            predictions[model_name] = _validated_predictions(
                provider.predict(
                    model_name=model_name,
                    training_rows=fold.training,
                    evaluation_rows=fold.evaluation,
                ),
                expected=len(fold.evaluation),
                model_name=model_name,
            )
        fold_metrics = {
            model_name: metrics(
                actual=actual,
                predicted=predictions[model_name],
                county_mean=county_mean,
            )
            for model_name in MODEL_NAMES
        }
        results.append(
            FoldResult(
                evaluation_year=fold.evaluation_year,
                provisional=any(row.provisional for row in fold.evaluation),
                counties=tuple(row.county_id for row in fold.evaluation),
                actual=actual,
                county_mean=county_mean,
                predictions=predictions,
                metrics=fold_metrics,
            )
        )
    aggregate = _aggregate_fold_results(results)
    return BenchmarkResult(
        schema_version=SCHEMA_VERSION,
        folds=tuple(results),
        aggregate=aggregate,
        decision=classify_decision(aggregate),
        manifest=dict(manifest),
    )


def _metrics_payload(metric: ExtendedMetrics) -> dict[str, object]:
    return asdict(metric)


def _fold_payload(fold: FoldResult) -> dict[str, object]:
    return {
        "evaluation_year": fold.evaluation_year,
        "provisional": fold.provisional,
        "county_count": len(fold.counties),
        "metrics": {
            name: _metrics_payload(fold.metrics[name]) for name in MODEL_NAMES
        },
    }


def _aggregate_payload(aggregate: AggregateResult) -> dict[str, object]:
    return {
        name: {
            "pooled": _metrics_payload(result.pooled),
            "mean_fold_mae": result.mean_fold_mae,
            "median_fold_mae": result.median_fold_mae,
            "fold_wins_vs_county_mean": result.fold_wins_vs_county_mean,
            "county_win_rate": result.county_win_rate,
        }
        for name, result in aggregate.models.items()
    }


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _write_json(path: Path, payload: object) -> None:
    _atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_benchmark_artifacts(
    result: BenchmarkResult, output_root: Path
) -> dict[str, Path]:
    """Write private row evidence and dashboard-safe aggregates atomically."""

    paths = {
        "experiment_manifest": output_root / "experiment_manifest.json",
        "fold_metrics": output_root / "fold_metrics.json",
        "aggregate_metrics": output_root / "aggregate_metrics.json",
        "decision": output_root / "decision.json",
        "predictions": output_root / "predictions.csv",
        "dashboard_fixture": output_root / "dashboard_fixture.json",
    }
    fold_payload = [_fold_payload(fold) for fold in result.folds]
    aggregate_payload = _aggregate_payload(result.aggregate)
    decision_payload = asdict(result.decision)
    manifest_payload = {
        "schema_version": result.schema_version,
        **dict(result.manifest),
    }
    _write_json(paths["experiment_manifest"], manifest_payload)
    _write_json(paths["fold_metrics"], fold_payload)
    _write_json(paths["aggregate_metrics"], aggregate_payload)
    _write_json(paths["decision"], decision_payload)

    paths["predictions"].parent.mkdir(parents=True, exist_ok=True)
    temporary_csv = paths["predictions"].with_suffix(".csv.tmp")
    with temporary_csv.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "evaluation_year",
            "county_id",
            "actual_yield_t_per_ha",
            "provisional",
            *MODEL_NAMES,
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for fold in result.folds:
            for index, county_id in enumerate(fold.counties):
                writer.writerow(
                    {
                        "evaluation_year": fold.evaluation_year,
                        "county_id": county_id,
                        "actual_yield_t_per_ha": fold.actual[index],
                        "provisional": str(fold.provisional).lower(),
                        **{
                            model_name: fold.predictions[model_name][index]
                            for model_name in MODEL_NAMES
                        },
                    }
                )
    temporary_csv.replace(paths["predictions"])

    dashboard_payload = {
        "schema_version": result.schema_version,
        "study_type": "exploratory_rolling_temporal",
        "evaluation_years": [fold.evaluation_year for fold in result.folds],
        "post_hoc_years": [
            fold.evaluation_year
            for fold in result.folds
            if fold.evaluation_year == 2023
        ],
        "models": list(MODEL_NAMES),
        "folds": fold_payload,
        "aggregate": aggregate_payload,
        "decision": decision_payload,
        "manifest": manifest_payload,
        "boundary": (
            "Retrospective county-year benchmark; not an operational forecast, "
            "causal model, farm estimate, or agronomic advisory."
        ),
        "checkpoint_license": "tabfm-non-commercial-v1.0",
    }
    _write_json(paths["dashboard_fixture"], dashboard_payload)
    return paths
