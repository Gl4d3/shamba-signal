# Product Requirements Document — Shamba Signal

**Status:** Approved for implementation  
**Release:** Foundation and MVP programme  
**Product direction:** Modular decision-intelligence platform  
**Primary geography:** Kenya  
**Primary validated unit:** County × crop × season

## 1. Executive summary

Shamba Signal is a research-grade agricultural decision-intelligence platform that produces
mid-season county-level crop-yield forecasts for Kenya, explains environmental signals behind
each estimate, and surfaces evidence-linked response options from approved agricultural playbooks.

The product is designed around scientific defensibility. Official yield statistics are the target
labels; remote sensing, climate, soils, and crop calendars are explanatory inputs. County-season
forecasts are validated outputs. Finer-resolution maps are explicitly labelled relative yield
potential or crop-stress indicators until matching field or ward labels become available.

## 2. Problem

Agricultural production information is fragmented across statistical portals, satellite catalogues,
climate archives, soil products, and local calendars. Researchers can assemble these sources in
notebooks, but operational users need a repeatable system that answers:

1. What yield is expected at mid-season?
2. How uncertain is the estimate?
3. How does it compare with normal conditions?
4. What evidence drove the estimate?
5. Which areas merit investigation or preparedness?
6. Which approved response options are relevant to that evidence?

## 3. Users

### 3.1 Primary persona — agricultural researcher or programme analyst

Needs reproducible data, model evidence, comparison across counties/seasons, uncertainty,
lineage, exports, and the ability to trigger backtests or scenario runs.

### 3.2 Secondary personas

- County extension leadership prioritising verification and field sampling.
- Food-security teams preparing monitoring and response capacity.
- Programme managers comparing geographic risk and evidence quality.

### 3.3 Deferred personas

Field extension officers and farmers may receive tailored interfaces later. The MVP does not
attempt a direct-to-farmer advisory service.

## 4. Product principles

1. **Evidence before prediction.** A forecast without lineage and uncertainty is incomplete.
2. **Baselines before complexity.** Deep models must beat transparent historical and tabular baselines.
3. **Resolution honesty.** County labels cannot validate farm-level output.
4. **Data selects the pilot.** The crop, county, and historical window emerge from feasibility scoring.
5. **Advisory by permission.** AI contextualises approved playbooks; it does not invent interventions.
6. **Working product before cloud migration.** AWS architecture is documented early and implemented after core slices work.
7. **Every slice flies.** Each implementation slice ends in a testable research or user outcome.

## 5. Scope

### 5.1 Geography

- Kenya-wide outlook for counties with sufficient evidence.
- One deep-dive county selected by data quality and coverage, not preference.

### 5.2 Crop

- One crop selected through the feasibility scorecard.
- Architecture and contracts remain crop-agnostic.

### 5.3 Forecast timing

- MVP forecast point: mid-season.
- Historical post-season evaluation is mandatory.
- Progressive early/mid/late estimates are deferred until calibration proves safe.

### 5.4 Crop calendars

- County-specific calendars where authoritative sources exist.
- Documented national or agro-ecological fallback otherwise.
- Every run records the calendar source and fallback decision.

## 6. Core user journey

1. Select crop and season.
2. View the national county outlook.
3. Identify abnormal yield forecasts or low-confidence counties.
4. Open a county deep dive.
5. Inspect estimate, prediction interval, historical comparison, and data completeness.
6. Review rainfall, vegetation, temperature, moisture, soil, and calendar evidence.
7. Inspect model drivers and comparable historical seasons.
8. Review approved operational response options.
9. Export evidence or trigger a backtest/scenario run.

## 7. Functional requirements

### FR-01 Data feasibility

The system shall profile candidate crop labels and explanatory datasets, score crop/county
combinations, and publish the selection evidence. The score weights are: yield-label quality 35%,
historical depth 20%, spatial resolution 15%, satellite usability 10%, licensing 10%, access stability 10%.

### FR-02 Source registry and lineage

Each source shall record publisher, URL, version, access method, spatial and temporal coverage,
license state, retrieval time, checksum, and transformation lineage.

### FR-03 County-season target table

The pipeline shall normalise harvested area, production, and yield into a county × crop × season
contract with units, source flags, missingness, and reproducible derivation rules.

### FR-04 Feature generation

The pipeline shall generate season-aware climate, vegetation, moisture, soil, terrain, and historical
lag features using only information available by the configured forecast cutoff date.

### FR-05 Baseline models

The evaluation shall include historical county mean, previous-season value, linear/regularised
regression, and a tree-based model before any temporal neural model is accepted.

### FR-06 Validation

The system shall evaluate leave-one-county/group-out and leave-one-season/year-out performance.
Random-row validation may be used only for debugging and must not support a headline claim.

### FR-07 Forecast output

