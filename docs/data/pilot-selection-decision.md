# Pilot Selection Decision

## Decision

- **MVP crop:** Maize
- **Deep-dive county:** Busia
- **Fallback county:** Trans Nzoia
- **Decision status:** selected for Slice 2, subject to snapshot-level completeness checks

The approved weighted score selects Maize at **91.25/100** and Busia at **85.75/100**.

## Crop ranking

| Rank | Crop | Score |
|---:|---|---:|
| 1 | Maize | 91.25 |
| 2 | Beans | 68.95 |
| 3 | Sorghum | 61.40 |
| 4 | Cowpea | 57.20 |

## County ranking

| Rank | County | Score |
|---:|---|---:|
| 1 | Busia | 85.75 |
| 2 | Trans Nzoia | 80.75 |
| 3 | Nakuru | 79.50 |
| 4 | Narok | 79.50 |
| 5 | Isiolo | 79.10 |

## Why this pair

Maize has the strongest combination of county-level yield history, current official dashboard coverage, crop-calendar support, and compatibility with open satellite and crop-mask evidence.

Busia adds distinct registered evidence: PlantVillage Crop Type Kenya and Crop Maps - Busia 2020 and Kenya 2019. It also retains the shared county-yield, climate, soil, boundary, calendar, and satellite evidence used to compare all counties.

Trans Nzoia remains the first fallback at **80.75/100**. Its profile retains the shared evidence set and becomes the pilot if the selected county fails the measured gates.

## Sensitivity

The winner remains unchanged in all four registered scenarios:

- Approved weights: maize + Busia
- Labels-heavy: maize + Busia
- Spatial-heavy: maize + Busia
- Governance-heavy: maize + Busia

The exact profiles and scenario weights are versioned in `data/feasibility/`.

## Source evidence

The audit records twelve public sources, including:

- KilimoSTAT county crop statistics and metadata
- KNBS/NIPFN maize production by county, 2012–2020
- Kenya Food Systems Dashboard maize and beans yield indicators
- Kenya Space Agency/AfriCultuReS crop calendars
- PlantVillage Crop Type Kenya
- NASA Harvest crop maps
- Sentinel-2 Level-2A
- CHIRPS v3
- SoilGrids
- ICPAC county boundaries

The machine-readable evidence register records publisher, URL, coverage, access method, licensing status and unresolved work.

## Required validation before modelling

1. Download and checksum the official maize county records.
2. Profile county-year completeness, flags, units and reported-versus-derived yield.
3. Measure Sentinel-2 and Sentinel-1 observation availability by forecast cutoff.
4. Confirm the exact spatial overlap and class distribution of the western Kenya crop-type labels.
5. Switch to Trans Nzoia if Busia fails label completeness, geographic overlap or observation thresholds.

## Scientific limits

- The scorecard ranks **data feasibility**, not expected model accuracy.
- The validated target remains **county × crop × season**.
- Pixel and ward products remain **relative yield potential** and **crop-stress indicators**.
- No source with unresolved redistribution terms is bundled into the repository.
- County label scores are metadata-level estimates until Slice 2 profiles the downloaded records.
