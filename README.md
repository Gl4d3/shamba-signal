# Shamba Signal

**A real-data maize yield research demo for Kenya**

Shamba Signal investigates whether official county-year maize data and weather features can support
a useful predictive model—and presents the answer honestly in a researcher-facing dashboard.

This is a personal portfolio project demonstrating official-data reconciliation, leakage-resistant
machine learning, scientific go/no-go judgement, and product delivery. It is not an operational
forecasting service.

## Current evidence

The private modelling panel contains 564 county-year rows across all 47 Kenya counties for
2012-2023, with 563 usable labels. The frozen split is 2012-2021 train, 2022 validation, and
provisional 2023 test.

| Provisional-2023 model | MAE t/ha | RMSE t/ha |
| --- | ---: | ---: |
| County historical mean | **0.2998** | **0.3982** |
| Ridge, alpha 100 | 0.3615 | 0.4783 |
| Previous year | 0.4651 | 0.6057 |

Target history alone does not beat the county historical mean. The remaining experiment adds one
bounded weather feature set; after that result, the project moves directly to the evidence UI and
portfolio closeout.

## Current boundary

- Output grain is county x year for maize.
- The 2023 source values are provisional.
- Annual labels do not validate mid-season, county-season, ward, pixel, farm, causal, or advisory
  claims.
- Official source bytes and row-level derived data remain private while redistribution terms are
  unresolved.
- AWS is a documented portability option only; no cloud deployment is claimed.

## Local setup

Python 3.12 and uv 0.10.x are required.

```bash
uv sync --locked --extra dev
make verify
make run
```

Open `http://127.0.0.1:8000` after starting the app. Private data build and modelling commands are
documented in the relevant data/model files and require the approved external snapshots.

## Start here

- [Remote execution handoff](REMOTE_EXECUTION.md)
- [Current PRD](docs/product/PRD.md)
- [MVP definition](docs/product/MVP.md)
- [Completion slices](docs/roadmap/IMPLEMENTATION_SLICES.md)
- [Modelling panel](docs/data/county-year-modelling-panel.md)
- [Baseline result](docs/modelling/temporal-baseline-result.md)
- [Architecture boundary](docs/architecture/ARCHITECTURE.md)

The remaining scope is deliberately small: one weather feature value test, one real-data evidence
dashboard, and portfolio closeout. No more foundation work is required.
