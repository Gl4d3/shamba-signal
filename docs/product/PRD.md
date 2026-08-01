# Product Requirements Document — Shamba Signal

**Status:** Approved programme; foundation implementation only
**Release:** Foundation and MVP programme
**Product direction:** Modular decision-intelligence platform
**Primary geography:** Kenya
**Primary validated unit:** County × crop × season

## 1. Executive summary

Shamba Signal is intended to become a research-grade agricultural decision-intelligence platform that produces mid-season county-level crop-yield forecasts for Kenya, explains environmental signals behind each supported estimate, and surfaces evidence-linked response options from approved agricultural playbooks.

The current foundation does **not** contain a downloaded target dataset, trained model, calibrated forecast, research dashboard, scheduler, advisory engine, or cloud deployment. It establishes the product and scientific contracts, a FastAPI shell, source catalogue, validation, tests, and delivery workflow needed to investigate whether the proposed forecasting product is viable.

Official yield statistics are candidate target labels; remote sensing, climate, soils, and crop calendars are candidate explanatory inputs. County-season forecasts may become validated outputs only after the data, baseline, and evaluation gates pass. Finer-resolution maps remain relative yield-potential or crop-stress indicators until matching field or ward labels exist.

## 2. Central research question

Can publicly obtainable maize county-season data support a defensible mid-season forecast that either:

1. beats mandatory naïve baselines under frozen geographic and temporal holdouts; or
2. produces a documented insufficiency/no-go result and abstains from unsupported forecasting?

## 3. Users

### Primary persona — agricultural researcher or programme analyst

Needs reproducible data, model evidence, comparison across counties and seasons, uncertainty, lineage, exports, and backtest or scenario-run controls.

### Secondary personas

- County extension leadership prioritising verification and field sampling.
- Food-security teams preparing monitoring and response capacity.
- Programme managers comparing geographic risk and evidence quality.

### Deferred personas

Field extension officers and farmers may receive tailored interfaces later. The MVP does not attempt a direct-to-farmer advisory service.

## 4. Product principles

1. **Evidence before prediction.** A forecast without lineage and uncertainty is incomplete.
2. **Baselines before complexity.** Deep models are considered only after transparent baselines and a precise improvement hypothesis.
3. **Resolution honesty.** County labels cannot validate farm- or ward-level output.
4. **Data selects the pilot.** The crop, county, and historical window emerge from feasibility evidence.
5. **No-go is a valid result.** Insufficient evidence must cause abstention, not a manufactured success claim.
6. **Advisory by permission.** AI contextualises approved playbooks; it does not invent interventions.
7. **Working product before cloud migration.** AWS architecture is documented early and implemented after core slices work.
8. **Every slice flies.** Each implementation slice ends in a testable research or user outcome.

## 5. Scope

### Geography

- Kenya-wide outlook only for counties that pass evidence gates.
- One deep-dive county selected by data quality and coverage, not preference.
- Missing counties remain missing, degraded, or abstained; they are not smoothed into a complete map.

### Crop

- One crop selected through the feasibility scorecard and confirmed by downloaded records.
- Architecture and contracts remain crop-agnostic.

### Forecast timing

- MVP forecast point: mid-season.
- Historical post-season evaluation is mandatory.
- Progressive early/mid/late estimates are deferred until calibration proves safe.

### Crop calendars

- County-specific calendars where authoritative sources exist.
- Documented national or agro-ecological fallback otherwise.
- Every run records the calendar source and fallback decision.

## 6. Functional requirements

### FR-01 Data feasibility

Profile candidate labels and explanatory datasets, score crop/county combinations, and publish the evidence and limitations. Metadata-level scoring is provisional until downloaded records confirm continuity, units, flags, missingness, and feature overlap.

### FR-02 Source registry and snapshot lineage

For each applicable source and snapshot, record source ID and publisher; dataset title and landing URL; exact acquisition URL or request parameters; access method and source version; retrieval timestamp; spatial and temporal coverage; media type and byte size; content checksum and schema fingerprint; licence or terms evidence and decision; redistribution status; portable logical storage location; and transformation code revision.

Access permission and redistribution permission are separate decisions. Restricted or unresolved bytes are never committed merely because they can be downloaded.

### FR-03 County-season target table

Normalise production, harvested area, and yield into a county × crop × season contract while preserving original values, units, source names, flags, and snapshot lineage.

Reported yield and derived yield remain distinct. Derived yield may be calculated only when harvested area is strictly greater than zero and production and area share county, crop, period, and compatible units. Every conversion, tolerance, source, and derivation method must be recorded. Derived yield never silently replaces reported yield.

