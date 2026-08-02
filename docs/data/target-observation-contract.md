# Canonical Target Observation Contract

## Purpose

This contract converts source-specific agricultural records into a stable county × crop × period representation without erasing the original evidence. The currently supported target grain is county-year; annual totals must not be disaggregated into seasons by a crop calendar.

## County identity

County names are resolved against the 47-county registry in `data/feasibility/candidate_profiles.json`.

- Canonical identifiers use the existing `candidate_id` values, such as `busia` and `trans_nzoia`.
- Case, punctuation, apostrophes, hyphens, and whitespace are normalized for matching.
- Narrow explicit aliases cover `Nairobi` → `nairobi_city` and `Muranga` → `muranga`.
- Unknown or colliding aliases fail; the system does not guess a county.

## Observation grain

Every canonical observation has one `TargetKey`:

```text
county_id × crop_id × period_id
```

`period_id` is deliberately a string. The accepted Slice 2A observations are annual years; no authoritative national county × season observed maize-yield panel has been found, so county-season is evidence-insufficient.

## Elements and units

| Element | Accepted source units | Canonical unit |
|---|---|---|
| Production | tonnes/tons/metric tonnes, kilograms | `t` |
| Harvested area | hectares, acres | `ha` |
| Reported yield | tonnes per hectare, kilograms per hectare | `t/ha` |

Conversions are explicit:

- kilograms ÷ 1,000 → tonnes;
- acres × 0.40468564224 → hectares;
- kilograms per hectare ÷ 1,000 → tonnes per hectare.

Unknown units, non-numeric values, non-finite values, and negative values fail before publication. Original value and unit remain alongside the normalized fields.

## Lineage and quality

Each observation retains:

- source name and source flag;
- quality class: `accepted`, `flagged`, or `review-required`;
- immutable snapshot identifier;
- original source fields when supplied;
- calendar source when a season mapping is later applied.

Quality classes are explicit source-adapter decisions. The generic target layer does not infer that a source flag is safe.

## Source adapter boundary

An unactivated KilimoSTAT adapter maps its documented fields—County, Domain, Subdomain, Element,
Item, Value, Unit, Year, Source, and Flag—into canonical observations. KilimoSTAT is off the
critical path because no current verified response contract is accessible.

- Non-maize rows fail for the current selected-crop build.
- Unsupported elements and placeholder/non-numeric values fail.
- Original fields are retained.
- Unknown flags remain `review-required`; an explicit source-flag policy is required before a flag may be treated as accepted or merely flagged.

Food Systems Dashboard adapters are off the critical path because no current verified response
contract is accessible.
The KNBS/NIPFN workbook adapter is verified against its tidy `County`, `Year`, `Indicator`, and
`Value` sheet. Its three observed indicators map to harvested area (`ha`), production (`t`), and
reported yield (`t/ha`); workbook-specific aliases resolve `Homabay` and `Tharaka-Nthi` without
guessing other county names.

## Derived yield

Derived yield is created only when production and harvested area:

1. have the correct elements;
2. use the same county, crop, and period;
3. have normalized compatible units;
4. have harvested area strictly greater than zero.

The result records the formula and all source snapshot identifiers:

```text
production_tonnes / harvested_area_ha
```

## Reported-versus-derived reconciliation

Reported and derived yield remain separate fields. Reconciliation produces one of:

- `reported_only`;
- `derived_only`;
- `consistent` within configured relative and absolute tolerances;
- `divergent` outside those tolerances.

The contract intentionally exposes no automatically selected yield value. Selection or abstention belongs to the later dataset-quality policy and must be evidence-backed.

## Duplicate control

Only one canonical observation may exist for each target key and element within a build input. Duplicate production, harvested-area, or reported-yield observations fail rather than being silently averaged or overwritten.

## Deterministic quality build

The target-build layer now produces deterministic target CSV and quality JSON representations. Its quality report records:

- county and period coverage;
- rows with reported, derived, missing, consistent, or divergent yield;
- quality-class and source-flag counts;
- canonical units;
- the fail-on-duplicate policy.

A pilot gate can return `confirmed`, `fallback`, or `insufficient` using explicitly supplied thresholds. No default threshold silently selects Busia or Trans Nzoia.

## Current boundary

These contracts and the KNBS/NIPFN annual-workbook mapping have tests. KilimoSTAT and the Food Systems Dashboard are outside the critical path until a current verified response contract is accessible.
They do not mean:

- annual records have been mapped to county-specific crop seasons;
- source redistribution terms are resolved;
- the annual target can support a forecasting model;
- a publishable Parquet dataset exists.
