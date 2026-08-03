# Shamba Signal Memory

| Date | Area | Decision and current truth |
| --- | --- | --- |
| 2026-08-02 | Slice 2 delivery | Deliver one official-source vertical slice before any model, satellite, AWS, or Druid work. The first accepted source determines the only adapter implemented in this phase. |
| 2026-08-02 | Target grain | Preserve annual records as county x maize x year. County-season is evidence-insufficient; no crop calendar may disaggregate annual totals. |
| 2026-08-02 | Pilot selection | The historical Slice 1 scorecard selected Busia with Trans Nzoia as fallback. Slice 2A confirms Busia for accepted annual-label validation; Slice 2B reconciliation remains required before county-year baseline feasibility. |
| 2026-08-02 | Source policy | Slice 2B reconciles the accepted NIPFN workbook with the private KNBS annual-report candidate. KilimoSTAT and Food Systems Dashboard are off the critical path because no current verified response contract is accessible. Preserve accepted source bytes outside Git where redistribution is unclear. |
| 2026-08-02 | KNBS/NIPFN snapshot | Accepted the manually downloaded original XLSX under private storage, SHA-256 `15a47b6fdc634fab7a69cd7576974d2f9eeb550218389d4a1526dd8123a92ab8`. The verified table is annual (2012-2018 and 2020), not seasonal; 2019 is absent. |
| 2026-08-02 | Annual pilot gate | Local-only build has 376 county-year rows from 1,128 observations. Busia passes the eight-period annual gate; this does not authorize forecasting, season mapping, or source redistribution. |
| 2026-08-02 | Slice 2A/2B split | Slice 2A is the completed, private source-bound annual snapshot. Slice 2B must reconcile conflicting official annual vintages and extend the county-year panel before baseline-feasibility modelling. County-season is evidence-insufficient; annual totals must not be crop-calendar disaggregated. |
| 2026-08-02 | Release boundary correction | The public/repository contract ends at Slice 2B and only plans a county-year baseline feasibility/no-go study. Forecast, crop-stress, advisory, and season-label work are out of scope. |
| 2026-08-02 | Visual proof | Desktop and narrow-mobile browser checks show the Slice 2A ready / Slice 2B next boundary without console errors. The previous acquisition-blocked screenshot is retained only under a historical filename. |
| 2026-08-02 | Feasibility artifact reproducibility | The feasibility generator writes JSON and Markdown with explicit LF newlines on Windows. Its canonical report is a historical Slice 1 selection artifact carrying the current Slice 2A/2B boundary. |
| 2026-08-02 | Acquisition review follow-up | A direct CSV source may parse an explicitly accepted `application/octet-stream` payload as CSV, but still fails its schema gate. Manual verified fields are only for supplied download-manager payloads: they are rejected before network acquisition without `--input-file`, for any non-download-manager source, and by the validation layer itself. |
| 2026-08-02 | Publication receipt | PR #14 is merged to `main` at `755e70a`. Issue #3 owns Slice 2A, issue #16 owns Slice 2B reconciliation, and issue #4 owns the county-year baseline study. GitHub Actions still fails before any job step under issue #12. |
| 2026-08-02 | Slice 2B modelling panel | The verified KNBS report annex supplies 235 rows for 2019-2023. The active private panel uses the NIPFN workbook for 2012-2018 and the report for 2019-2023, preserving the superseded 2020 vintage separately. Result: 564 rows, 563 usable labels, 47 counties, train 2012-2021, validation 2022, provisional test 2023. Slice 3 temporal baselines are now unblocked. |
| 2026-08-02 | Slice 3 temporal baseline | Actual modelling is complete on the private panel. Ridge alpha 100 beats previous-year MAE on provisional 2023 (0.3615 vs 0.4651 t/ha) but loses to county historical mean (0.2998). Same-year production and area are excluded as leakage. The evidence-backed next slice is one weather-feature value test with 0.2998 MAE as the threshold. |

## Current Slice 2 state

