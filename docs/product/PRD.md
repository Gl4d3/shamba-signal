# Shamba Signal Product Requirements Document

**Status:** Current completion contract

**Product:** A local, evidence-backed maize yield research demo for Kenya

**Release grain:** County x year, not county x season or farm

## 1. Why this project exists

Shamba Signal is a personal portfolio project that bridges production Python/data engineering
experience into digital-agriculture research. It should demonstrate that the owner can:

- turn difficult official data into a reproducible modelling dataset;
- make honest scientific decisions about leakage, holdouts, uncertainty, and no-go results;
- implement and evaluate a useful machine-learning experiment;
- translate model evidence into a polished, understandable product; and
- explain how the local design could map to cloud services without building an unnecessary
  cloud platform.

It is not an enterprise foundation, a national operational service, or an excuse to accumulate
infrastructure. The end goal does not justify more scaffolding.

## 2. Product statement

Shamba Signal lets a researcher inspect Kenya county-level maize yield history, compare simple
temporal baselines with one weather-informed model, and understand where the evidence supports
or fails to support a predictive claim.

The product is complete even if weather features do not beat the strongest naive baseline,
provided the result is reproducible, visible in the UI, and reported honestly.

## 3. Evidence boundary

The available official labels are annual county aggregates. Therefore this release is a
county-year retrospective backtest and evidence explorer. It must not be described as:

- a mid-season operational forecast;
- measured ward-, pixel-, or farm-level yield;
- agronomic advice or a farmer decision system;
- a causal explanation of yield; or
- a deployed national service.

The current test year, 2023, is provisional in the source report. That limitation must remain
visible wherever results are presented.

## 4. Primary user and journey

The primary user is an agricultural researcher or programme analyst evaluating whether the
available public evidence supports a useful county-level model.

The finished local UI must let the user:

1. see the national 2023 backtest summary and the winning model;
2. compare model MAE/RMSE against county historical mean and previous year;
3. select a county and inspect historical actuals plus the 2023 prediction/error;
4. see which weather features were tested and whether they added value;
5. understand data coverage, provisional-label status, leakage exclusions, and limitations; and
6. export or inspect the displayed evaluation data without encountering invented values.

## 5. Functional requirements

### FR-01 — Reproducible real-data pipeline

Given the approved private source snapshots, documented commands rebuild the county-year panel,
weather feature table, evaluation outputs, and versioned UI fixture. Source-derived row-level data
remains outside Git while redistribution permission is unresolved.

### FR-02 — One bounded weather experiment

Use one accessible, documented weather source and a small defensible feature set. Keep the frozen
split: 2012-2021 train, 2022 model selection, provisional 2023 final test. Same-year production and
harvested area remain excluded because yield is derived from them.

The weather-informed model is retained only if its provisional-2023 MAE beats the county historical
mean benchmark of 0.2998 t/ha. If it does not, publish the no-go result and stop adding models.

### FR-03 — Honest evaluation artifact

Publish MAE and RMSE for every compared model, county-level errors, feature definitions, split
definitions, and a concise limitations statement. Do not use random-row splits, tune on 2023, or
describe correlation or feature importance as causation.

### FR-04 — Minimal evidence dashboard

Replace the foundation/status-only page with a polished local research dashboard driven entirely
by a generated, versioned evaluation fixture. The UI must clearly distinguish actual, predicted,
baseline, unavailable, and provisional values. It must work on desktop and mobile and include an
honest no-go state if no model beats the naive benchmark.

### FR-05 — Portfolio closeout

The README must tell the completed problem/data/method/result/product story, include verified UI
screenshots, provide reproducible local commands, and state the evidence boundaries. One concise
architecture diagram may show how the proven local workflow maps to AWS; no AWS deployment is
required.

## 6. Quality requirements

- The core data and metric calculations have focused regression tests.
- A clean local happy path produces the real evaluation artifact and launches the UI.
- The final UI is verified in a real browser at desktop and mobile widths.
- No secrets, source-restricted bytes, private paths, or fabricated data enter Git.
- Documentation and the UI use the same metrics and capability claims.

Repository-wide test expansion, additional validators, service decomposition, observability,
scheduling, deployment automation, and governance work are not quality requirements for this
personal project.

## 7. Definition of done

Shamba Signal is finished when all of the following are true:

- the existing official maize panel and one weather feature set produce a frozen-split result;
- the weather model either beats 0.2998 t/ha MAE or yields an explicit, reproducible no-go;
- a researcher can explore the real evaluation in the local dashboard;
- the dashboard has browser-verified desktop and mobile evidence;
- the README presents the final result and exact limitations as a CV/portfolio case study; and
- all completion changes are merged and pushed to `main`.

## 8. Explicit non-goals

- More source discovery after one usable weather source is found.
- County-season reconstruction from annual labels.
- Satellite imagery, CNNs, LSTMs, transformers, feature stores, or MLOps platforms.
- Advisory playbooks, recommendations, chatbots, scheduling, queues, or microservices.
- PostgreSQL, Druid, SageMaker, AWS deployment, production monitoring, or enterprise governance.
- Multi-crop expansion, farmer-facing workflows, or farm-level claims.
- CI repair while GitHub Actions remains blocked before job execution by the repository account.

Any future idea outside this contract belongs in a short “future possibilities” note, not in the
implementation path for completing the project.
