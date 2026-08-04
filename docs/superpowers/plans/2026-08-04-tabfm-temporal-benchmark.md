# TabFM Temporal Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an isolated, reproducible TabFM rolling temporal benchmark and expose its generated evidence as an optional, clearly labelled extension in the Shamba Signal dashboard.

**Architecture:** Keep the root FastAPI application free of TabFM/PyTorch/pandas dependencies. Put deterministic fold, metric, decision, and artifact logic in the main package; run the actual pretrained model from an isolated `experiments/tabfm` environment; have FastAPI and the static dashboard read only the generated JSON fixture.

**Tech Stack:** Python 3.12, NumPy, FastAPI, pytest, TabFM v1.0.0 at commit `b8a8b090c66d1b9e7af278003461582219996b6a`, PyTorch backend, pandas in the isolated experiment only, browser-native JavaScript and SVG.

## Global Constraints

- Preserve the original bounded weather experiment and its no-go result unchanged.
- Label the TabFM work as an exploratory rolling temporal extension.
- Keep 2023 explicitly post-hoc and provisional.
- Add no TabFM, pandas, scikit-learn, PyTorch, or Hugging Face dependency to the root `pyproject.toml`.
- Never download weights during normal root tests or API startup.
- Use only the existing county, lag, and four ERA5 feature contracts.
- Keep source-derived row-level predictions and generated fixtures outside Git.
- Do not present the result as operational forecasting, causal inference, farm-level estimation, or agronomic advice.

---

### Task 1: Core rolling fold contract

**Files:**
- Create: `src/shamba_signal/modelling/tabfm_benchmark.py`
- Create: `tests/test_tabfm_benchmark.py`

**Interfaces:**
- Consumes: `PanelExample`, `LaggedExample`, and `WeatherFeature` from existing modelling modules.
- Produces: `TemporalFold`, `BenchmarkRow`, `build_temporal_folds(examples, weather_features, evaluation_years)`, and feature column constants.

- [ ] **Step 1: Write failing tests for fold chronology and row shape.**

```python
def test_build_temporal_folds_never_places_future_rows_in_context() -> None:
    folds = build_temporal_folds(examples, weather, evaluation_years=(2018, 2019))
    assert [fold.evaluation_year for fold in folds] == [2018, 2019]
    assert all(row.year < fold.evaluation_year for fold in folds for row in fold.training)
    assert all(row.year == fold.evaluation_year for fold in folds for row in fold.evaluation)


def test_tabfm_rows_preserve_county_as_categorical_text() -> None:
    fold = build_temporal_folds(examples, weather, evaluation_years=(2019,))[0]
    assert fold.training[0].temporal_features["county_id"] == "alpha"
    assert tuple(fold.training[0].weather_features) == WEATHER_COLUMNS
```

- [ ] **Step 2: Run `pytest tests/test_tabfm_benchmark.py -q` and confirm imports fail because the module does not exist.**
- [ ] **Step 3: Implement immutable dataclasses, fixed temporal/weather column constants, weather lookup validation, lag construction reuse, and chronological fold building.**
- [ ] **Step 4: Run the focused test and confirm it passes.**
- [ ] **Step 5: Commit `feat: add TabFM rolling fold contract`.**

### Task 2: Metrics, model comparison, and decisions

**Files:**
- Modify: `src/shamba_signal/modelling/tabfm_benchmark.py`
- Modify: `tests/test_tabfm_benchmark.py`

**Interfaces:**
- Consumes: `TemporalFold` and mapping `{model_name: predictions}`.
- Produces: `ExtendedMetrics`, `FoldResult`, `AggregateResult`, `metrics(actual, predicted, county_mean)`, `aggregate_results(folds)`, and `classify_decision(aggregate)`.

