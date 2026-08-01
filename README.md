# Shamba Signal

**Crop-yield research infrastructure for Kenya**

Shamba Signal is building a research-grade decision-intelligence workflow for a narrow question: can publicly obtainable county-season maize data support a defensible mid-season yield forecast under geographic and temporal holdouts?

## Current implementation state

**Implemented in the foundation:**

- approved PRD, MVP, architecture, scientific boundaries, and implementation slices;
- a FastAPI application shell with `/`, `/healthz`, `/openapi.json`, and `/api/v1/platform/status`;
- a public foundation page that reports implemented, next, and planned capabilities;
- a candidate source catalogue, repository validator, tests, and hardened CI definition.

**Not implemented:** a downloaded target dataset, trained model, calibrated forecast, stress attribution, research dashboard, advisory engine, scheduler, AWS deployment, or Druid benchmark. Those remain planned and must not be inferred from the logical architecture diagram.

## Resolution boundary

- **Future validated output:** county × crop × season yield forecast, only where evidence gates pass.
- **Possible explanatory output:** relative yield potential and crop-stress indicators.
- **Never implied:** measured ward yield or farm-level yield prediction without matching labels.

## Reproducible local setup

Python 3.12 and uv 0.10.x are required.

```bash
uv sync --locked --extra dev
make verify
make run
```

Open `http://127.0.0.1:8000`. The platform contract is available at `http://127.0.0.1:8000/api/v1/platform/status`.

## Repository map

- `src/shamba_signal/` — implemented application and domain code.
- `tests/` — behavioral, OpenAPI, validator, and repository-contract tests.
- `data/catalog/` — candidate source metadata; no raw restricted datasets.
- `docs/product/` — PRD and MVP definition.
- `docs/architecture/` — logical local architecture and deferred AWS mapping.
- `docs/roadmap/` — testable implementation slices and no-go outcomes.
- `docs/data/` — source discovery, access, and licensing evidence.
- `.github/` — read-only CI and contribution workflow.

See [the PRD](docs/product/PRD.md), [architecture](docs/architecture/ARCHITECTURE.md), and [implementation slices](docs/roadmap/IMPLEMENTATION_SLICES.md).
