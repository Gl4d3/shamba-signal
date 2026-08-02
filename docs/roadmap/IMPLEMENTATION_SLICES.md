# Shamba Signal Implementation Slices

A slice is a testable end-to-end product or research outcome. Infrastructure setup belongs inside the slice whose outcome needs it; it is not a standalone achievement. Roadmap completion reflects merged artifacts, not open-PR claims.

## Foundation — Product and repository contract

**Status:** complete on `main`.

**Outcome:** a contributor can run a web/API shell and understand exactly what the product currently implements and does not claim.

**Artifacts:** PRD, MVP, architecture, source register, repo scaffold, locked dependencies, hardened CI, issue templates, platform-status API, public foundation page, tests, and backlog issues.

**Acceptance:** locked install contract is current; `make verify` passes when package infrastructure is available; `/`, `/healthz`, static assets, OpenAPI, and `/api/v1/platform/status` respond; repository validation passes. The external GitHub Actions pre-run blocker remains tracked separately in #12.

## Slice 1 — Metadata-level data feasibility and provisional pilot selection

**Status:** complete. The selected pair was provisional pending Slice 2 annual-label evidence.

**Outcome:** one crop and deep-dive county are provisionally ranked from documented metadata and expert-judgement scores, with limitations and tested sensitivity scenarios disclosed.

**Decision:** maize + Busia, with Trans Nzoia as fallback.

**Artifacts:** evidence register, four-crop and 47-county profiles, scorecard, sensitivity scenarios, source/licence notes, generated canonical decision record, and machine-readable selection.

**Acceptance:** the generation command writes canonical paths, is byte-stable, matches committed artifacts, regenerates scores from registered weights/evidence, and clearly transfers downloaded-record validation to Slice 2.

## Slice 2A — Source-bound annual snapshot

**Status:** complete locally. The accepted NIPFN workbook is private, source-bound, and not model-ready.

**Outcome:** a deterministic annual county-year maize snapshot package validates the accepted workbook without publishing source-derived rows.

**Acceptance:** accepted-workbook SHA-256 lineage, deterministic private build, documented annual coverage and gaps, and an annual-label pilot result. It makes no season, forecast, or decision-support claim.

## Slice 2B — Official annual label reconciliation and forecast readiness

**Status:** next. No modelling work begins before conflicting official annual vintages are reconciled and the annual panel is extended.

**Outcome:** reconcile source vintages, establish evidence-backed source precedence, and decide whether county-year baseline feasibility is supportable. County-season is an evidence-insufficiency result.

**Acceptance:** private source audit, reconciliation policy, annual-panel extension, terms review, and a documented modelling go/no-go. No crop calendar may disaggregate annual totals.

## Out-of-scope history

Earlier planning mentioned forecasting, crop-stress, and advisory work. They are not current
release capabilities or promised slices. The only post-Slice-2B consideration is a county-year
baseline feasibility/no-go study, if its reconciliation gate closes.
