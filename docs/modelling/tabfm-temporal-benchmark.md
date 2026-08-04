# TabFM rolling temporal benchmark

**Status:** implemented experiment path; real checkpoint result not yet claimed

## Research question

Can a pretrained tabular foundation model learn useful nonlinear structure from the same leakage-safe county history and annual ERA5 feature contract used by Shamba Signal—and can it beat the county historical mean consistently through time?

This is a separate exploratory extension. It does not reopen or overwrite the original frozen experiment, where Weather Ridge failed to beat county mean on the one-time provisional-2023 test.

## Model variants

### TabFM Temporal

- `county_id` as categorical text;
- `year`;
- previous-year yield;
- trailing three-year mean yield.

### TabFM Weather

TabFM Temporal plus:

- annual precipitation total;
- wet-day count above 1 mm;
- annual mean 2 m temperature;
- annual maximum 2 m temperature.

Same-year production and harvested area remain excluded because yield is derived from them.

## Rolling protocol

The expanding evaluation years are **2018–2023**. For evaluation year `Y`, every in-context training row has `year < Y`, and every lagged feature uses only observations before `Y`.

The **2018–2022** folds provide the primary repeated temporal evidence. The 2023 fold is post-hoc and provisional: the original study had already inspected those labels and model results, so 2023 is not presented as a new untouched confirmation.

Each fold compares identical county-year rows across:

1. previous year;
2. county historical mean;
3. Temporal Ridge;
4. Weather Ridge;
5. TabFM Temporal; and
6. TabFM Weather.

## Frozen TabFM configuration

The isolated project pins Google Research TabFM to commit `b8a8b090c66d1b9e7af278003461582219996b6a` and uses the PyTorch regression checkpoint.

- 16 ensemble members;
- all available historical context rows via `max_num_rows=None`;
- seed 42;
- alphabetical categorical encoding;
- batch size 1;
- no NNLS weighting;
- no feature-cross or SVD augmentation;
- no context cache.

The experiment fails visibly if this configuration or checkpoint cannot be loaded. It never silently falls back to a random 100-row context.

## Metrics and decision

Per fold and pooled across folds, the benchmark records MAE, RMSE, median absolute error, mean signed error, worst absolute county error, and county wins against county mean.

The generated decision is deterministic:

- **Strong go:** TabFM Weather beats pooled county-mean MAE, wins at least four of six folds, improves on TabFM Temporal, and keeps worst error within 20% of county mean.
- **Model go, weather no-go:** TabFM Temporal beats county mean but the weather variant adds no improvement.
- **Inconclusive:** pooled MAE improves but stability, incremental-weather value, or tail-error requirements fail.
- **No-go:** neither TabFM variant beats county mean on pooled MAE.

A good TabFM score alone does not prove weather value. The relevant weather test is TabFM Weather versus TabFM Temporal.

## Private artifacts

A real run writes the following under ignored `data/processed/tabfm-experiment-v1/`:

- `experiment_manifest.json`;
- `fold_metrics.json`;
- `aggregate_metrics.json`;
- `decision.json`;
- `predictions.csv`;
- `dashboard_fixture.json`.

`predictions.csv` contains source-derived county rows and remains private. The dashboard fixture contains aggregate and fold-level evidence only; it deliberately excludes county predictions.

## Run

```bash
make tabfm-test
make tabfm-run \
  TABFM_PANEL=/path/to/modelling_panel.csv \
  TABFM_WEATHER_CACHE=data/raw/open-meteo-era5-batch-v1
```

Optional environment variables:

- `TABFM_OUTPUT_ROOT`, default `data/processed/tabfm-experiment-v1`;
- `TABFM_DEVICE`, one of `auto`, `cpu`, or `cuda`.

## Licence and interpretation boundary

The default pretrained weights use the separate `tabfm-non-commercial-v1.0` licence and are restricted to non-commercial, non-production research use.

This remains a retrospective county-year benchmark. It is not a mid-season or operational forecast, causal explanation, farm-level estimate, or agronomic advisory. A **future untouched year** would provide stronger confirmation than the already-seen provisional 2023 fold.
