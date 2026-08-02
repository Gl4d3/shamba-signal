from __future__ import annotations

import math
from pathlib import Path

from shamba_signal.modelling.temporal_baselines import (
    PanelExample,
    build_lagged_examples,
    load_panel_examples,
    run_baseline_experiment,
)


def _panel() -> tuple[PanelExample, ...]:
    rows: list[PanelExample] = []
    for county_id, offset in (("a", 0.0), ("b", 1.0)):
        for year in range(2018, 2024):
            rows.append(
                PanelExample(
                    county_id=county_id,
                    year=year,
                    yield_t_per_ha=offset + (year - 2017) * 0.5,
                    split=(
                        "train" if year <= 2021 else "validation" if year == 2022 else "test"
                    ),
                    provisional=year == 2023,
                )
            )
    return tuple(rows)


def test_build_lagged_examples_uses_only_prior_county_values() -> None:
    rows = build_lagged_examples(_panel())

    validation_a = next(
        row for row in rows if row.county_id == "a" and row.year == 2022
    )
    test_a = next(row for row in rows if row.county_id == "a" and row.year == 2023)

    assert validation_a.lag_1_yield == 2.0
    assert validation_a.trailing_3_mean == 1.5
    assert test_a.lag_1_yield == 2.5
    assert test_a.trailing_3_mean == 2.0


def test_run_baseline_experiment_keeps_validation_and_test_separate() -> None:
    experiment = run_baseline_experiment(_panel(), alpha_candidates=(0.1, 1.0, 10.0))

    validation_a = next(
        item
        for item in experiment.predictions
        if item.county_id == "a" and item.year == 2022
    )
    test_a = next(
        item
        for item in experiment.predictions
        if item.county_id == "a" and item.year == 2023
    )

    assert validation_a.previous_year_prediction == 2.0
    assert validation_a.county_mean_prediction == 1.25
    assert test_a.previous_year_prediction == 2.5
    assert test_a.county_mean_prediction == 1.5
    assert experiment.selected_alpha in {0.1, 1.0, 10.0}
    assert set(experiment.validation_metrics) == {"previous_year", "county_mean", "ridge"}
    assert set(experiment.test_metrics) == {"previous_year", "county_mean", "ridge"}
    assert all(
        math.isfinite(metric.mae) and math.isfinite(metric.rmse)
        for metric in experiment.test_metrics.values()
    )


def test_load_panel_examples_excludes_unusable_labels(tmp_path: Path) -> None:
    panel_path = tmp_path / "panel.csv"
    panel_path.write_text(
        "county_id,year,active_yield_t_per_ha,split,provisional,usable_for_modelling\n"
        "busia,2021,1.2,train,false,true\n"
        "busia,2022,,validation,false,false\n"
        "busia,2023,1.5,test,true,true\n",
        encoding="utf-8",
    )

    rows = load_panel_examples(panel_path)

    assert rows == (
        PanelExample("busia", 2021, 1.2, "train", False),
        PanelExample("busia", 2023, 1.5, "test", True),
    )
