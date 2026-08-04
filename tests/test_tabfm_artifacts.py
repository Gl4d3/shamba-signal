from __future__ import annotations

import csv
import json
from pathlib import Path

from shamba_signal.modelling.tabfm_benchmark import BenchmarkRow, build_temporal_folds
from shamba_signal.modelling.tabfm_execution import (
    MODEL_NAMES,
    run_tabfm_benchmark,
    write_benchmark_artifacts,
)
from shamba_signal.modelling.temporal_baselines import PanelExample
from shamba_signal.modelling.weather_experiment import WeatherFeature


class FakeProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, int]] = []

    def predict(
        self,
        *,
        model_name: str,
        training_rows: tuple[BenchmarkRow, ...],
        evaluation_rows: tuple[BenchmarkRow, ...],
    ) -> tuple[float, ...]:
        self.calls.append((model_name, len(training_rows), len(evaluation_rows)))
        offset = 0.08 if model_name == "tabfm_temporal" else 0.04
        return tuple(row.yield_t_per_ha + offset for row in evaluation_rows)


def _examples() -> tuple[PanelExample, ...]:
    return tuple(
        PanelExample(
            county_id=county,
            year=year,
            yield_t_per_ha=base + (year - 2012) * slope,
            split=(
                "train"
                if year < 2018
                else "validation"
                if year == 2018
                else "test"
            ),
            provisional=year == 2019,
        )
        for year in range(2012, 2020)
        for county, base, slope in (
            ("alpha", 1.0, 0.10),
            ("beta", 2.0, 0.05),
        )
    )


def _weather() -> tuple[WeatherFeature, ...]:
    return tuple(
        WeatherFeature(
            county_id=county,
            year=year,
            precipitation_total_mm=600.0 + 5 * (year - 2012) + offset,
            wet_day_count=80 + (year - 2012),
            mean_temperature_c=20.0 + offset,
            max_temperature_c=29.0 + offset,
        )
        for year in range(2012, 2020)
        for county, offset in (("alpha", 0.0), ("beta", 1.0))
    )


def test_runner_compares_six_models_on_identical_fold_rows() -> None:
    folds = build_temporal_folds(
        _examples(), _weather(), evaluation_years=(2018, 2019)
    )
    provider = FakeProvider()

    result = run_tabfm_benchmark(
        folds,
        provider=provider,
        manifest={"checkpoint": "fake-regression", "random_state": 42},
    )

    assert result.schema_version == "tabfm-experiment-v1"
    assert len(result.folds) == 2
    assert set(result.aggregate.models) == set(MODEL_NAMES)
    assert all(set(fold.predictions) == set(MODEL_NAMES) for fold in result.folds)
    assert provider.calls == [
        ("tabfm_temporal", 10, 2),
        ("tabfm_weather", 10, 2),
        ("tabfm_temporal", 12, 2),
        ("tabfm_weather", 12, 2),
    ]
    assert result.manifest["checkpoint"] == "fake-regression"


def test_artifact_writer_separates_private_predictions_from_dashboard_fixture(
    tmp_path: Path,
) -> None:
    result = run_tabfm_benchmark(
        build_temporal_folds(
            _examples(), _weather(), evaluation_years=(2018, 2019)
        ),
        provider=FakeProvider(),
        manifest={"checkpoint": "fake-regression", "random_state": 42},
    )

    paths = write_benchmark_artifacts(result, tmp_path)

    assert set(paths) == {
        "experiment_manifest",
        "fold_metrics",
        "aggregate_metrics",
        "decision",
        "predictions",
        "dashboard_fixture",
    }
    fixture = json.loads(paths["dashboard_fixture"].read_text(encoding="utf-8"))
    assert fixture["schema_version"] == "tabfm-experiment-v1"
    assert fixture["study_type"] == "exploratory_rolling_temporal"
    assert "predictions" not in fixture
    assert fixture["decision"]["code"] == result.decision.code

    with paths["predictions"].open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 4
    assert set(MODEL_NAMES).issubset(rows[0])
    assert rows[-1]["provisional"] == "true"
