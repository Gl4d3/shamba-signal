from __future__ import annotations

import csv
import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np

Split = Literal["train", "validation", "test"]


@dataclass(frozen=True)
class PanelExample:
    county_id: str
    year: int
    yield_t_per_ha: float
    split: Split
    provisional: bool


@dataclass(frozen=True)
class LaggedExample:
    county_id: str
    year: int
    yield_t_per_ha: float
    split: Split
    provisional: bool
    lag_1_yield: float
    trailing_3_mean: float


@dataclass(frozen=True)
class Prediction:
    county_id: str
    year: int
    actual_yield_t_per_ha: float
    split: Split
    provisional: bool
    previous_year_prediction: float
    county_mean_prediction: float
    ridge_prediction: float


@dataclass(frozen=True)
class Metrics:
    mae: float
    rmse: float


@dataclass(frozen=True)
class BaselineExperiment:
    selected_alpha: float
    validation_metrics: Mapping[str, Metrics]
    test_metrics: Mapping[str, Metrics]
    predictions: tuple[Prediction, ...]


@dataclass(frozen=True)
class _RidgeModel:
    counties: tuple[str, ...]
    means: np.ndarray
    scales: np.ndarray
    coefficients: np.ndarray


def load_panel_examples(path: Path) -> tuple[PanelExample, ...]:
    """Load usable labels from the private modelling-panel contract."""
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            records = list(csv.DictReader(handle))
    except OSError as exc:
        raise ValueError(f"could not read modelling panel: {path}") from exc
    required = {
        "county_id",
        "year",
        "active_yield_t_per_ha",
        "split",
        "provisional",
        "usable_for_modelling",
    }
    if not records or not required.issubset(records[0]):
        raise ValueError("modelling panel is missing required columns or rows")
    examples: list[PanelExample] = []
    for record in records:
        if record["usable_for_modelling"] not in {"true", "false"}:
            raise ValueError("usable_for_modelling must be true or false")
        if record["usable_for_modelling"] == "false":
            continue
        split = record["split"]
        if split not in {"train", "validation", "test"}:
            raise ValueError(f"unsupported modelling split: {split}")
        provisional = record["provisional"]
        if provisional not in {"true", "false"}:
            raise ValueError("provisional must be true or false")
        try:
            year = int(record["year"])
            yield_value = float(record["active_yield_t_per_ha"])
        except ValueError as exc:
            raise ValueError("modelling panel year and yield must be numeric") from exc
        examples.append(
            PanelExample(
                county_id=record["county_id"],
                year=year,
                yield_t_per_ha=yield_value,
                split=split,
                provisional=provisional == "true",
            )
        )
    return tuple(sorted(examples, key=lambda item: (item.year, item.county_id)))


def build_lagged_examples(examples: Sequence[PanelExample]) -> tuple[LaggedExample, ...]:
    """Create lag features using only earlier values from the same county."""
    grouped: dict[str, list[PanelExample]] = defaultdict(list)
    for item in examples:
        if not math.isfinite(item.yield_t_per_ha):
            raise ValueError("panel yields must be finite")
        grouped[item.county_id].append(item)

    rows: list[LaggedExample] = []
    for county_id, county_rows in grouped.items():
        ordered = sorted(county_rows, key=lambda item: item.year)
        seen_years: set[int] = set()
        for index, item in enumerate(ordered):
            if item.year in seen_years:
                raise ValueError(f"duplicate panel row: {county_id} {item.year}")
            seen_years.add(item.year)
            if index == 0 or ordered[index - 1].year != item.year - 1:
                continue
            history = ordered[:index]
            rows.append(
                LaggedExample(
                    county_id=county_id,
                    year=item.year,
                    yield_t_per_ha=item.yield_t_per_ha,
                    split=item.split,
                    provisional=item.provisional,
                    lag_1_yield=history[-1].yield_t_per_ha,
                    trailing_3_mean=sum(row.yield_t_per_ha for row in history[-3:])
                    / len(history[-3:]),
                )
            )
    return tuple(sorted(rows, key=lambda item: (item.year, item.county_id)))


def _raw_features(row: LaggedExample, counties: Sequence[str]) -> list[float]:
    return [
        float(row.year - 2012),
        row.lag_1_yield,
        row.trailing_3_mean,
        *(1.0 if row.county_id == county else 0.0 for county in counties[1:]),
    ]


