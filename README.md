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

## Foundation release

This repository currently contains the approved product specification, architecture,
MVP contract, implementation slices, data-source registry, CI rules, and a runnable
FastAPI web/API shell. The next slice selects the crop and pilot county through a
reproducible data-feasibility scorecard.

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

- `src/shamba_signal/` — application and domain code.
- `tests/` — behavioral and repository-contract tests.
- `data/catalog/` — source metadata and selection rules, never raw datasets.
- `docs/product/` — PRD and MVP definition.
- `docs/architecture/` — working and AWS target architectures.
- `docs/roadmap/` — testable implementation slices.
- `docs/data/` — data discovery and licensing evidence.
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
