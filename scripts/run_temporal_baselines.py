from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from shamba_signal.modelling.temporal_baselines import (
    Metrics,
    load_panel_examples,
    run_baseline_experiment,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run leakage-safe county-year yield baselines."
    )
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--alpha",
        type=float,
        action="append",
        default=None,
        help="Ridge alpha candidate; repeat to override the default grid.",
    )
    return parser.parse_args()


def _metric_payload(metric: Metrics) -> dict[str, float]:
    return {"mae_t_per_ha": metric.mae, "rmse_t_per_ha": metric.rmse}


def main() -> None:
    args = parse_args()
    examples = load_panel_examples(args.panel)
    experiment = run_baseline_experiment(
        examples,
        alpha_candidates=tuple(args.alpha or (0.01, 0.1, 1.0, 10.0, 100.0)),
    )
    validation_metrics = {
        name: _metric_payload(metric)
        for name, metric in experiment.validation_metrics.items()
    }
    test_metrics = {
        name: _metric_payload(metric) for name, metric in experiment.test_metrics.items()
    }
    test_winner = min(test_metrics, key=lambda name: test_metrics[name]["mae_t_per_ha"])
    result = {
        "experiment_version": "county-year-temporal-baselines-v1",
        "feature_contract": [
            "county identity",
            "year trend",
            "previous-year yield",
            "trailing-three-observation mean",
        ],
        "excluded_as_leakage": ["same-year production", "same-year harvested area"],
        "selected_ridge_alpha": experiment.selected_alpha,
        "validation_year": 2022,
        "test_year": 2023,
        "test_labels_provisional": True,
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "test_winner_by_mae": test_winner,
        "ridge_beats_previous_year": (
            test_metrics["ridge"]["mae_t_per_ha"]
            < test_metrics["previous_year"]["mae_t_per_ha"]
        ),
        "prediction_rows": len(experiment.predictions),
    }
    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / "results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (args.output_root / "predictions.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "county_id",
                "year",
                "split",
                "provisional",
                "actual_yield_t_per_ha",
                "previous_year_prediction",
                "county_mean_prediction",
                "ridge_prediction",
            ]
        )
        for item in experiment.predictions:
            writer.writerow(
                [
                    item.county_id,
                    item.year,
                    item.split,
                    str(item.provisional).lower(),
                    format(item.actual_yield_t_per_ha, ".12g"),
                    format(item.previous_year_prediction, ".12g"),
                    format(item.county_mean_prediction, ".12g"),
                    format(item.ridge_prediction, ".12g"),
                ]
            )
    (args.output_root / "report.md").write_text(
        "\n".join(
            [
                "# County-year temporal baseline result",
                "",
                f"- Selected ridge alpha on 2022: {experiment.selected_alpha:g}.",
                f"- Provisional-2023 winner by MAE: {test_winner}.",
                (
                    "- Ridge beats previous-year MAE: "
                    f"{str(result['ridge_beats_previous_year']).lower()}."
                ),
                "- Same-year production and harvested area are excluded as target leakage.",
                "",
                "## Provisional-2023 metrics",
                "",
                *(
                    f"- {name}: MAE {metrics['mae_t_per_ha']:.4f} t/ha; "
                    f"RMSE {metrics['rmse_t_per_ha']:.4f} t/ha."
                    for name, metrics in test_metrics.items()
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
