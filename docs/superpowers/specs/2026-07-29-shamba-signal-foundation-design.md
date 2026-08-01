# Shamba Signal Foundation Design

## Purpose

Establish the complete product contract and a runnable foundation for a modular crop-yield decision-intelligence
platform. The foundation must prevent future implementation from drifting into unsupported farm-level claims,
disconnected notebooks, premature microservices, or AWS infrastructure without a working analytical outcome.

## Approved product

Shamba Signal produces mid-season county-season crop-yield forecasts for Kenya. One crop and one deep-dive county
are selected through a public-data feasibility scorecard. Crop-stress layers explain the forecast. Expert-authored
playbooks control operational response options, while AI may only contextualise allowed actions.

## Foundation deliverables

1. Product requirements document and MVP boundary.
2. Working and AWS target architecture.
3. Testable implementation slices and decision log.
4. Candidate public-data catalogue with explicit licence status.
5. Python package, FastAPI API, and public foundation page.
6. Stable health and platform-status contracts.
7. Repository validation, CI workflow, issue forms, and contribution templates.
8. GitHub backlog issues matching the implementation slices.

## Architecture

Use one Python distribution with clear domain, service, API, and web packages. The foundation web page is served by
FastAPI to provide a dependency-light, verifiable vertical slice. Later UI work may split into a dedicated web client
without changing forecast or platform contracts. Data and forecast workers remain conceptual deployable boundaries
until their slices implement real work.

## Error handling

The foundation API has no external dependencies and therefore returns deterministic contracts. Later source, pipeline,
and model failures follow the run-level policy in the architecture document: record failure, retain the prior publication,
and expose run-stage evidence rather than silently degrading.

## Testing

Behavioral tests cover health, product contract, and MVP boundary copy. Repository-contract tests ensure the PRD,
MVP, architecture, slices, source catalogue, CI, and issue forms cannot disappear unnoticed. Data-catalogue tests verify
selection weights, required sources, HTTPS access, and explicit licensing state.

## Acceptance

- `PYTHONPATH=src pytest -q` passes.
- `PYTHONPATH=src python scripts/validate_repo.py` passes.
- `python -m compileall -q src scripts` passes.
- `/healthz`, `/api/v1/platform/status`, and `/` pass behavioral tests.
- Foundation files are published to `Gl4d3/shamba-signal`.
- GitHub issues exist for Slices 1–9.
