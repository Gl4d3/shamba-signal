# Shamba Signal Implementation Slices

A slice is a testable end-to-end product or research outcome. Infrastructure setup belongs inside the
slice whose outcome needs it; it is not a standalone achievement.

## Foundation — Product and repository contract

**Outcome:** a contributor can run a web/API shell and understand exactly what the product will and will not claim.

**Artifacts:** PRD, MVP, architecture, AWS mapping, source register, repo scaffold, CI, issue templates,
platform-status API, public foundation page, tests, and backlog issues.

**Acceptance:** `make verify` passes; `/`, `/healthz`, and `/api/v1/platform/status` respond; repository-contract tests pass.

## Slice 1 — Data feasibility and pilot selection

**Outcome:** one crop, one deep-dive county, a historical window, and a target-label policy are selected by evidence.

**Artifacts:** source adapters for metadata/sample retrieval, profiling notebook/report, 47-county scorecard,
crop scorecard, licensing decisions, data dictionary, and a signed selection decision record.

**Acceptance:** another environment regenerates the scorecard; weights total 100; every selected source has a licence decision;
selection is stable under documented sensitivity checks.

## Slice 2 — Reproducible county-season target dataset

**Outcome:** official production, harvested area, and yield become a versioned modelling table.

**Artifacts:** raw snapshot manifests, canonical schemas, unit conversions, crop/calendar mapping, quality classes,
Parquet output, dataset card, and data-quality report.

**Acceptance:** target rows are unique by county/crop/season; derivations reconcile production and area within tolerance;
source flags and missingness are preserved; reruns from the same snapshots are byte- or value-equivalent.

## Slice 3 — Defensible baseline yield model

**Outcome:** a transparent mid-season benchmark predicts held-out county-season yield.

**Artifacts:** cutoff-aware feature table, historical mean and previous-season baselines, regularised regression,
tree-based model, spatial/temporal evaluation, error analysis, model card, and forecast fixture.

**Acceptance:** no post-cutoff feature leakage; metrics include MAE/RMSE and interval coverage; headline model beats simple baselines
or the slice explicitly concludes that available data is insufficient.

## Slice 4 — Remote-sensing temporal model

**Outcome:** a small temporal model tests whether seasonal sequences improve held-out performance.

**Artifacts:** Sentinel-2 compositing, observation-quality features, temporal tensors, small temporal CNN,
training/evaluation pipeline, comparison report, and retained or rejected architecture decision.

**Acceptance:** model is accepted only if it improves predetermined held-out criteria without materially worsening calibration;
otherwise the baseline remains the production model and the negative result is documented.

## Slice 5 — Uncertainty and stress attribution

**Outcome:** every forecast carries calibrated uncertainty and an evidence-based explanation.

**Artifacts:** interval-calibration method, confidence/data-quality classes, rainfall/heat/vegetation/moisture attribution,
similar-season retrieval, abstention rules, and explanation tests.

**Acceptance:** interval coverage is reported by geography/time; low-evidence cases abstain; explanations never claim causality;
all factors trace to feature values and source snapshots.

## Slice 6 — National outlook and county deep dive

**Outcome:** a public user can investigate forecasts without a notebook.

**Artifacts:** map-ready forecast API, national outlook, selected-county analysis, model evidence screen, data explorer,
responsive/accessibility checks, export endpoints, and deployed preview.

**Acceptance:** displayed values match published forecast fixtures; keyboard and mobile journeys work; map statuses are not colour-only;
all headline values expose lineage and uncertainty.

## Slice 7 — Guardrailed advisory

**Outcome:** forecasts link to approved operational response options without pretending to be a farm agronomist.

**Artifacts:** playbook schema, approved action catalogue, evidence-to-action rules, AI contextualisation adapter,
suppression gates, review UI, audit log, and adversarial tests.

**Acceptance:** generated text cannot introduce an action absent from the playbook; low confidence/stage mismatch suppresses advice;
chemical dosage, irrigation quantity, and farm-specific treatment are rejected.

## Slice 8 — Scheduled operations and forecast versioning

**Outcome:** national refreshes and analyst-triggered runs are reliable, comparable, and recoverable.

**Artifacts:** scheduler, queue/worker contract, run state machine, idempotency, retry policy, publication promotion,
run comparison, structured logs, operational dashboard, and failure drills.

**Acceptance:** a failed run leaves the prior published version active; duplicate requests are idempotent; run IDs connect logs,
source snapshots, features, model, forecasts, and advisory outputs.

## Slice 9 — AWS portability and Druid proof

**Outcome:** one completed product slice runs on AWS with equivalent contracts, and Druid proves or fails a concrete use case.

**Artifacts:** IaC, S3/RDS/container/job/queue deployment, IAM model, Secrets Manager, CloudWatch, cost notes,
local-to-AWS migration runbook, Druid ingestion/query benchmark, and architecture decision record.

**Acceptance:** the selected slice reproduces local forecast outputs within documented tolerance; least-privilege roles pass review;
Druid is retained only if a named analytical query or latency target materially benefits.