- [ ] **Step 1: Add failing tests with hand-calculated MAE, RMSE, median absolute error, bias, worst error, county wins, and all four decision states.**
- [ ] **Step 2: Run the focused test and confirm missing symbols fail.**
- [ ] **Step 3: Implement exact metric calculations and deterministic decision rules from the approved design.**
- [ ] **Step 4: Run the focused test and confirm all cases pass.**
- [ ] **Step 5: Commit `feat: evaluate TabFM temporal evidence`.**

### Task 3: Dependency-injected benchmark runner and artifacts

**Files:**
- Modify: `src/shamba_signal/modelling/tabfm_benchmark.py`
- Create: `tests/test_tabfm_artifacts.py`

**Interfaces:**
- Consumes: `PredictionProvider` protocol with `predict(model_name, training_rows, evaluation_rows) -> Sequence[float]`.
- Produces: `run_tabfm_benchmark(...) -> BenchmarkResult`, `write_benchmark_artifacts(result, output_root, manifest)`, schema version `tabfm-experiment-v1`.

- [ ] **Step 1: Write a failing end-to-end unit test using a deterministic fake provider and two synthetic folds.**
- [ ] **Step 2: Assert the output contains six model names, fold metrics, aggregate metrics, the decision, configuration manifest, and private prediction rows.**
- [ ] **Step 3: Run the test and confirm the runner/artifact writer is absent.**
- [ ] **Step 4: Implement baseline predictions, provider calls for `tabfm_temporal` and `tabfm_weather`, aggregate computation, atomic JSON/CSV writes, and dashboard fixture creation.**
- [ ] **Step 5: Run both TabFM test files and confirm pass.**
- [ ] **Step 6: Commit `feat: generate TabFM benchmark artifacts`.**

### Task 4: Isolated real TabFM environment

**Files:**
- Create: `experiments/tabfm/pyproject.toml`
- Create: `experiments/tabfm/README.md`
- Create: `experiments/tabfm/run_experiment.py`
- Create: `experiments/tabfm/src/shamba_tabfm/__init__.py`
- Create: `experiments/tabfm/src/shamba_tabfm/provider.py`
- Create: `experiments/tabfm/tests/test_provider_contract.py`

**Interfaces:**
- Consumes: `BenchmarkRow`, `PredictionProvider`, private panel CSV, existing weather cache, and TabFM PyTorch checkpoint.
- Produces: `TabFMPredictionProvider`, CLI arguments `--panel`, `--weather-cache`, `--output-root`, `--device`, and generated artifacts.

- [ ] **Step 1: Write a provider-contract test that injects a fake `TabFMRegressor` class and verifies DataFrame columns, alphabetical county encoding, `max_num_rows=None`, `n_estimators=16`, `batch_size=1`, and seed 42.**
- [ ] **Step 2: Run the isolated test with the root environment and confirm the provider module is missing.**
- [ ] **Step 3: Implement lazy imports, checkpoint loading, temporal/weather DataFrame conversion, finite prediction validation, and actionable dependency/weight errors.**
- [ ] **Step 4: Add the pinned Git source and PyTorch extra to the isolated pyproject without modifying the root environment.**
- [ ] **Step 5: Implement the CLI by reusing `load_panel_examples`, `fetch_open_meteo_features`, and `run_tabfm_benchmark`.**
- [ ] **Step 6: Run provider contract tests without downloading weights and confirm pass.**
- [ ] **Step 7: Commit `feat: add isolated TabFM runner`.**

### Task 5: Optional FastAPI evidence endpoint

**Files:**
- Modify: `src/shamba_signal/api/app.py`
- Create: `tests/test_tabfm_api.py`

**Interfaces:**
- Consumes: generated `dashboard_fixture.json`.
- Produces: `GET /api/v1/tabfm-evaluation` and optional `tabfm_fixture_path` argument on `create_app`.

