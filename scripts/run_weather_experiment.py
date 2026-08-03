from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from shamba_signal.modelling.temporal_baselines import Metrics, load_panel_examples
from shamba_signal.modelling.weather_experiment import (
    WEATHER_FEATURE_NAMES,
    WeatherExperiment,
    fetch_open_meteo_features,
    run_weather_experiment,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the bounded county-year Open-Meteo weather value experiment."
    )
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--weather-cache", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--alpha", type=float, action="append", default=None,
        help="Ridge alpha candidate; repeat to override the small default grid.",
    )
    return parser.parse_args()


def _metric_payload(metric: Metrics) -> dict[str, float]:
    return {"mae_t_per_ha": metric.mae, "rmse_t_per_ha": metric.rmse}


def _write_weather_features(path: Path, features: object) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "county_id", "year", "precipitation_total_mm", "wet_day_count",
                "mean_temperature_c", "max_temperature_c",
            ]
        )
        for row in features:
            writer.writerow(
                [
                    row.county_id, row.year, format(row.precipitation_total_mm, ".12g"),
                    row.wet_day_count, format(row.mean_temperature_c, ".12g"),
                    format(row.max_temperature_c, ".12g"),
                ]
            )


def _write_predictions(path: Path, experiment: WeatherExperiment) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "county_id", "year", "split", "provisional", "actual_yield_t_per_ha",
                "previous_year_prediction", "county_mean_prediction", "ridge_prediction",
                "weather_ridge_prediction",
            ]
        )
        for row in experiment.predictions:
            writer.writerow(
                [
                    row.county_id, row.year, row.split, str(row.provisional).lower(),
                    format(row.actual_yield_t_per_ha, ".12g"),
                    format(row.previous_year_prediction, ".12g"),
                    format(row.county_mean_prediction, ".12g"),
                    format(row.ridge_prediction, ".12g"),
                    format(row.weather_ridge_prediction, ".12g"),
                ]
            )


def _build_fixture(
    examples: object, experiment: WeatherExperiment, result: str
) -> dict[str, object]:
    county_history: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in examples:
        county_history[row.county_id].append(
            {
                "year": row.year,
                "actual_yield_t_per_ha": row.yield_t_per_ha,
                "provisional": row.provisional,
            }
        )
    test_prediction_by_county = {
        item.county_id: item for item in experiment.predictions if item.split == "test"
    }
    counties = []
    for county_id in sorted(county_history):
        test = test_prediction_by_county[county_id]
        predicted = {
            "previous_year": test.previous_year_prediction,
            "county_mean": test.county_mean_prediction,
            "ridge": test.ridge_prediction,
            "weather_ridge": test.weather_ridge_prediction,
        }
        counties.append(
            {
                "county_id": county_id,
                "history": sorted(county_history[county_id], key=lambda item: item["year"]),
                "test": {
                    "year": test.year,
                    "provisional": test.provisional,
                    "actual_yield_t_per_ha": test.actual_yield_t_per_ha,
                    "predictions": predicted,
                    "errors_t_per_ha": {
                        name: value - test.actual_yield_t_per_ha
                        for name, value in predicted.items()
                    },
                },
            }
        )
    test_metrics = experiment.test_metrics
    return {
        "fixture_version": "county-year-weather-evaluation-v1",
        "result": result,
        "result_statement": (
            "Weather Ridge did not beat the county historical mean; this is a no-go for this "
            "retrospective feature set."
            if result == "no-go"
            else "Weather Ridge beat the county historical mean on the provisional 2023 test."
        ),
        "provisional_test_year": 2023,
        "selection_year": 2022,
        "feature_definitions": list(WEATHER_FEATURE_NAMES),
        "models": [
            {
                "id": model_id,
                "label": {
                    "previous_year": "Previous year",
                    "county_mean": "County historical mean",
                    "ridge": "Temporal Ridge",
                    "weather_ridge": "Weather Ridge",
                }[model_id],
                **_metric_payload(metric),
            }
            for model_id, metric in test_metrics.items()
        ],
        "limitations": [
            "Annual county labels support a retrospective county-year backtest only.",
            "2023 source labels are provisional.",
            (
                "Weather uses representative county points in ERA5 reanalysis, "
                "not farm or pixel observations."
            ),
            "Same-year production and harvested area are excluded because yield is their ratio.",
            "This is not a mid-season forecast, causal analysis, or farmer advisory system.",
        ],
        "counties": counties,
    }


def main() -> None:
    args = parse_args()
    examples = load_panel_examples(args.panel)
    county_ids = sorted({row.county_id for row in examples})
    weather_features, source_metadata = fetch_open_meteo_features(
        county_ids=county_ids,
        raw_cache_dir=args.weather_cache,
        start_year=min(row.year for row in examples),
        end_year=max(row.year for row in examples),
    )
    experiment = run_weather_experiment(
        examples,
        weather_features,
        alpha_candidates=tuple(args.alpha or (0.01, 0.1, 1.0, 10.0, 100.0)),
    )
    test_metrics = {
        name: _metric_payload(metric) for name, metric in experiment.test_metrics.items()
    }
    result = (
        "keep"
        if test_metrics["weather_ridge"]["mae_t_per_ha"]
        < test_metrics["county_mean"]["mae_t_per_ha"]
        else "no-go"
    )
    args.output_root.mkdir(parents=True, exist_ok=True)
    _write_weather_features(args.output_root / "weather_features.csv", weather_features)
    _write_predictions(args.output_root / "predictions.csv", experiment)
    report = {
        "experiment_version": "county-year-weather-ridge-v1",
        "panel_sha256": hashlib.sha256(args.panel.read_bytes()).hexdigest(),
        "source": source_metadata,
        "feature_contract": list(WEATHER_FEATURE_NAMES),
        "retrospective_only": True,
        "excluded_as_leakage": ["same-year production", "same-year harvested area"],
        "selected_ridge_alpha_on_2022": experiment.selected_alpha,
        "validation_metrics": {
            name: _metric_payload(metric) for name, metric in experiment.validation_metrics.items()
        },
        "test_metrics": test_metrics,
        "result": result,
        "decision_threshold_mae_t_per_ha": test_metrics["county_mean"]["mae_t_per_ha"],
        "test_labels_provisional": True,
    }
    (args.output_root / "results.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    fixture = _build_fixture(examples, experiment, result)
    (args.output_root / "evaluation_fixture.json").write_text(
        json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
