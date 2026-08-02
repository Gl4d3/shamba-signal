# County-year temporal baseline result

The first leakage-safe model experiment is complete on the private 2012-2023 panel.

## Design

- Train: 2012-2021.
- Model selection: 2022.
- Untouched test: provisional 2023.
- References: previous-year yield and county historical mean.
- Model: ridge regression using county identity, year trend, previous-year yield, and trailing-three-observation mean.
- Excluded as leakage: same-year production and harvested area, because report-period yield is their ratio.

## Result

| Model | 2022 MAE | Provisional-2023 MAE | Provisional-2023 RMSE |
| --- | ---: | ---: | ---: |
| County historical mean | 0.3936 | **0.2998** | **0.3982** |
| Previous year | 0.3571 | 0.4651 | 0.6057 |
| Ridge, alpha 100 | **0.3336** | 0.3615 | 0.4783 |

Ridge improves on the previous-year reference but does not beat the county
historical mean on provisional 2023. Target history alone is therefore not a
sufficient forecasting model. The next justified experiment is to add weather
features and require them to beat the 0.2998 t/ha county-mean MAE.

The largest county-mean test errors occur in Samburu, Kakamega, Machakos,
Nyandarua, and Baringo. The private predictions artifact retains all county-level
errors for follow-up; row-level source-derived values remain outside Git.