Each output shall contain point estimate, prediction interval, anomaly, confidence, data quality,
forecast cutoff, feature snapshot, model version, calendar source, and run identifier.

### FR-08 Stress attribution

The system shall explain rainfall deficits, delayed onset, dry spells, vegetation underperformance,
heat stress, soil-moisture anomaly, and evidence gaps without representing correlation as causation.

### FR-09 Risk flags

Flags shall be one of: normal monitoring, watch, elevated concern, or critical review. Thresholds
shall be versioned and auditable.

### FR-10 Guardrailed advisory

Approved expert playbooks define all selectable actions. AI may select and explain an action in
context but may not create new action content, dosage, treatment, or farm-specific prescriptions.
Low confidence or inadequate crop-stage evidence shall suppress advisory output.

### FR-11 Refresh modes

The platform shall support scheduled national refreshes and analyst-triggered backtests/scenario runs.
Every output shall be versioned and comparable with prior runs.

### FR-12 Research dashboard

The public application shall expose national outlook, county analysis, model evidence, data explorer,
and advisory review without requiring a notebook.

### FR-13 Exports

Researchers shall be able to export forecast tables, evaluation summaries, lineage manifests, and
map-compatible data while respecting source licensing restrictions.

## 8. Analytical requirements

### 8.1 Target

Reported yield in tonnes per hectare where reliable, otherwise production divided by harvested area
with explicit derivation and unit conversion metadata.

### 8.2 Candidate predictors

- cumulative and anomaly rainfall;
- onset, cessation, and dry-spell features;
- growing-degree days and heat-stress days;
- NDVI/EVI/NDWI temporal summaries and integrals;
- soil moisture and evapotranspiration where viable;
- SoilGrids properties and uncertainty;
- elevation and agro-ecological context;
- lagged official yields and production area;
- crop calendar and forecast-cutoff position.

### 8.3 Model progression

1. Historical and previous-season baselines.
2. Transparent tabular regression and tree models.
3. Small temporal CNN or equivalent sequence model.
4. Ensemble only when held-out evidence justifies it.

### 8.4 Metrics

MAE and RMSE are mandatory. Normalised or percentage metrics may supplement them when zero and
low-yield cases are handled explicitly. Prediction-interval coverage and interval width are mandatory.
Results shall be segmented by county, year/season, rainfall regime, crop, and label-quality class.

## 9. Non-functional requirements

- **Reproducibility:** deterministic configuration, pinned dependencies, checksummed inputs, versioned outputs.
- **Auditability:** forecast-to-source lineage and immutable run metadata.
- **Portability:** local filesystem/object-store and PostgreSQL interfaces map cleanly to S3 and RDS.
- **Reliability:** failed scheduled runs retain the previous published forecast and expose failure status.
- **Security:** no credentials in Git; least-privilege service identities; secrets through environment providers.
- **Observability:** structured logs, run metrics, data-quality metrics, model metrics, and traceable run IDs.
- **Accessibility:** keyboard-operable UI, meaningful focus states, text alternatives, and non-colour-only statuses.
- **Performance:** national outlook loads from materialised forecast outputs rather than recomputing models per request.

## 10. Success measures

### Research success

- Beats historical mean and previous-season baselines on spatial and temporal holdouts.
- Prediction intervals achieve the documented coverage target without becoming operationally useless.
- Error analysis identifies where and why the model should abstain.

### Product success

- A researcher can reproduce the selected dataset and model evaluation from the repository.
- Every displayed forecast can be traced to source snapshots and model version.
- The national outlook and county deep dive are usable from a public deployment.
- Advisory output never escapes the approved action vocabulary.

### Portfolio success

- Public repository, live preview, architecture documentation, reproducible experiments, data/model cards,
  evaluation evidence, issue history, and an AWS migration design with one completed portability slice.

## 11. Risks and controls

| Risk | Control |
|---|---|
| Sparse or inconsistent yield labels | Feasibility gate, source flags, crop/county selection, abstention |
| Leakage from future-season data | Cutoff-aware feature contracts and temporal tests |
| Spatial autocorrelation inflates performance | Geographic holdouts and regional group validation |
| Cloud cover damages optical signals | observation-count features, compositing, Sentinel-1 option later |
| Crop masks are stale or unlicensed | licence gate, alternate masks, sensitivity analysis |
| Advisory sounds authoritative despite weak evidence | approved playbooks, confidence gates, human review |
| Infrastructure consumes the project | AWS work follows functioning model/product slices |

## 12. Release structure

The implementation is split into the testable slices defined in
`docs/roadmap/IMPLEMENTATION_SLICES.md`. Foundation establishes contracts and a runnable shell;
Slice 1 selects the evidence; later slices build target data, models, explanations, product screens,
operational refreshes, and finally cloud portability.
