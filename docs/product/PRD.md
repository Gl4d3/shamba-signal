# Product Requirements Document — Shamba Signal

**Status:** Approved programme; foundation implementation only  
**Product direction:** Modular decision-intelligence platform  
**Primary geography:** Kenya  
**Validated output grain:** County × crop × season

## 1. Product statement

Shamba Signal is intended to become a research-grade agricultural decision-intelligence platform that produces defensible mid-season county-level crop-yield forecasts for Kenya, exposes uncertainty and evidence quality, explains non-causal environmental signals associated with each supported estimate, and may later surface response options from approved expert playbooks.

The foundation implements product and scientific contracts, a FastAPI shell, public status page, source catalogue, repository validation, tests, a lockfile, and a hardened CI definition. It does **not** contain a downloaded target dataset, trained model, calibrated forecast, research dashboard, scheduler, advisory engine, AWS deployment, or Druid benchmark.

## 2. Central research question

Can publicly obtainable county-season data for the **feasibility-selected crop** support a defensible mid-season forecast that either:

1. beats mandatory naïve baselines under frozen geographic and temporal holdouts; or
2. produces a documented insufficiency/no-go result and abstains from unsupported forecasting?

Metadata-level feasibility may identify a provisional crop and county. Downloaded records must confirm or replace that choice before modelling.

## 3. Users

### Primary user

Agricultural researchers and programme analysts who need reproducible data, model evidence, uncertainty, lineage, held-out evaluation, exports, and backtest controls.

### Secondary users

County extension leadership, food-security teams, and programme managers may use the same evidence to prioritise verification and preparedness. Farmer-facing and field-prescription workflows are deferred.

## 4. Product principles

1. **Evidence before prediction.** A forecast without lineage and uncertainty is incomplete.
2. **Baselines before complexity.** Deep models follow transparent baselines and a precise improvement hypothesis.
3. **Resolution honesty.** County labels cannot validate ward- or farm-level yield.
4. **Data selects the pilot.** Crop, county, and historical window emerge from evidence.
5. **No-go is valid.** Insufficient evidence causes abstention, not a manufactured success claim.
6. **Advisory by permission.** AI may contextualise approved playbooks; it may not invent interventions.
7. **Working slices before cloud migration.** AWS and Druid follow a functioning local data-to-forecast loop.
8. **Merged reality governs status.** Public wording distinguishes designed, implemented, tested, merged, deployed, and verified-with-real-data states.

## 5. Scope

### Geography and resolution

- Kenya-wide outputs only for counties that pass evidence gates.
- One deep-dive county selected by data quality and coverage.
- Missing counties remain absent, degraded, or abstained; they are not smoothed into a complete map.
- Ward and pixel layers may show relative yield potential or crop-stress indicators, never measured local yield without matching labels.

### Crop and timing

- One crop is selected through feasibility and confirmed with downloaded records.
- The MVP forecast point is mid-season.
- County-specific calendars are preferred; a documented national or agro-ecological fallback is allowed.
- Every run records the calendar source, forecast cutoff, and fallback decision.

## 6. Functional requirements

### FR-01 — Feasibility and provisional selection

Profile candidate labels and explanatory sources, publish the scoring evidence and limitations, and clearly distinguish measured metadata, documented evidence, and expert judgement. Stability is claimed only for the registered sensitivity scenarios.

### FR-02 — Source registry and immutable snapshots

For each applicable source and snapshot, record:

- source ID, publisher, and dataset title;
- landing URL and exact acquisition URL or request parameters;
- access method, source version, and retrieval timestamp;
- spatial and temporal coverage;
- HTTP/content metadata, media type, and byte size;
- content checksum and schema fingerprint;
- licence or terms evidence, decision, and redistribution status;
- a portable logical or content-addressed storage identifier;
- transformation code revision.

Adapters must validate status, redirects, content type, payload shape, and expected schema; reject HTML/login/bot/error documents; use bounded timeouts; preserve original bytes before transformation; and never store credentials, cookies, bearer tokens, signed URLs, or developer-machine absolute paths in canonical manifests.

Access permission and redistribution permission are separate decisions. Restricted or unresolved bytes are not committed merely because they can be downloaded.