- Branch: `slice/2-target-dataset` is published to draft PR #14; check live GitHub state before merging.
- The accepted KNBS workbook is byte-preserved outside Git. A standard-library XLSX reader binds the annual target to the accepted manifest digest and fails on source/schema drift.
- The local-only package contains `target.csv`, quality report, pilot decision, provenance manifest, and dataset card. It must not be committed while source redistribution remains review-required.
- The Slice 2A annual snapshot is ready but explicitly source-bound and not model-ready. Slice 2B is the annual-source reconciliation gate; no county-season mapping or forecast model exists.
- Public status release `slice-2a-annual-snapshot-v1` exposes the ready Slice 2A package, the next conflicting-2020-vintage reconciliation gate, and only planned county-year baseline feasibility.
- `refresh_modes` is intentionally empty: scheduled and analyst-triggered operations are unavailable.
- Private modelling package: `derived/county-year-maize-modelling-v1` under the adjacent private snapshot root. It contains the fixed panel, 2020 comparison, manifest, and dataset card; source-derived rows remain outside Git.
- Private baseline package: `derived/temporal-baselines-v1`. `results.json` SHA-256 is `a0635e793f68631a2a39dcfc6a6f5e55a554dacfe3dba219ce8cc6d876d6c579`; `predictions.csv` SHA-256 is `b12615c74b7923833e1acfe87a5da265c33c63aa6e30703a953a963fa5d190d7`.

## 2026-08-02 baseline reproducibility repair

- Regenerated `uv.lock` with the available `uv 0.7.8`; dependency pins did not change, but the lock metadata now matches the resolver and `uv sync --locked --extra dev` succeeds.
- Added the repository root to Pytest's import path so tests importing `scripts.*` work on Windows.
- Applied Python 3.12-safe Ruff modernization and corrected lockfile tests to validate the current UV extra-dependency format rather than an invalid manual Pytest-to-Pygments edge.
- Enforced LF for deterministic feasibility artifacts through `.gitattributes`; the generated scorecard is byte-stable on this worktree.
- Local verification uses `uv run pytest -q --basetemp .pytest-tmp` because the shared Windows temp root is denied. The current split and visual-proof checkpoint passes 170 tests, followed by lint, repository and Slice 2 validators, compilation, API smoke, and desktop/mobile browser checks.

# Remote execution reset and completion contract (2026-08-03)

- The project is now explicitly a finishable personal/CV research demo, not an enterprise
  foundation. `docs/product/PRD.md` is the current completion contract.
- The scientific claim is narrowed to a Kenya maize county-year retrospective backtest and
  evidence dashboard. Annual labels do not support mid-season, seasonal, farm, causal, or advisory
  claims.
- Completed evidence on `main`: a private 564-row 2012-2023 panel (563 usable) and leakage-safe
  temporal baselines. On provisional 2023, county historical mean remains best at 0.2998 t/ha MAE;
  ridge is 0.3615 and previous-year is 0.4651.
- The only remaining ML work is one bounded weather-feature value test against the 0.2998 benchmark.
  Whether it wins or produces a no-go, implementation then moves directly to a real-data dashboard
  and portfolio closeout.
- `REMOTE_EXECUTION.md` is the canonical next-agent handoff. It includes motivations, private
  artifact hashes/access limits, execution order, anti-overengineering rules, and definition of
  done.
- Source workbooks, reports, row-level panel, and predictions remain outside Git while
  redistribution permission is unresolved. The root workbook filename is ignored to prevent an
  accidental public commit.
- GitHub Actions issue #12 is an external account/billing pre-run blocker. Do not debug CI; use
  focused local verification and user-visible browser proof.
- Do not add infrastructure, validators, registries, governance, source hunts, speculative models,
  or further planning slices. Complete weather experiment, dashboard, README/screenshots, then stop.

## 2026-08-03 completion receipt

- The supplied private modelling panel and KNBS report matched their approved SHA-256 hashes.
- The bounded Open-Meteo ERA5 weather experiment selected Ridge alpha 10 on 2022. On provisional
  2023, Weather Ridge MAE is 0.3370 t/ha (RMSE 0.4537): better than temporal Ridge (0.3615), but
  not county historical mean (0.2998). The project records a no-go and stops modelling.
- `scripts/run_weather_experiment.py` caches the single raw weather response outside Git and writes
  local features, metrics, predictions, and dashboard fixture under ignored paths.
- The status homepage was replaced by the evidence dashboard. README, method note, and AWS
  portability diagram now describe the completed county-year retrospective study.
