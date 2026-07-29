# Shamba Signal MVP Definition

## Single sentence

Produce a defensible mid-season yield forecast for one data-selected crop at county-season
resolution across Kenya, with one data-selected county deep dive, calibrated uncertainty,
stress attribution, evidence lineage, and guardrailed response options.

## Primary user

Agricultural researchers and program analysts. County extension leadership and food-security
teams are secondary users of the same evidence. Farmer-facing workflows are outside the first release.

## Primary output

For every county with sufficient evidence:

- estimated yield in tonnes per hectare;
- calibrated lower and upper prediction bounds;
- historical county baseline and anomaly;
- data-completeness and model-confidence indicators;
- forecast version, cutoff date, crop calendar source, and model version;
- risk flag with the evidence that produced it.

## Spatial explanatory output

Ward and pixel layers may show vegetation performance, rainfall anomalies, heat stress,
soil-moisture context, and **relative yield potential**. They must never be labelled measured
ward yield or farm yield without matching validation data.

## MVP screens

1. **National Yield Outlook** — county map, crop/season selector, forecast, anomaly,
   confidence, data quality, and forecast version.
2. **County Yield Analysis** — actual-versus-predicted history, seasonal climate and vegetation
   curves, prediction interval, stress periods, model drivers, and similar seasons.
3. **Model Evidence** — baseline comparison, spatial and temporal holdouts, errors by county/year,
   prediction-interval coverage, feature importance, lineage, and limitations.
4. **Data Explorer** — source, resolution, coverage, access method, licensing, missingness, and
   last successful ingestion.
5. **Advisory Review** — approved response options and the evidence linking each option to the flag.

## Acceptance criteria

- The crop and pilot county are selected by a reproducible data-feasibility scorecard.
- A new environment can regenerate the county-season modelling table from documented sources.
- The final model beats historical mean and previous-season baselines on held-out geography and time.
- Every forecast contains a calibrated prediction interval and explicit data-quality status.
- A researcher can trace each forecast to source snapshots, features, model, and cutoff date.
- Advisory output contains only actions present in a versioned approved playbook.
- Scheduled national and analyst-triggered runs produce versioned, comparable forecast outputs.
- The public application is usable without opening a notebook.

## Explicit non-goals

- Farm-level yield prediction without farm-level labels.
- Ward-level measured yield inferred by distributing county labels.
- Multiple crops before one crop is validated.
- Automated resource allocation or autonomous agronomic treatment.
- Pesticide, fertilizer, irrigation dosage, or farm-specific medical-style advice.
- Full AWS deployment before the local working product demonstrates value.
