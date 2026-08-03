# Earthy Research Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the slideshow-like evidence page with a responsive Natural & Earthy research dashboard whose charts, filters, downloads, and system states are driven by the existing real APIs.

**Architecture:** Preserve FastAPI plus static HTML/CSS/JavaScript. Load evaluation, platform status, and health concurrently; keep the fixture as the single source of analytical truth; organize browser behavior into rendering, state, chart, navigation, and export functions without introducing a frontend build chain.

**Tech Stack:** Python 3.12, FastAPI, semantic HTML, modern CSS, browser-native ES2022 JavaScript, SVG charts, pytest, Playwright/Chromium for visual smoke checks.

## Global Constraints

- Keep the application lightweight; add no React, Node production runtime, database, or frontend bundler.
- Every analytical value must come from `/api/v1/evaluation`; do not fabricate forecasts, alerts, advisories, prices, or feature importance.
- Keep 2023 visibly provisional and preserve the retrospective county-year/no-go evidence boundary.
- Maintain mobile and desktop support and keyboard-visible focus states.
- Do not expose source-restricted row data beyond what the private local fixture already serves.

---

### Task 1: Dashboard shell and API state

**Files:**
- Modify: `src/shamba_signal/web/index.html`
- Modify: `src/shamba_signal/web/static/styles.css`
- Modify: `src/shamba_signal/web/static/app.js`
- Modify: `tests/test_home.py`

**Interfaces:**
- Consumes: `GET /api/v1/evaluation`, `GET /api/v1/platform/status`, `GET /healthz`.
- Produces: `loadDashboard(): Promise<void>`, application state object, loading/error/ready page states, persistent responsive navigation.

- [ ] Extend `tests/test_home.py` with shell-contract assertions for the sidebar, hero, API status, model metric tabs, county search, and download controls.
- [ ] Run `pytest tests/test_home.py -q` and confirm the new assertions fail against the old page.
- [ ] Replace the HTML with semantic dashboard landmarks and honest loading placeholders.
- [ ] Add the forest/sand/olive visual tokens and responsive shell CSS.
- [ ] Implement concurrent endpoint loading, health degradation, retry, and active-section navigation.
- [ ] Run `pytest tests/test_home.py -q` and confirm it passes.
- [ ] Commit with `feat: build earthy dashboard shell`.

### Task 2: National model evidence

**Files:**
- Modify: `src/shamba_signal/web/static/app.js`
- Modify: `src/shamba_signal/web/static/styles.css`
- Modify: `tests/test_home.py`

**Interfaces:**
- Consumes: `payload.models[]`, `payload.result`, `payload.result_statement`, `payload.provisional_test_year`.
- Produces: `renderOverview(payload)`, `renderModelComparison(models, metric)`, `renderModelBattlecard(models, metric)`, accessible SVG comparison chart.

- [ ] Add script-contract assertions for MAE/RMSE metric toggling, benchmark ranking, and no-go copy.
- [ ] Run the focused test and confirm failure.
- [ ] Render real KPI values and the gap to the county-mean benchmark.
- [ ] Implement metric tabs that update the model bars, labels, ranks, and summary text.
- [ ] Add keyboard and selected-state behavior to metric controls.
- [ ] Run the focused test and confirm pass.
- [ ] Commit with `feat: add interactive model evidence`.

### Task 3: County explorer and data export

**Files:**
- Modify: `src/shamba_signal/web/static/app.js`
- Modify: `src/shamba_signal/web/static/styles.css`
- Modify: `tests/test_home.py`

**Interfaces:**
- Consumes: `payload.counties[]` including history, 2023 actual, predictions, and signed errors.
- Produces: `renderCounty(county)`, `renderHistoryChart(history, test)`, searchable county picker, county CSV export, complete fixture JSON export.

- [ ] Add assertions for county filtering, all four model predictions, CSV export, and JSON export.
- [ ] Run the focused test and confirm failure.
- [ ] Build the searchable county list with Enter/Escape and click selection behavior.
- [ ] Draw responsive actual-yield history and prediction comparison SVGs from the selected county.
- [ ] Render signed errors and identify the closest model for the selected county.
- [ ] Generate CSV and JSON downloads from the loaded fixture.
- [ ] Run the focused test and confirm pass.
- [ ] Commit with `feat: add functional county explorer`.

### Task 4: Method, quality, responsive hardening, and visual QA

**Files:**
- Modify: `src/shamba_signal/web/static/app.js`
- Modify: `src/shamba_signal/web/static/styles.css`
- Modify: `tests/test_home.py`
- Create: `design-qa.md`

**Interfaces:**
- Consumes: feature definitions, limitations, fixture metadata, platform status, and health status.
- Produces: method timeline, data lineage, system-health panel, complete mobile layout, final QA evidence.

- [ ] Add assertions for feature rendering, split timeline, limitations, service health, and fixture version.
- [ ] Run the focused test and confirm failure.
- [ ] Render features, split timeline, lineage, data coverage, platform release, service/fixture states, and limitations.
- [ ] Add reduced-motion, focus-visible, small-screen navigation, chart overflow, loading, empty, and error styles.
- [ ] Run all available Python tests and Ruff checks.
- [ ] Serve a fixture-backed local app and capture 1440×1024 and 390×844 screenshots in real Chromium.
- [ ] Test county switching, metric toggling, retry/error handling, downloads, navigation, and browser console errors.
- [ ] Compare both screenshots with the selected Natural & Earthy concept; fix every P0/P1/P2 issue and repeat.
- [ ] Write `design-qa.md` with evidence paths and `final result: passed`.
- [ ] Commit with `test: verify earthy dashboard experience`.

### Task 5: Review and integration

**Files:**
- Review all branch changes.

**Interfaces:**
- Consumes: completed tasks and verification evidence.
- Produces: reviewed PR merged to `main`.

- [ ] Compare the feature branch with `main` for accidental scope expansion or invented product claims.
- [ ] Verify the final branch head and tests once more.
- [ ] Open a pull request with implementation and verification evidence.
- [ ] Review the PR patch and resolve any substantive issue.
- [ ] Merge the PR to `main` using squash merge.
