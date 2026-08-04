# TabFM Temporal Benchmark Design

**Status:** Approved for implementation

**Branch:** `experiment/tabfm-temporal-benchmark`

## Objective

Add a reproducible TabFM regression benchmark to Shamba Signal without rewriting or weakening the completed weather experiment. The original 2012–2021 training, 2022 selection, and provisional-2023 one-time test result remains unchanged and continues to be presented as the original bounded study. TabFM is a separate exploratory follow-up evaluated with rolling temporal origins.

## Scientific boundary

The extension remains a retrospective county-year study. Annual ERA5 values describe the completed label year, so the benchmark is not a mid-season forecast, farmer advisory, causal model, farm-level estimate, or deployed service.

The 2023 fold is explicitly post-hoc and exploratory because the project has already inspected those labels and model results. Results from 2018–2022 provide the primary repeated temporal evidence. A strong 2023 score cannot retroactively alter the original experiment's no-go conclusion.

## Architecture

The implementation has three isolated layers:

1. **Dependency-free benchmark core inside the main package.** This layer builds rolling temporal folds, constructs model-ready rows from the existing lag and weather contracts, calculates metrics, applies decision rules, and emits a versioned artifact. It imports no TabFM, PyTorch, pandas, or Hugging Face packages.
2. **Isolated TabFM runner under `experiments/tabfm`.** This environment pins the Google Research TabFM repository commit and PyTorch backend, loads the regression checkpoint, creates pandas DataFrames, and passes predictions into the benchmark core.
3. **Read-only dashboard integration.** FastAPI optionally serves the generated TabFM fixture. The static dashboard renders a clearly labelled Foundation Model Study section only when that artifact exists. The application never loads model weights at request time.

## Data contract

Both TabFM variants use the existing leakage-safe lag features:

- `county_id` as categorical text;
- `year` as numeric;
- `lag_1_yield` as numeric;
- `trailing_3_mean` as numeric.

The weather variant additionally uses:

- `precipitation_total_mm`;
- `wet_day_count`;
- `mean_temperature_c`;
- `max_temperature_c`.

The target is `yield_t_per_ha`.

Same-year production and harvested area remain excluded because yield is derived from them. No future yield value may enter a fold's training context or feature history.

## Temporal evaluation

The rolling evaluation years are 2018, 2019, 2020, 2021, 2022, and 2023. For evaluation year `Y`, every training row must have `year < Y`. Lag features for the evaluation row must use only observations before `Y`.

Each fold compares identical evaluation rows across:

- previous year;
- county historical mean;
- temporal Ridge;
- weather Ridge;
- TabFM Temporal;
- TabFM Weather.

The existing Ridge functions may be reused where their contracts fit. The TabFM core accepts prediction callbacks so unit tests can exercise the full fold and artifact logic without downloading the checkpoint.

## TabFM configuration

The isolated runner uses the PyTorch backend and the pinned Google Research TabFM commit `b8a8b090c66d1b9e7af278003461582219996b6a`.

The frozen default configuration is:

- regression checkpoint `tabfm_v1_0_0`;
- `n_estimators=16`;
- `max_num_rows=None`, so every available historical row is used where the backend permits;
- `max_num_features=500`;
- `batch_size=1`;
- `random_state=42`;
- categorical encoder mode `alphabetical`;
- no NNLS, feature crosses, or SVD augmentation;
- context caching disabled for compatibility and deterministic comparison.

The runner records the exact backend, checkpoint, commit, context rows, feature columns, seed, and ensemble settings in the manifest. It fails visibly rather than silently falling back to random 100-row contexts or a different model.

## Metrics

Per model and fold:

- MAE;
- RMSE;
- median absolute error;
- signed mean error;
- worst absolute county error;
- counties beating the county-mean baseline.

Across folds:

- pooled out-of-fold MAE and RMSE;
- mean and median fold MAE;
- fold wins against county mean;
- county win rate;
- TabFM Weather minus TabFM Temporal MAE.

## Decision rules

The generated decision is one of:

- `strong_go`: TabFM Weather beats county mean on pooled MAE, wins at least four of six folds, beats TabFM Temporal, and does not worsen worst absolute error by more than 20 percent.
- `model_go_weather_no_go`: TabFM Temporal beats county mean on pooled MAE but TabFM Weather does not improve on TabFM Temporal.
- `inconclusive`: TabFM improves pooled MAE but wins fewer than four folds or has materially worse tail error.
- `no_go`: neither TabFM variant beats county mean on pooled MAE.

The decision function is deterministic and uses only generated metrics. The UI does not improvise interpretations.

## Artifacts and privacy

The runner writes to `data/processed/tabfm-experiment-v1/`:

- `experiment_manifest.json`;
- `fold_metrics.json`;
- `aggregate_metrics.json`;
- `decision.json`;
- `predictions.csv`;
- `dashboard_fixture.json`.

All row-level outputs remain ignored by Git. A manually written result note may commit aggregate values only after a real checkpoint run. Model weights and Hugging Face caches remain outside the repository.

## API and dashboard

`create_app` accepts an optional TabFM fixture path and exposes `GET /api/v1/tabfm-evaluation`.

- When the fixture is missing, the endpoint returns HTTP 503 with a precise local-generation message.
- When present, it returns a JSON object only after validating the top-level shape and schema version.

The dashboard adds a `Foundation model` navigation item and section containing:

- an `Exploratory extension` badge;
- pooled model comparison;
- fold-by-fold temporal stability;
- TabFM Temporal versus TabFM Weather;
- the generated decision and evidence boundary;
- configuration and licence notes.

Failure to load this optional endpoint must not break the completed original dashboard.

## Testing

Focused tests cover:

- rolling fold boundaries and no future leakage;
- deterministic model row construction and categorical county preservation;
- metric correctness;
- decision classification;
- artifact schema and privacy split;
- API success and missing-fixture behavior;
- HTML/JavaScript contracts for optional TabFM rendering;
- lazy import behavior so normal application tests do not require TabFM.

A separate smoke command runs the real checkpoint when the isolated environment and weights are available. The normal root verification suite never downloads model weights.

## Non-goals

- Changing the original 2023 result or headline.
- Adding TabFM dependencies to the root runtime.
- Training or fine-tuning TabFM.
- Hyperparameter search against 2023.
- Random-row cross-validation.
- Live inference through FastAPI.
- Commercial or production use of the non-commercial checkpoint.
- Adding new agricultural sources or features during this slice.
