# Remote execution handoff — finish Shamba Signal

## Read this first

> **The end goal does not justify the means.** This project has already received several lifetimes
> of scaffolding, contracts, validators, governance, and architecture work. Do not add more
> foundation. Do not confuse tests, clean exits, CI, documentation volume, or infrastructure with
> product progress. From this point on, every slice must produce either a new ML result or a real
> user-visible capability.

Work directly from the current `main` branch and finish the current PRD. Do not reopen the product
design unless real implementation evidence makes a requirement impossible.

## Why the project exists

Shamba Signal is a personal portfolio project designed to bridge strong applied Python, AI, and
data-engineering experience into digital-agriculture research. Its value is the complete story:
acquiring difficult official evidence, reconciling it honestly, building a leakage-resistant ML
experiment, making a defensible go/no-go decision, and translating the result into a polished
research product.

It should demonstrate research judgement and product delivery, not pretend to be an enterprise
platform. AWS matters only as evidence that the owner understands a sensible migration path after
a local workflow exists. A concise architecture mapping is enough; do not deploy it.

## Authoritative reading order

1. `docs/product/PRD.md` — current completion contract.
2. `docs/product/MVP.md` — exact remaining MVP.
3. `docs/roadmap/IMPLEMENTATION_SLICES.md` — Slices 4-6 and then stop.
4. `docs/data/county-year-modelling-panel.md` — data grain and evidence boundary.
5. `docs/modelling/temporal-baseline-result.md` — benchmark to beat.
6. `memory.md` — implementation history and current receipt.

Older plans, historical architecture sections, closed issues, and prior conversations are context,
not the active scope when they conflict with the files above.

## Current repository truth

- Repository: `https://github.com/Gl4d3/shamba-signal`
- Branch: `main`
- Completed pull requests:
  - `#14` annual target package;
  - `#17` county-year modelling panel;
  - `#18` temporal baselines.
- There are no open pull requests at handoff time.
- GitHub Actions issue `#12` is an external account/billing pre-run failure. Runs have failed before
  executing steps. Do not spend project time debugging CI; use focused local verification.
- The last merged local verification passed 185 tests, Ruff, the repository validator, and the
  Slice 2 validator. That is sufficient foundation evidence.

## Scientific and data truth

- Target: maize yield in tonnes/hectare at county x year grain.
- Coverage: all 47 Kenya counties, 2012-2023.
- Panel: 564 rows; 563 usable.
- Frozen split: 2012-2021 train (470 rows), 2022 validation (47), provisional 2023 test (47).
- 2023 labels are provisional in the official source report.
- Same-year production and harvested area are excluded as predictors because yield is their ratio.
- Annual labels do not support county-season, mid-season, ward, pixel, farm, causal, or advisory
  claims.

Current provisional-2023 results:

| Model | MAE t/ha | RMSE t/ha |
| --- | ---: | ---: |
| County historical mean | **0.299836** | **0.398155** |
| Ridge, alpha 100 | 0.361491 | 0.478273 |
| Previous year | 0.465056 | 0.605742 |

Ridge beats previous year but not county mean. The next experiment must test whether weather adds
enough information to beat 0.2998 t/ha MAE. If it does not, record the negative result and move to
the UI; do not begin model shopping.

## Private artifacts and remote limitation

The official source bytes and row-level derived artifacts are intentionally outside Git while
redistribution permission remains unresolved. Do not weaken this boundary merely to make remote
execution convenient.

Expected private snapshot location in the original local environment:

`D:\proj-d\side-projects\shamba-signal-private-snapshots`

Important artifact checksums:

- NIPFN workbook:
  `15a47b6fdc634fab7a69cd7576974d2f9eeb550218389d4a1526dd8123a92ab8`
- KNBS 2024 report PDF:
  `7d86dc4cbfa1d0b5204e2428fb8d84c3bada0fc1775bf0b7d557dfebcc4d70eb`
- modelling panel:
  `a7328d34a4d97e31425e1a939ab689ff34d498cd38dd0d687b0092ad17affe60`
- baseline results:
  `a0635e793f68631a2a39dcfc6a6f5e55a554dacfe3dba219ce8cc6d876d6c579`
