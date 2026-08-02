# Shamba Signal

**County-year maize-label research infrastructure for Kenya**

Shamba Signal is building a research-grade decision-intelligence workflow for a narrow question:
can reconciled official county-year data for one feasibility-selected crop support a baseline-feasibility decision?

## Current implementation state

**Implemented through Slice 1:**

- approved PRD, MVP, architecture, scientific boundaries, and implementation slices;
- a FastAPI application shell with `/`, `/healthz`, `/openapi.json`, and
  `/api/v1/platform/status`;
- a public foundation page that reports implemented, next, and planned capabilities;
- a candidate source catalogue, repository validator, tests, and hardened CI definition;
- a versioned evidence register, four crop profiles, and all 47 county profiles;
- deterministic feasibility scoring and sensitivity analysis under the approved
  `35/20/15/10/10/10` weights;
- generated scorecard, machine-readable selection, and canonical decision record.

**Current metadata-level selection:** maize is the MVP crop, Busia is the deep-dive county, and
Trans Nzoia is the fallback. This is a Slice 2 acquisition hypothesis, not proof of label
completeness, satellite usability, or model skill.

**Current Slice 2 checkpoint:** Slice 2A is complete: an original KNBS/NIPFN workbook is accepted
and preserved outside Git with SHA-256 lineage. Its verified tidy sheet has 1,128 observations: all
47 counties × three indicators × eight annual years (2012-2018 and 2020). A local-only package
produces 376 county-year rows and confirms Busia under the explicit annual-data policy. It is
source-bound, private, and not model-ready. Slice 2B is next: reconcile conflicting official 2020
vintages, extend the annual panel, and assess county-year baseline feasibility. No season labels,
forecast, decision support, or resolved source precedence is claimed. See
[`docs/data/slice-2-acquisition-status.md`](docs/data/slice-2-acquisition-status.md).

**Not implemented:** a county-season target, trained model, calibrated forecast, stress
attribution, research dashboard, advisory engine, scheduler, AWS deployment, or Druid benchmark.
The annual local-only target is not a redistribution approval and must not be inferred as a model.

## Resolution boundary

- **Future validated output:** county × crop × season yield forecast, only where evidence gates pass.
- **Possible explanatory output:** relative yield potential and crop-stress indicators.
- **Never implied:** measured ward yield or farm-level yield prediction without matching labels.

## Reproducible local setup

Python 3.12 and uv 0.10.x are required.

```bash
uv sync --locked --extra dev
make verify
make feasibility
make run
```

`make feasibility` regenerates:

- `data/feasibility/scorecard.csv`
- `data/feasibility/selection.json`
- `docs/data/pilot-selection-decision.md`

Open `http://127.0.0.1:8000`. The platform contract is available at
`http://127.0.0.1:8000/api/v1/platform/status`.

## Repository map

- `src/shamba_signal/` — implemented application, feasibility, and domain code.
- `tests/` — behavioral, OpenAPI, deterministic-artifact, validator, and contract tests.
- `data/catalog/` — candidate source metadata; no raw restricted datasets.
- `data/feasibility/` — metadata-level evidence inputs and generated selection artifacts.
- `docs/product/` — PRD and MVP definition.
- `docs/architecture/` — logical local architecture and deferred AWS mapping.
- `docs/roadmap/` — testable implementation slices and no-go outcomes.
- `docs/data/` — source discovery, access, licensing evidence, and pilot decision record.
- `.github/` — read-only CI and contribution workflow.

See [the pilot decision](docs/data/pilot-selection-decision.md),
[the PRD](docs/product/PRD.md), [architecture](docs/architecture/ARCHITECTURE.md), and
[implementation slices](docs/roadmap/IMPLEMENTATION_SLICES.md).