### FR-04 Feature generation

Generate season-aware climate, vegetation, moisture, soil, terrain, and historical-lag features using only information available by the configured forecast cutoff.

### FR-05 Baseline models

Evaluate historical county mean, previous-season value, linear or regularised regression, and one tree-based model before any temporal neural model is considered.

### FR-06 Validation

Define folds before training. Use geographic and temporal holdouts for headline claims. Random-row validation is allowed only for debugging. Hyperparameter selection must not inspect final holdouts.

### FR-07 Forecast output

Each supported output contains point estimate, prediction interval, anomaly, evidence quality, forecast cutoff, feature snapshot, model version, calendar source, and run identifier. Unsupported cases expose an abstention or insufficient-evidence state.

### FR-08 Stress attribution

Potential future explanations may cover rainfall deficits, delayed onset, dry spells, vegetation underperformance, heat, soil moisture, and evidence gaps. Correlation, SHAP, or feature importance must not be described as causal evidence.

### FR-09 Guardrailed advisory

Deferred until forecast evidence and confidence rules exist. Approved expert playbooks define all selectable actions. AI may contextualise an allowed action but may not create dosage, treatment, irrigation quantity, pesticide, fertiliser, or farm-specific prescriptions.

### FR-10 Refresh modes

Scheduled national refreshes and analyst-triggered research runs are planned, not implemented. Failed future runs must retain the previous valid publication.

## 7. Analytical requirements

### Target

Prefer trustworthy reported yield in tonnes per hectare. A separate derived yield may be calculated only under the strict matching and positive-area rules in FR-03.

### Candidate predictors

- cumulative and anomaly rainfall;
- onset, cessation, and dry-spell features;
- growing-degree days and heat-stress days;
- vegetation-index temporal summaries;
- soil moisture and evapotranspiration where viable;
- soil properties and uncertainty;
- elevation and agro-ecological context;
- lagged official yields and production area;
- crop calendar and forecast-cutoff position.

### Model progression

1. Historical and previous-season baselines.
2. Transparent tabular regression and tree models.
3. Sequence model only after a precise, testable improvement hypothesis.
4. Ensemble only when held-out evidence justifies it.

### Metrics

MAE and RMSE are mandatory. Prediction-interval coverage and interval width are mandatory. Results are segmented by county, season or year, and evidence-quality class. “Accuracy” is not used as the headline regression metric.

## 8. Non-functional requirements

- **Reproducibility:** locked dependencies, checksummed inputs, deterministic configuration, byte- or value-stable generated outputs.
- **Auditability:** forecast-to-source lineage and immutable run metadata.
- **Portability:** local logical storage and PostgreSQL interfaces map cleanly to S3 and RDS later.
- **Security:** no credentials or environment files in Git; no tokens, cookies, bearer headers, signed URLs, or machine-specific absolute paths in canonical manifests.
- **Accessibility:** keyboard-operable UI, meaningful focus states, and non-colour-only statuses.
- **Truthfulness:** public copy separates implemented, active, planned, tested, merged, deployed, and verified-with-real-data states.

## 9. Success and no-go criteria

A baseline slice is accepted when either a model beats historical mean and previous-season baselines under the approved geographic and temporal holdouts while meeting documented interval-coverage requirements, or the slice publishes a reproducible insufficiency/no-go report, identifies the failed evidence or performance gates, and abstains from unsupported forecasting.

A researcher must be able to reproduce the selected dataset and evaluation, trace every displayed value to its source and model artifact, and see uncertainty, evidence quality, and abstention states.

## 10. Risks and controls

| Risk | Control |
|---|---|
| Sparse or inconsistent yield labels | Feasibility gate, source flags, quality classes, abstention |
| Leakage from future data | Cutoff-aware feature contracts and leakage tests |
| Spatial autocorrelation inflates performance | Geographic holdouts |
| Cherry-picked split or metric | Folds and metrics frozen before training |
| Crop masks are stale or unlicensed | Licence gate, alternatives, explicit limitations |
| Advisory sounds authoritative | Deferred implementation, approved playbooks, human review |
| Infrastructure consumes the project | Dataset and baseline before AWS, Druid, or distributed services |

## 11. Release sequence

Foundation establishes truthful contracts and a runnable shell. Slice 1 performs provisional metadata-level feasibility. Slice 2 must acquire and quality-check real target records. Slice 3 answers the baseline research question. A minimal evidence UI follows a real versioned forecast fixture. Remote-sensing complexity, full dashboard work, advisory, scheduling, AWS, and Druid remain deferred until those gates pass.
