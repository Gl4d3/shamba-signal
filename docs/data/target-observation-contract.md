# Canonical Target Observation Contract

## Purpose

This contract converts source-specific agricultural records into a stable county × crop × period representation without erasing the original evidence. It is a prerequisite for the target dataset; it is not evidence that an official source snapshot has already been accepted.

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

`period_id` is deliberately a string so annual records such as `2023` and later season-specific identifiers can coexist without pretending an annual label is already a crop season.

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

## Current boundary

This contract has fixture-level tests. It does not yet mean:

- an official source snapshot has passed acquisition gates;
- annual records have been mapped to county-specific crop seasons;
- Busia has passed continuity, flags, or missingness thresholds;
- a publishable Parquet target dataset exists.
