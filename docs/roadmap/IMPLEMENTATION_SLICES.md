# Shamba Signal Implementation Slices

A slice is a testable end-to-end product or research outcome. Infrastructure setup belongs inside the slice whose outcome needs it; it is not a standalone achievement. Roadmap completion reflects merged artifacts, not open-PR claims.

## Foundation — Product and repository contract

**Outcome:** a contributor can run a web/API shell and understand exactly what the product currently implements and does not claim.

**Artifacts:** PRD, MVP, architecture, source register, repo scaffold, locked dependencies, hardened CI, issue templates, platform-status API, public foundation page, tests, and backlog issues.

**Acceptance:** locked install contract is current; `make verify` passes; `/`, `/healthz`, static assets, OpenAPI, and `/api/v1/platform/status` respond; repository validation passes.

## Slice 1 — Metadata-level data feasibility and provisional pilot selection

**Outcome:** one crop and deep-dive county are provisionally ranked from documented metadata and expert-judgement scores, with limitations and tested sensitivity scenarios disclosed.

**Artifacts:** evidence register, four-crop and 47-county profiles, scorecard, sensitivity scenarios, source/licence notes, and provisional selection record.

**Acceptance:** the generation command writes canonical paths, is byte-stable, leaves a clean Git diff, regenerates scores from registered weights/evidence, and clearly transfers downloaded-record validation to Slice 2.

## Slice 2 — Reproducible county-season target dataset

**Outcome:** official production, harvested area, and yield evidence becomes a versioned modelling table, or the slice publishes a rigorous evidence-insufficiency result.

**Artifacts:** immutable snapshots or protected references, manifests, canonical schema, unit and county mappings, Parquet/CSV target data, data dictionary, dataset card, quality report, and Busia-confirm or fallback decision.

**Acceptance:** unique county/crop/season keys; deterministic rebuild; schema-drift failure; licence-aware publication; missingness and continuity profiles; reported-versus-derived reconciliation; positive-area and unit checks; snapshot-to-output lineage.

## Slice 3 — Defensible baseline yield model

**Outcome:** answer whether public data supports a useful mid-season forecast.

**Artifacts:** frozen cutoff and feature contracts, historical mean and previous-season baselines, regularised regression, one tree model, geographic and temporal evaluation, prediction intervals, error analysis, model card, and real forecast fixture.

**Acceptance:** no post-cutoff leakage; MAE, RMSE, interval coverage, and width are reported; the model beats mandatory naïve baselines under frozen holdouts **or** the slice publishes a documented no-go/insufficiency result and abstains.

## Slice 4 — Minimal evidence UI

**Outcome:** a user can inspect the actual baseline fixture without a notebook.

**Artifacts:** county outlook, selected-county deep dive, actual-versus-predicted history, interval, evidence quality, cutoff, lineage, and visible abstention state.

**Acceptance:** every displayed value reconciles with the fixture/API; missing counties are not fabricated; relative indicators are not labelled measured yield.

## Deferred programme slices

The following remain valid long-term work but are deferred until the target dataset and baseline are complete:

- Remote-sensing temporal model.
- Rich stress attribution.
- Full national dashboard.
- Guardrailed advisory.
- Scheduled operations and forecast versioning.
- AWS portability exercise.
- Druid proof with one concrete benchmark.

A negative benchmark or decision to reject a technology is an acceptable outcome.