- baseline predictions:
  `b12615c74b7923833e1acfe87a5da265c33c63aa6e30703a953a963fa5d190d7`

The remote environment must receive these artifacts through an approved private mount/upload, or
rebuild them from the documented official sources. The public repository alone cannot contain
them. Do not substitute invented, reconstructed, or unofficial labels.

Official source entry points:

- NIPFN workbook landing page:
  `https://nipfn.knbs.or.ke/download/maize-production-by-county-2012-2020/`
- KNBS report PDF:
  `https://www.knbs.or.ke/wp-content/uploads/2025/01/National-Agriculture-Production-Report-2024.pdf`

## Execute this sequence

### 1. Weather feature value test

Use one accessible official or well-established weather source. Prefer the simplest source that can
provide reproducible county-level annual aggregates for 2012-2023. A small feature set such as
precipitation total/anomaly, wet-day count, dry-spell proxy, and mean/max temperature is enough.

- Cache raw responses outside Git and record source/version/retrieval metadata.
- Join features by stable county identifier and year.
- Preserve the frozen split and existing baselines.
- Try one sensible tabular model family, with selection on 2022 only.
- Produce versioned metrics and county-level prediction artifacts suitable for the UI.
- Beat 0.2998 MAE or publish a clear no-go. Then stop modelling.

Do not add satellite imagery, crop calendars, seasonal reconstruction, deep learning, hyperparameter
sweeps, feature stores, experiment platforms, or multiple competing data vendors.

### 2. Real-data evidence dashboard

Replace the status-only homepage with the smallest polished interface that completes the journey in
the PRD. Reuse FastAPI and the existing static frontend unless a concrete blocker proves they are
insufficient. Drive the UI from a generated, legally safe evaluation fixture; never hard-code fake
results.

Browser-check desktop and mobile. Fix visibly broken layout, hierarchy, labels, empty states, and
accessibility issues. The product should foreground the finding, not its plumbing.

### 3. Portfolio closeout

Rewrite the README around the completed evidence: problem, official data, reconciliation, modelling
decision, UI, limitations, and local reproduction. Add browser screenshots and one concise diagram
showing how the proven local components could map to AWS. Clearly label the cloud mapping as a
design option, not a deployment.

Suggested honest CV framing:

> Built Shamba Signal, a Kenya county-level maize-yield research demo that reconciles official
> 2012-2023 data, evaluates leakage-resistant temporal and weather baselines, and exposes real
> model evidence and limitations in an interactive dashboard.

Update the wording to the final measured result. Do not claim farm validation, operational
forecasting, remote-sensing CNN work, causal drivers, or deployed AWS infrastructure.

## Execution rules

- Progress is measured by ML artifacts and UI behavior, not scaffolding.
- Do not create new validators, registries, policies, abstraction layers, services, databases,
  queues, schedulers, CI systems, cloud resources, or governance documents.
- Do not search endlessly for more data. The only justified acquisition is one usable weather
  source; switch once if the first route fails, then make a bounded decision.
- Use a local happy-path run, focused calculation tests, and one core regression test. Add tests only
  when they protect behavior introduced in the slice.
- Do not loop on automated reviewers. Fix only comments that affect correctness, truthfulness,
  security, or the actual user experience.
- Make coherent commits, not micro-commit theatre. Merge important work promptly after local proof.
- Never publish restricted source bytes, secrets, developer paths, or unsupported claims.
- If weather adds no value, that is a result. Ship the no-go dashboard and finish the project.

## Definition of finished

The project is complete when the current PRD definition of done is met, all final changes are on
remote `main`, and a reviewer can see a real data-to-model-to-dashboard story without reading the
historical scaffolding. Do not invent a Slice 7.

## Suggested skills

- `test-driven-development` — only for the focused behavior being added, not blanket test growth.
- `agent-browser` — for final desktop/mobile exploratory UI verification.
- `release-visual-proof` — at the end of the dashboard slice for screenshots and claim verification.
- `ship-work-safely` — only at delivery boundaries for exact staging, commit, and remote checks.

Avoid invoking planning, architecture, audit, or multi-agent orchestration skills unless a concrete
blocker requires them. The plan already exists; execute it.
