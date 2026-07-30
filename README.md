# Shamba Signal

**Crop Yield Intelligence with Stress Attribution for Kenya**

Shamba Signal is a research-grade decision-intelligence platform for mid-season,
county-level crop-yield forecasting. It combines official agricultural statistics,
satellite observations, climate histories, soils, and crop calendars to estimate yield,
quantify uncertainty, explain stress signals, and surface approved response options.

The project is deliberately honest about resolution:

- **Validated output:** county-season yield forecast.
- **Explanatory spatial output:** relative yield potential and crop-stress indicators.
- **Not claimed:** measured ward yield or farm-level yield prediction without matching labels.

## Current product decision

Slice 1 now provides a reproducible data-feasibility pipeline covering four crop candidates
and all 47 Kenyan counties. Under the approved 35/20/15/10/10/10 score contract it selects:

- **MVP crop:** maize — 91.25/100
- **Deep-dive county:** Busia — 85.75/100
- **Fallback county:** Trans Nzoia — 80.75/100

The choice remains stable under labels-heavy, spatial-heavy, and governance-heavy sensitivity
scenarios. It is still conditional on Slice 2 downloading the official records and measuring
county-year completeness, units, flags, and satellite observation availability.

Run the selection pipeline with:

```bash
make feasibility
```

See [`docs/data/pilot-selection-decision.md`](docs/data/pilot-selection-decision.md) for the
decision and [`data/feasibility/`](data/feasibility/) for the evidence, profiles, scorecard,
and machine-readable selection.

## Foundation release

The repository contains the approved product specification, architecture, MVP contract,
implementation slices, source registry, CI rules, and a runnable FastAPI web/API shell.
The next implementation slice builds the reproducible maize county-season target dataset
and verifies whether Busia passes the snapshot-level evidence gates.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
make verify
make run
```

Open `http://127.0.0.1:8000` and inspect the API contract at
`http://127.0.0.1:8000/api/v1/platform/status`.

## Repository map

- `src/shamba_signal/` — application, domain, and feasibility code.
- `tests/` — behavioral and repository-contract tests.
- `data/catalog/` — source metadata and selection rules, never raw datasets.
- `data/feasibility/` — evidence register, 47-county profiles, scorecard, and selection.
- `docs/product/` — PRD and MVP definition.
- `docs/architecture/` — working and AWS target architectures.
- `docs/roadmap/` — testable implementation slices.
- `docs/data/` — data discovery, licensing evidence, and pilot decision.
- `.github/` — CI, issue forms, and contribution workflow.

## Engineering rules

1. Every slice ends in a demonstrable, testable artifact.
2. Classical baselines are mandatory before deep-learning models.
3. Spatial and temporal holdouts replace random-row validation.
4. Forecasts always include uncertainty and data-quality context.
5. AI advisory output is constrained to approved playbooks.
6. AWS is introduced after working product slices, with local interfaces designed for migration.

See [the PRD](docs/product/PRD.md), [architecture](docs/architecture/ARCHITECTURE.md),
and [implementation slices](docs/roadmap/IMPLEMENTATION_SLICES.md).
