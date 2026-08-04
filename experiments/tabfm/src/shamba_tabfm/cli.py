"""Command-line entrypoint for the isolated TabFM temporal benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from shamba_signal.modelling.tabfm_benchmark import (
    DEFAULT_EVALUATION_YEARS,
    TEMPORAL_COLUMNS,
    WEATHER_COLUMNS,
    build_temporal_folds,
)
from shamba_signal.modelling.tabfm_execution import (
    run_tabfm_benchmark,
    write_benchmark_artifacts,
)
from shamba_signal.modelling.temporal_baselines import load_panel_examples
from shamba_signal.modelling.weather_experiment import fetch_open_meteo_features
from shamba_tabfm.provider import load_pytorch_provider


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the exploratory Shamba Signal TabFM temporal benchmark."
    )
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--weather-cache", type=Path, required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/processed/tabfm-experiment-v1"),
    )
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    examples = load_panel_examples(args.panel)
    county_ids = sorted({row.county_id for row in examples})
    weather, weather_metadata = fetch_open_meteo_features(
        county_ids=county_ids,
        raw_cache_dir=args.weather_cache,
        start_year=min(row.year for row in examples),
        end_year=max(row.year for row in examples),
    )
    folds = build_temporal_folds(
        examples,
        weather,
        evaluation_years=DEFAULT_EVALUATION_YEARS,
    )
    provider = load_pytorch_provider(device=args.device)
    manifest = {
        **provider.manifest,
        "evaluation_years": list(DEFAULT_EVALUATION_YEARS),
        "post_hoc_years": [2023],
        "temporal_columns": list(TEMPORAL_COLUMNS),
        "weather_columns": list(WEATHER_COLUMNS),
        "context_rows_by_fold": {
            str(fold.evaluation_year): len(fold.training) for fold in folds
        },
        "weather_source": weather_metadata,
        "checkpoint_license": "tabfm-non-commercial-v1.0",
    }
    result = run_tabfm_benchmark(folds, provider=provider, manifest=manifest)
    paths = write_benchmark_artifacts(result, args.output_root)
    print(
        json.dumps(
            {
                "decision": result.decision.code,
                "output_root": str(args.output_root),
                "artifacts": {name: str(path) for name, path in paths.items()},
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0
