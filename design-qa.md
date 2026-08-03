# Shamba Signal Earthy Dashboard — Design QA

## Comparison target

- **Source visual truth:** `/mnt/data/a_wide_presentation_comparison_image_showing_two_d.png`, right-hand **Approach 2: Natural & Earthy** dashboard.
- **Implementation:** `feature/earthy-research-dashboard` using the branch HTML, CSS, and JavaScript modules.
- **Primary state:** evaluation fixture loaded, no-go result visible, county explorer available, platform and health APIs live.

## Capture setup

The sandbox could not clone GitHub or navigate to localhost because outbound DNS and local browser navigation were administratively blocked. The exact branch HTML/CSS/JavaScript was therefore rendered in system Chromium through Playwright using `page.set_content`, with the three network endpoints intercepted using deterministic responses matching the real API schemas and the committed model metrics. This exercises the browser code and controls rather than replacing the interface with a static image.

| Evidence | Viewport / density | State | Local path |
| --- | --- | --- | --- |
| Desktop overview | 1440 × 1024 CSS px, device scale factor 1 | MAE overview, 47 counties, all services ready | `/mnt/data/shamba-signal-preview/qa/desktop-overview.png` |
| Desktop county explorer | 1440 × 1024 CSS px, device scale factor 1 | Nairobi selected, RMSE active | `/mnt/data/shamba-signal-preview/qa/desktop-county.png` |
| Mobile overview | 390 × 844 CSS px, device scale factor 1 | Responsive overview and mobile navigation | `/mnt/data/shamba-signal-preview/qa/mobile-overview.png` |
| Browser smoke report | N/A | Interaction and console result | `/mnt/data/shamba-signal-preview/qa/smoke-report.json` |

The source is a wide presentation board containing two concepts; comparison used the right-hand dashboard region. The implementation captures contain app content only, with no browser chrome. Density normalization was unnecessary because both implementation captures used device scale factor 1.

## Full-view comparison

The implementation preserves the selected visual system and hierarchy:

- fixed deep-forest navigation rail;
- warm sand application canvas;
- agricultural landscape hero with olive/amber light;
- rounded cream analytical surfaces with restrained shadows;
- compact search, release, and live-status controls;
- KPI row, model battlecard, county evidence chart, method, and data-health regions;
- editorial serif headings paired with compact sans-serif application copy.

Unlike the conceptual mock, the implementation removes invented prices, alerts, forecasts, advisories, feature importance, and map values. Those areas are replaced with the real Shamba Signal evidence contract: MAE/RMSE comparison, county actuals and predictions, signed model errors, feature definitions, temporal split, lineage, limitations, and live API state.

## Focused-region comparison

### Hero and KPIs

The source uses a photographic farm banner and four compact metrics. The implementation matches the proportions, forest/earth palette, rounded geometry, and compact metric cadence while using an abstract landscape treatment to avoid adding a heavy image dependency. The hero communicates the actual no-go result and keeps the retrospective boundary visible.

### Model evidence

The source's model battlecard and driver chart become a working MAE/RMSE ranking. Controls update bars, values, ranks, and summaries from the loaded fixture. The county historical mean remains visually and numerically identifiable as the winner.

### County workspace

The county section uses the same cream-panel / dark-summary-card relationship as the source. The history SVG, provisional marker, four model predictions, signed errors, closest-model result, and CSV export all update after county selection.

### Mobile

At 390 × 844, the sidebar becomes a sticky compact header and horizontal navigation. The hero, buttons, KPI cards, and content remain readable, touch-sized, and free of horizontal page overflow.

## Required fidelity surfaces

- **Fonts and typography:** Georgia supplies the warm editorial display voice; Inter/system sans supplies controls and dense evidence labels. Hierarchy, wrapping, line height, and optical weight were checked at both target widths. No clipped or unreadable text was found.
- **Spacing and layout rhythm:** Desktop uses a 248 px navigation rail, wide analytical canvas, 14–17 px panel gaps, and 17–24 px radii. Mobile collapses to a single column with 12–21 px edge spacing. No persistent control or content overflow was found.
- **Colors and tokens:** Forest, olive, sand, soil, amber, and semantic error tokens are centralized in CSS variables. Contrast remained readable across the dark sidebar, hero, featured KPI, county summary, and light analytical surfaces.
- **Image quality and asset fidelity:** The hero is an intentional lightweight abstract agricultural landscape rather than a raster photo. It remains sharp at all widths and preserves the source's natural/earthy mood without adding a remote or bundled photographic asset.
- **Copy and content:** All visible product claims match the retrospective county-year evidence boundary. The UI does not claim live forecasts, advisories, prices, causal drivers, or farm-level accuracy.

## Interaction verification

The fresh Chromium smoke run verified:

- evaluation, platform status, and health API loading through `Promise.allSettled`;
- loading, ready, degraded, and fixture-error code paths;
- MAE → RMSE metric switching and accessible selected state;
- searchable county selection and Nairobi update;
- actual history, four predictions, signed errors, and closest-model result;
- selected-county CSV download containing county and weather-model rows;
- complete evaluation JSON download containing all 47 counties;
- desktop sidebar and mobile horizontal navigation behavior;
- no horizontal page overflow at 390 px;
- no browser console or page errors.

## Comparison history

### Iteration 1

- **[P2] Global search showed the default selected county.**
  - Evidence: the first desktop/mobile capture displayed `Baringo` in the top search control immediately after load.
  - Impact: the control read as stale state instead of an available query field, drifting from the selected concept.
  - Fix: added a small search-state module that clears the transient global query after initial/default county selection and after Enter-driven navigation, while leaving the dedicated county combobox as the persistent selected value.
  - Post-fix evidence: the final desktop and mobile overview captures show an empty search field; the browser smoke run asserts the input is empty after load.

### Iteration 2

- **[P1] Platform status API exposed the obsolete Slice 2A release.**
  - Evidence: the live service contract still returned `slice-2a-annual-snapshot-v1`, `not scheduled`, and planned baseline capabilities.
  - Impact: the dashboard could display technically false release and readiness information despite the completed baseline, weather experiment, and UI.
  - Fix: updated the status API to `county-year-weather-evidence-v1`, the retrospective end-of-year timing boundary, all-47-county coverage, and four delivered capabilities. Updated regression tests accordingly.
  - Post-fix evidence: the final desktop capture shows the completed release; 7 focused FastAPI/UI contract tests pass.

## Verification commands and results

- `PYTHONPATH=src pytest -q tests/test_home.py tests/test_platform_status.py` → **7 passed in 0.32s**.
- `node --check src/shamba_signal/web/static/app.js` → **passed**.
- `node --check src/shamba_signal/web/static/search-state.js` → **passed**.
- `python /mnt/data/shamba-signal-preview/visual_smoke.py` → desktop/mobile screenshots produced, RMSE and Nairobi interactions passed, CSV/JSON downloads passed, **0 console errors**.
- Ruff could not be executed in the sandbox because the installed environment does not contain the `ruff` command or module. No claim is made that Ruff ran.

## Residual P3 polish

- The approved concept uses a photographic hero; the implementation uses a crisp abstract agricultural landscape to keep the app self-contained and lightweight. This is an intentional product constraint, not a broken or placeholder asset.

## Final result

final result: passed
