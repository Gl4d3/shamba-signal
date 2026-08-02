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
| 2026-08-02 | Feasibility artifact reproducibility | The feasibility generator writes JSON and Markdown with explicit LF newlines on Windows. Its canonical report is a historical Slice 1 selection artifact carrying the current Slice 2A/2B boundary. |

## Current Slice 2 state

- Branch: `slice/2-target-dataset` contains local Slice 2 implementation commits; check live Git state before publishing.
- The accepted KNBS workbook is byte-preserved outside Git. A standard-library XLSX reader binds the annual target to the accepted manifest digest and fails on source/schema drift.
- The local-only package contains `target.csv`, quality report, pilot decision, provenance manifest, and dataset card. It must not be committed while source redistribution remains review-required.
- The Slice 2A annual snapshot is ready but explicitly source-bound and not model-ready. Slice 2B is the annual-source reconciliation gate; no county-season mapping or forecast model exists.
- Public status release `slice-2a-annual-snapshot-v1` exposes the ready Slice 2A package, the next conflicting-2020-vintage reconciliation gate, and only planned county-year baseline feasibility.
- `refresh_modes` is intentionally empty: scheduled and analyst-triggered operations are unavailable.

## 2026-08-02 baseline reproducibility repair

- Regenerated `uv.lock` with the available `uv 0.7.8`; dependency pins did not change, but the lock metadata now matches the resolver and `uv sync --locked --extra dev` succeeds.
- Added the repository root to Pytest's import path so tests importing `scripts.*` work on Windows.
- Applied Python 3.12-safe Ruff modernization and corrected lockfile tests to validate the current UV extra-dependency format rather than an invalid manual Pytest-to-Pygments edge.
- Enforced LF for deterministic feasibility artifacts through `.gitattributes`; the generated scorecard is byte-stable on this worktree.
- Local verification used `uv run pytest -q --basetemp .pytest-tmp` because the shared Windows temp root is denied. The command passed 129 tests, followed by lint, repository and Slice 2 validators, compilation, and API smoke.
