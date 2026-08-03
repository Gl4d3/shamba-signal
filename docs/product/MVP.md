# Shamba Signal MVP

## One sentence

A polished local research dashboard that uses real official county-year maize data to show whether
one weather-informed model improves on transparent temporal baselines for Kenya.

## What is already real

- A reconciled private modelling panel with 564 county-year rows across all 47 counties for
  2012-2023; 563 labels are usable.
- Frozen splits: 2012-2021 train, 2022 validation, provisional 2023 test.
- Leakage-safe previous-year, county-mean, and ridge baselines.
- Provisional-2023 county-mean benchmark: 0.2998 t/ha MAE and 0.3982 t/ha RMSE.
- Ridge improves on previous year but does not beat county mean.

## Delivered

1. One reproducible Open-Meteo ERA5 county-year weather feature table, cached outside Git.
2. One weather-informed Ridge experiment against the frozen split: a transparent no-go.
3. A private generated evaluation fixture serving a real-data evidence dashboard.
4. A desktop/mobile responsive dashboard implementation with national comparison, county history,
   provisional 2023 prediction/error, feature definitions, lineage, and limitations.
5. Portfolio README, method note, exact local commands, and concise unimplemented AWS mapping.

## Acceptance

- The weather experiment does not inspect 2023 during selection and is compared directly with
  0.2998 t/ha MAE.
- Failure to beat the benchmark is presented as a valid result, not hidden by more model search.
- The UI shows national metrics, model comparison, county history, county-level 2023 prediction
  and error, feature definitions, lineage summary, and limitations using real artifacts.
- Nothing suggests that annual county labels validate mid-season, seasonal, ward, pixel, farm,
  causal, or advisory claims.
- A fresh contributor with access to the approved private snapshots can reproduce the pipeline and
  run the app with documented commands.

## Stop list

Do not add more source registries, validators, abstraction layers, cloud resources, databases,
workers, queues, schedulers, governance processes, advisory features, or speculative models. The
remaining MVP is an ML experiment plus a user-visible product, not another foundation phase.
