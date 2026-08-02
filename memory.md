# Shamba Signal Memory

| Date | Area | Decision and current truth |
| --- | --- | --- |
| 2026-08-02 | Slice 2 delivery | Deliver one official-source vertical slice before any model, satellite, AWS, or Druid work. The first accepted source determines the only adapter implemented in this phase. |
| 2026-08-02 | Target grain | Preserve annual records as county x maize x year. County-season mapping is deferred until a documented crop-calendar source supports it. |
| 2026-08-02 | Pilot selection | Busia remains provisional; Trans Nzoia is the fallback. The published data-quality gate must select Busia, Trans Nzoia, or insufficient evidence from real observations. |
| 2026-08-02 | Source policy | Try KNBS/NIPFN first, KilimoSTAT second, then Food Systems Dashboard. Preserve accepted source bytes outside Git where redistribution is unclear. |

## Current Slice 2 state

- Branch: `slice/2-target-dataset` at `2872141` before local changes.
- Source registry, immutable manifests, fail-closed acquisition, canonical observations, quality reports, and the pilot gate already exist.
- No official snapshot, real target table, or model exists yet. Do not describe Slice 2 as complete until source bytes pass the registered terms, media, schema, and lineage gates.

## 2026-08-02 baseline reproducibility repair

- Regenerated `uv.lock` with the available `uv 0.7.8`; dependency pins did not change, but the lock metadata now matches the resolver and `uv sync --locked --extra dev` succeeds.
- Added the repository root to Pytest's import path so tests importing `scripts.*` work on Windows.
- Applied Python 3.12-safe Ruff modernization and corrected lockfile tests to validate the current UV extra-dependency format rather than an invalid manual Pytest-to-Pygments edge.
- Enforced LF for deterministic feasibility artifacts through `.gitattributes`; the generated scorecard is byte-stable on this worktree.
- Local verification used `uv run pytest -q --basetemp .pytest-tmp` because the shared Windows temp root is denied. The command passed 129 tests, followed by lint, repository and Slice 2 validators, compilation, and API smoke.