- [ ] **Step 1: Write failing tests for HTTP 503 when absent, HTTP 200 when valid, and HTTP 503 for invalid schema/version.**
- [ ] **Step 2: Run `pytest tests/test_tabfm_api.py -q` and confirm the route returns 404.**
- [ ] **Step 3: Add the optional path and route using a small shared JSON-object loader while preserving existing evaluation behavior.**
- [ ] **Step 4: Run `tests/test_tabfm_api.py tests/test_home.py` and confirm pass.**
- [ ] **Step 5: Commit `feat: serve optional TabFM evidence`.**

### Task 6: Foundation Model dashboard section

**Files:**
- Modify: `src/shamba_signal/web/index.html`
- Modify: `src/shamba_signal/web/static/app.js`
- Modify: `src/shamba_signal/web/static/styles.css`
- Modify: `tests/test_home.py`

**Interfaces:**
- Consumes: optional `GET /api/v1/tabfm-evaluation` payload.
- Produces: `renderTabfmStudy(payload)`, `renderTabfmModelComparison(models)`, `renderTabfmFoldChart(folds)`, and a non-blocking unavailable state.

- [ ] **Step 1: Add failing shell/script/style assertions for `#tabfm`, the exploratory badge, optional endpoint fetch, render functions, rolling fold chart, licence note, and responsive cards.**
- [ ] **Step 2: Run `pytest tests/test_home.py -q` and confirm failure.**
- [ ] **Step 3: Add the navigation link and semantic section while keeping the original Overview and Models copy unchanged.**
- [ ] **Step 4: Extend `loadDashboard` so the TabFM request is optional: original evaluation failure remains fatal, TabFM failure only renders a local-generation message.**
- [ ] **Step 5: Render pooled MAE cards, temporal versus weather delta, fold bars/lines, decision copy, configuration, 2023 post-hoc label, and non-commercial checkpoint note from the fixture.**
- [ ] **Step 6: Add Natural & Earthy responsive styles and accessible SVG/table fallbacks.**
- [ ] **Step 7: Run focused tests and confirm pass.**
- [ ] **Step 8: Commit `feat: add TabFM evidence dashboard`.**

### Task 7: Documentation and commands

**Files:**
- Modify: `Makefile`
- Modify: `README.md`
- Create: `docs/modelling/tabfm-temporal-benchmark.md`

**Interfaces:**
- Produces: `make tabfm-test`, `make tabfm-run TABFM_PANEL=... TABFM_WEATHER_CACHE=...`, setup and interpretation documentation.

- [ ] **Step 1: Add a failing repository-contract test or validation assertion for the two Make targets and research-extension documentation.**
- [ ] **Step 2: Run the focused validation and confirm failure.**
- [ ] **Step 3: Add commands that invoke the isolated project and never alter normal `make verify`.**
- [ ] **Step 4: Document the rolling protocol, licence, expected private artifacts, post-hoc 2023 caveat, and how a future untouched year would strengthen the claim.**
- [ ] **Step 5: Keep the README's original result first; add a separate optional research-extension section with no fabricated scores.**
- [ ] **Step 6: Run tests/validation and confirm pass.**
- [ ] **Step 7: Commit `docs: document TabFM research extension`.**

### Task 8: Verification, review, and pull request

**Files:**
- Review all branch changes.

**Interfaces:**
- Produces: verified feature branch and pull request to `main`.

- [ ] **Step 1: Run `python -m compileall -q src experiments/tabfm scripts`.**
- [ ] **Step 2: Run all root tests and Ruff checks available in the execution environment.**
- [ ] **Step 3: Run isolated provider contract tests without weights.**
- [ ] **Step 4: Confirm importing `shamba_signal.api.app` does not import `tabfm`, `torch`, or `pandas`.**
- [ ] **Step 5: Compare the branch with `main` for source-derived data, weights, accidental dependency changes, and altered original-result claims.**
- [ ] **Step 6: Open a pull request containing implementation summary, test evidence, the real-checkpoint command, and the explicit note that scores are not yet claimed until weights/private inputs are run.**
