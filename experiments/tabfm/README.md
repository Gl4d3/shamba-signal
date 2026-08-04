# Shamba Signal TabFM experiment

This isolated project runs the exploratory rolling temporal benchmark without
adding TabFM, PyTorch, pandas, or Hugging Face dependencies to the Shamba Signal
web application.

## Boundary

- The original frozen 2023 weather experiment remains unchanged.
- Rolling evaluation years are 2018–2023; the 2023 fold is post-hoc and provisional.
- This is retrospective county-year evidence, not an operational or mid-season forecast.
- The default pretrained weights use the `tabfm-non-commercial-v1.0` licence and
  must not be used commercially or in production.

## Setup

```bash
uv sync --project experiments/tabfm --extra dev
```

The project pins Google Research TabFM to commit
`b8a8b090c66d1b9e7af278003461582219996b6a` and uses its PyTorch regression
checkpoint. Model weights are downloaded by TabFM from Hugging Face and remain
outside this repository.

The checked-in environment selects the pinned **CPU** PyTorch wheel for the most
portable default. `--device cuda` is accepted only for users who deliberately
replace that wheel with the matching CUDA-enabled PyTorch build; the runner
fails clearly when CUDA is requested but unavailable.

## Run

```bash
uv run --project experiments/tabfm shamba-tabfm \
  --panel /path/to/modelling_panel.csv \
  --weather-cache data/raw/open-meteo-era5-batch-v1 \
  --output-root data/processed/tabfm-experiment-v1 \
  --device auto
```

The command writes a private predictions CSV and aggregate JSON artifacts. All
outputs remain under the root repository's ignored `data/processed/` tree.

## Contract tests without weights

```bash
uv run --project experiments/tabfm pytest experiments/tabfm/tests -q
```

These tests inject a fake regressor and verify feature columns, categorical
county handling, context configuration, resolved device recording, and
deterministic prediction contracts. They do not download or load the real
checkpoint.
