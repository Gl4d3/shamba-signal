# Earthy Research Dashboard Design

## Goal

Turn the current long-form evidence page into a responsive, genuinely interactive research dashboard that preserves Shamba Signal's honest county-year evidence boundary while making model performance, county history, data health, and methodology immediately explorable.

## Selected visual direction

The selected direction is the **Natural & Earthy** concept: deep forest navigation, warm sand surfaces, restrained olive accents, editorial agricultural imagery, rounded analytical panels, and dense-but-readable data presentation. The interface should feel like a serious agricultural intelligence product rather than a slideshow or marketing page.

## Product boundary

The dashboard remains a local FastAPI application backed by the generated evaluation fixture. It does not become an operational forecast, advisory engine, national service, or new modelling programme. The 2023 labels remain visibly provisional and the weather-model result remains an explicit no-go.

## Architecture

Keep the existing lightweight stack: FastAPI serves one HTML shell, one CSS bundle, one JavaScript module, and the existing JSON APIs. Do not add React, a bundler, a database, or new runtime dependencies. The browser layer is split internally into small rendering and interaction functions so it behaves like an application without increasing deployment weight.

The UI loads three real endpoints in parallel:

- `/api/v1/evaluation` for model metrics, features, limitations, county history, predictions, and errors;
- `/api/v1/platform/status` for release and source-readiness metadata; and
- `/healthz` for live service health.

## Information architecture

### Persistent shell

- Dark forest sidebar with Shamba Signal identity.
- Anchor navigation for Overview, Models, Counties, Method, and Data quality.
- Dataset scope block and live API status at the bottom.
- Mobile collapsible navigation with the same destinations.

### Overview

- Earthy hero with the real no-go result and provisional-status badge.
- KPI row: benchmark MAE, Weather Ridge MAE, gap to benchmark, and county coverage.
- Model comparison chart with MAE/RMSE toggle.
- Explicit benchmark winner and scientific interpretation.

### Models

- Ranked model battlecard driven by fixture metrics.
- Hover/focus details and metric toggle.
- Model explanations that distinguish references from the weather-informed model.

### Counties

- Searchable county combobox.
- Historical actual-yield line chart.
- 2023 actual and all four model predictions on the same evidence view.
- Signed model errors and best-county model indicator.
- Download of the selected county evidence as CSV.

### Method and data quality

- Feature definitions from the fixture.
- Split timeline: 2012–2021 train, 2022 select, 2023 final provisional test.
- Lineage flow from official labels and ERA5 through the experiment to the dashboard.
- Live API/service status, fixture version, coverage summary, and limitations.
- Download of the complete loaded evaluation as JSON.

## Interaction model

- Model metric toggle updates comparison bars and ranking without another network call.
- County search filters options and Enter selects the first visible result.
- County selection updates history, prediction bars, errors, summary copy, and CSV export.
- Navigation updates the active section using `IntersectionObserver`.
- Retry action re-fetches all endpoints after an error.
- Downloads are generated from the same loaded fixture; no invented or separately maintained values.

## Responsive behaviour

- Desktop: fixed 248 px sidebar and fluid two-column dashboard canvas.
- Tablet: narrower sidebar and stacked analytical panels.
- Mobile: sticky compact header, horizontal section navigation, single-column cards, horizontally scrollable dense tables where needed, and touch-sized controls.
- Charts remain SVG with responsive view boxes and accessible text summaries.

## States and accessibility

- Loading skeletons for metrics and charts.
- Honest fixture-unavailable error with retry; health/status can degrade independently.
- Keyboard-operable metric tabs, county search, navigation, and download actions.
- Visible focus styles, semantic landmarks, table headers, chart labels, and status text.
- Reduced-motion support.

## Verification

- Python endpoint and HTML contract tests.
- Browser smoke script checks API loading, county switching, metric toggling, downloads, mobile layout, and console errors.
- Desktop and mobile screenshots are compared against the selected Natural & Earthy visual target.
- `design-qa.md` records iterations and must end with `final result: passed` before merge.
