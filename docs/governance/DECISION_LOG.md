# Decision Log

## ADR-001 — Modular decision-intelligence platform

**Decision:** build a modular monolith plus independent workers before considering microservices.  
**Reason:** preserve testable boundaries without building an airport before a working forecast exists.

## ADR-002 — County-season yield is the validated output

**Decision:** ward and pixel layers are relative yield potential and crop-stress indicators.  
**Reason:** public county labels cannot validate farm- or ward-level yield claims.

## ADR-003 — One crop selected by feasibility

**Decision:** do not hard-code maize; let label continuity, coverage, licensing, and satellite usability select the crop.  
**Reason:** a single defensible model is stronger than broad unsupported coverage.

## ADR-004 — Mid-season MVP forecast

**Decision:** start at mid-season, retain progressive early/mid/late forecasting as a later maturity step.  
**Reason:** mid-season is useful while reducing the false confidence risk of very early predictions.

## ADR-005 — Hybrid advisory governance

**Decision:** expert-authored playbooks control allowed actions; AI only selects and contextualises them.  
**Reason:** combine operational usefulness with a bounded and auditable action vocabulary.

## ADR-006 — Scheduled and analyst-triggered runs

**Decision:** support both modes with separate research and published-run semantics.  
**Reason:** scheduled refreshes serve operations; manual runs serve backtesting and investigation.

## ADR-007 — AWS follows working slices

**Decision:** document AWS interfaces now, migrate a completed slice later.  
**Reason:** demonstrate architecture knowledge without allowing cloud setup to replace the product.