### FR-03 — Canonical county-season target table

The typed target record contains stable county identifiers, source-provided and canonical names, crop code, year or season, calendar source, element, original and normalised values/units, production, harvested area, reported yield, derived yield, source flag, derivation method, quality class, and snapshot ID.

Reported and derived yield remain separate. Derived yield may be calculated only when:

- harvested area is strictly greater than zero;
- production and area refer to the same county, crop, and period;
- units are compatible and conversions are recorded;
- the source and derivation method are retained;
- reconciliation tolerance is explicit.

Derived yield never silently replaces reported yield.

### FR-04 — Feature and cutoff contract

Feature generation may use climate, vegetation, moisture, soil, terrain, calendar, and historical-lag inputs only when they were available by the configured forecast cutoff. Every feature table records source snapshot IDs and transformation revision.

### FR-05 — Mandatory baseline models

The first modelling slice implements:

- historical county mean;
- previous-season value;
- simple linear or regularised regression;
- one tree-based model.

A temporal neural model is considered only after the baseline slice is complete and a precise improvement hypothesis exists.

### FR-06 — Evaluation and leakage controls

- Geographic and temporal folds are defined before training.
- Random-row splits are debugging-only.
- Hyperparameter selection does not inspect final holdouts.
- Headline metrics are MAE, RMSE, prediction-interval coverage, and interval width.
- Errors are reported by county, season/year, and evidence-quality class.
- Results are compared against historical mean and previous-season baselines.
- Correlation, SHAP, and feature importance are not described as causal evidence.

### FR-07 — Forecast contract

Each supported forecast records point estimate, prediction interval, historical baseline, anomaly, evidence quality, forecast cutoff, calendar, source/feature/model lineage, and run identifier. Unsupported cases expose an abstention or insufficient-evidence state.

### FR-08 — Minimal evidence UI

The first useful interface is built only after a real versioned forecast fixture exists. It shows county outlook, selected-county history, actual versus predicted values, prediction interval, evidence quality, cutoff, lineage, and visible abstention. It does not interpolate missing counties or invent sample forecasts.

### FR-09 — Deferred advisory and operations

Guardrailed advisory, scheduled operations, AWS, SageMaker, Druid, multi-crop support, and farmer-facing interfaces remain deferred until the target dataset and baseline research gates pass. Advisory output, when implemented, may select only approved playbook actions and may not provide farm-specific dosage, irrigation quantity, pesticide, fertiliser, or treatment prescriptions.

## 7. Non-functional requirements

- **Reproducibility:** locked dependencies, checksummed inputs, deterministic configuration, and byte- or value-stable generated artifacts.
- **Auditability:** snapshot-to-target-to-forecast lineage and immutable run metadata.
- **Portability:** logical storage identifiers and contracts that map from local execution to S3/RDS later.
- **Security:** no secrets, environment files, restricted source data, signed URLs, or machine-specific artifacts in Git.
- **Accessibility:** keyboard-operable UI and non-colour-only status communication.
- **Truthfulness:** no model-performance, deployment, or service-maturity claim without corresponding evidence.

## 8. Success and no-go criteria

A baseline slice is accepted when either:

1. a model beats historical mean and previous-season baselines under the approved geographic and temporal holdouts while meeting documented interval-coverage requirements; or
2. the slice publishes a reproducible insufficiency/no-go report, identifies the failed evidence or performance gates, and abstains from unsupported forecasting.

A successful product demonstration must let a researcher reproduce the selected dataset and evaluation, trace every displayed value to its source and model artifact, and see uncertainty, evidence quality, and abstention states.

## 9. Delivery sequence

1. Merge and verify the product foundation.
2. Complete metadata-level feasibility and provisional selection.
3. Acquire and quality-check real target records, producing a canonical dataset or rigorous insufficiency result.
4. Build mandatory baseline models and publish success or no-go evidence.
5. Build the minimal evidence UI from a real versioned fixture.
6. Consider remote-sensing sequence models only after a precise baseline-improvement hypothesis.
7. Defer full dashboard work, advisory, scheduling, AWS, and Druid until the central data-to-forecast loop is proven.
