# Shamba Signal

**A real-data maize yield research demo for Kenya**

Shamba Signal investigates whether official county-year maize data and weather features can support
a useful predictive model—and presents the answer honestly in a researcher-facing dashboard.

This is a personal portfolio project demonstrating official-data reconciliation, leakage-resistant
machine learning, scientific go/no-go judgement, and product delivery. It is not an operational
forecasting service.

## Result: an honest weather no-go

The private modelling panel contains 564 county-year rows across all 47 Kenya counties for
2012-2023, with 563 usable labels. The frozen split is 2012-2021 train, 2022 validation, and
provisional 2023 test.

| Provisional-2023 model | MAE t/ha | RMSE t/ha |
| --- | ---: | ---: |
| County historical mean | **0.2998** | **0.3982** |
| Weather Ridge | 0.3370 | 0.4537 |
| Ridge, alpha 100 | 0.3615 | 0.4783 |
| Previous year | 0.4651 | 0.6057 |

One small, reproducible ERA5 weather feature set improved the temporal Ridge baseline but did **not**
beat the county historical mean. The model selection used 2022; provisional 2023 was evaluated once.
That makes the result a scientifically useful no-go, not an invitation to keep model-shopping.

The local dashboard turns this result into an evidence journey: national model comparison, county
history, county-level provisional-2023 predictions/errors, feature definitions, lineage, and the
limitations that govern interpretation.

## Dashboard

![Shamba Signal desktop evidence overview](docs/assets/weather-evidence-dashboard/desktop-overview.png)

The committed overview contains aggregate evidence only. The private local fixture unlocks the
interactive 47-county history and prediction view without redistributing source-derived rows.

## Current boundary

- Output grain is county x year for maize; this is a retrospective end-of-year backtest.
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

With the approved private panel mounted, build the local fixture and then run the app:

```bash
uv run python scripts/run_weather_experiment.py \
  --panel /path/to/modelling_panel.csv \
  --weather-cache data/raw/open-meteo-era5-batch-v1 \
  --output-root data/processed/weather-experiment-v1
make run
```

Open `http://127.0.0.1:8000`. Raw weather responses, the panel, predictions, and the generated
fixture are intentionally ignored by Git while redistribution permission remains unresolved.

## Method in brief

1. Reconcile official county-level annual maize labels into a 47-county, 2012–2023 private panel.
2. Freeze 2012–2021 for training, 2022 for model selection, and provisional 2023 for the final test.
3. Compare transparent temporal references with one Ridge family using four annual
   [Open-Meteo ERA5](https://open-meteo.com/en/docs/historical-weather-api) features.
4. Present the national and county-level evidence, including the no-go, in the local dashboard.

This is not a mid-season operational forecast, farm measurement, causal analysis, or advisory tool.

## CV-ready summary

Built a reproducible Kenya maize county-year retrospective ML study from difficult official sources:
reconciled a 47-county 2012–2023 panel, enforced leakage-safe temporal splits, tested ERA5 weather
features against transparent baselines, published an honest no-go when the county historical mean
remained best, and delivered the evidence in a FastAPI dashboard.

## Start here

- [Remote execution handoff](REMOTE_EXECUTION.md)
- [Current PRD](docs/product/PRD.md)
- [MVP definition](docs/product/MVP.md)
- [Completion slices](docs/roadmap/IMPLEMENTATION_SLICES.md)
- [Modelling panel](docs/data/county-year-modelling-panel.md)
- [Baseline result](docs/modelling/temporal-baseline-result.md)
- [Weather feature value test](docs/modelling/weather-feature-value-test.md)
- [Architecture boundary](docs/architecture/ARCHITECTURE.md)

The completion scope is deliberately closed. No further infrastructure, sources, or model families
are planned for this portfolio release.
