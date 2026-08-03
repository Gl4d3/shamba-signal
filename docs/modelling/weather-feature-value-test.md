# County-year weather feature value test

## Decision

**No-go.** The Weather Ridge model improved on the temporal Ridge reference but did not beat the
county historical mean on the untouched provisional-2023 test. No further models, sources, or
feature work are justified by this experiment.

| Model | 2022 MAE t/ha | Provisional-2023 MAE t/ha | Provisional-2023 RMSE t/ha |
| --- | ---: | ---: | ---: |
| County historical mean | 0.3936 | **0.2998** | **0.3982** |
| Weather Ridge | **0.3053** | 0.3370 | 0.4537 |
| Temporal Ridge | 0.3336 | 0.3615 | 0.4783 |
| Previous year | 0.3571 | 0.4651 | 0.6057 |

Weather Ridge was selected from a small Ridge regularization grid using 2022 only (selected
alpha: 10). It never inspected 2023 labels during selection.

## Data and method

- Labels: the approved private 47-county maize panel, 2012–2023; 2023 is provisional.
- Split: 2012–2021 training, 2022 selection, 2023 one-time final test.
- Weather: [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api),
  fixed to ERA5 reanalysis and cached locally outside Git.
- Geographic proxy: one representative interior coordinate per county. This is coarse county-level
  reanalysis, not a farm, pixel, or station observation.
- Features: annual precipitation total, wet-day count (daily precipitation over 1 mm), annual mean
  2 m temperature, and annual maximum 2 m temperature, plus the existing leakage-safe temporal
  history features and county identity.
- Excluded as leakage: same-year production and harvested area, because yield is their ratio.

The weather values describe the completed label year. This is therefore a retrospective
end-of-year evidence test, not a usable mid-season forecast.

## Reproduce locally

The official panel and cached source responses remain private. With the approved panel available:

```bash
uv run python scripts/run_weather_experiment.py \
  --panel /path/to/modelling_panel.csv \
  --weather-cache data/raw/open-meteo-era5-batch-v1 \
  --output-root data/processed/weather-experiment-v1
```

The command writes private local outputs: cached raw response, annual weather features, predictions,
metrics, and `evaluation_fixture.json`. The local FastAPI dashboard serves that fixture; none of
those row-level artifacts are committed.

## Interpretation

The weather feature set adds measurable signal relative to the temporal Ridge baseline, but its
0.3370 t/ha MAE remains 0.0372 t/ha behind the county historical mean. The correct portfolio claim
is not that weather forecasting works; it is that a bounded, leakage-aware experiment produced an
honest no-go and made the evidence visible.

## Browser evidence

The generated private fixture was verified in the real dashboard at 1440 x 900 and 390 x 844.
County selection updated the displayed history and 2023 evidence without browser console errors.
Portfolio-safe overview screenshots are stored under
`docs/assets/weather-evidence-dashboard/`; full county-detail captures remain private because they
contain source-derived row values.