def _fit_ridge(rows: Sequence[LaggedExample], *, alpha: float) -> _RidgeModel:
    if alpha < 0 or not math.isfinite(alpha):
        raise ValueError("ridge alpha must be finite and non-negative")
    counties = tuple(sorted({row.county_id for row in rows}))
    if not rows or not counties:
        raise ValueError("ridge training requires examples")
    raw = np.asarray([_raw_features(row, counties) for row in rows], dtype=float)
    means = raw.mean(axis=0)
    scales = raw.std(axis=0)
    scales[scales == 0] = 1.0
    design = np.column_stack([np.ones(len(rows)), (raw - means) / scales])
    target = np.asarray([row.yield_t_per_ha for row in rows], dtype=float)
    penalty = np.eye(design.shape[1])
    penalty[0, 0] = 0.0
    coefficients = np.linalg.solve(
        design.T @ design + alpha * penalty,
        design.T @ target,
    )
    return _RidgeModel(
        counties=counties,
        means=means,
        scales=scales,
        coefficients=coefficients,
    )


def _predict_ridge(model: _RidgeModel, rows: Sequence[LaggedExample]) -> np.ndarray:
    raw = np.asarray([_raw_features(row, model.counties) for row in rows], dtype=float)
    design = np.column_stack([np.ones(len(rows)), (raw - model.means) / model.scales])
    return design @ model.coefficients


def _county_means(rows: Sequence[PanelExample | LaggedExample]) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[row.county_id].append(row.yield_t_per_ha)
    return {county: sum(values) / len(values) for county, values in grouped.items()}


def _metrics(actual: Sequence[float], predicted: Sequence[float]) -> Metrics:
    errors = np.asarray(predicted, dtype=float) - np.asarray(actual, dtype=float)
    return Metrics(
        mae=float(np.mean(np.abs(errors))),
        rmse=float(np.sqrt(np.mean(errors**2))),
    )


def _metric_set(predictions: Sequence[Prediction]) -> dict[str, Metrics]:
    actual = [item.actual_yield_t_per_ha for item in predictions]
    return {
        "previous_year": _metrics(
            actual, [item.previous_year_prediction for item in predictions]
        ),
        "county_mean": _metrics(
            actual, [item.county_mean_prediction for item in predictions]
        ),
        "ridge": _metrics(actual, [item.ridge_prediction for item in predictions]),
    }


def _predict_period(
    *,
    ridge_training: Sequence[LaggedExample],
    reference_training: Sequence[PanelExample],
    evaluation: Sequence[LaggedExample],
    alpha: float,
) -> tuple[Prediction, ...]:
    model = _fit_ridge(ridge_training, alpha=alpha)
    ridge_predictions = _predict_ridge(model, evaluation)
    county_means = _county_means(reference_training)
    return tuple(
        Prediction(
            county_id=row.county_id,
            year=row.year,
            actual_yield_t_per_ha=row.yield_t_per_ha,
            split=row.split,
            provisional=row.provisional,
            previous_year_prediction=row.lag_1_yield,
            county_mean_prediction=county_means[row.county_id],
            ridge_prediction=float(ridge_prediction),
        )
        for row, ridge_prediction in zip(evaluation, ridge_predictions, strict=True)
    )


def run_baseline_experiment(
    examples: Sequence[PanelExample],
    *,
    alpha_candidates: Sequence[float],
) -> BaselineExperiment:
    """Select ridge regularization on 2022, then evaluate once on 2023."""
    if not alpha_candidates:
        raise ValueError("at least one ridge alpha candidate is required")
    lagged = build_lagged_examples(examples)
    reference_train = tuple(row for row in examples if row.split == "train")
    reference_train_and_validation = tuple(
        row for row in examples if row.split in {"train", "validation"}
    )
    train = tuple(row for row in lagged if row.split == "train")
    validation = tuple(row for row in lagged if row.split == "validation")
    test = tuple(row for row in lagged if row.split == "test")
    if not train or not validation or not test:
        raise ValueError("experiment requires train, validation, and test examples")

    validation_by_alpha: list[tuple[float, tuple[Prediction, ...]]] = []
    for alpha in alpha_candidates:
        validation_by_alpha.append(
            (
                float(alpha),
                _predict_period(
                    ridge_training=train,
                    reference_training=reference_train,
                    evaluation=validation,
                    alpha=float(alpha),
                ),
            )
        )
    selected_alpha, validation_predictions = min(
        validation_by_alpha,
        key=lambda item: (_metric_set(item[1])["ridge"].mae, item[0]),
    )
    test_predictions = _predict_period(
        ridge_training=(*train, *validation),
        reference_training=reference_train_and_validation,
        evaluation=test,
        alpha=selected_alpha,
    )
    return BaselineExperiment(
        selected_alpha=selected_alpha,
        validation_metrics=_metric_set(validation_predictions),
        test_metrics=_metric_set(test_predictions),
        predictions=(*validation_predictions, *test_predictions),
    )
