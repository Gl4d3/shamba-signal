# Data Source Register

**Purpose:** identify candidate public evidence before selecting the MVP crop and county.  
**Review date:** 2026-07-29  
**Rule:** no source enters the modelling pipeline until access, schema, coverage, and licensing are captured in a source snapshot.

| Source | Proposed role | Coverage / characteristics | Access and licensing decision |
|---|---|---|---|
| Kenya KilimoSTAT crops | Candidate official county production, area, and yield labels | County table includes domain, subdomain, element, item, value, unit, year, source, and flag; portal states monthly updates | Candidate primary label source. Portal states CC BY-NC-SA 3.0 IGO plus dataset-specific terms. Verify endpoint behaviour and exact redistribution obligations before caching public extracts. |
| Copernicus Sentinel-2 L2A | Multispectral crop-condition time series | Global data from 2015; 13 bands with 10 m, 20 m, and 60 m native resolutions; L2A is analysis-ready surface reflectance | Candidate primary optical source. Record collection, processing baseline, tile, cloud mask, and observation counts. |
| CHIRPS v3 | Rainfall, anomaly, onset, and dry-spell features | 1981 to near-present; 0.05° land grid; preliminary and monthly final products | Candidate primary rainfall source. Prefer final product for training and define preliminary/final policy for operational forecasts. |
| SoilGrids | Static soil property covariates and uncertainty | Global gridded properties with WCS and WebDAV access | Candidate soil source. Use WCS subsets or cached WebDAV/VRT assets; do not make the beta REST API a production dependency. |
| ICPAC Kenya Admin Level 1 | Candidate county geometry | Kenya administrative level 1 download/OGC layer | Technically usable, but licensing needs confirmation before redistribution. Compare against an explicitly licensed alternative. |
| ICPAC / RCMRD Kenya 2015 croplands | Candidate crop mask and crop context | Landsat 8-derived 30 m cropland, reference year 2015, with county and crop attributes | Useful for feasibility testing, but metadata reports no specified license. Do not redistribute or make it the sole crop mask without permission. |

## Official source URLs

- https://statistics.kilimo.go.ke/en/cd_s_crops/
- https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html
- https://www.chc.ucsb.edu/data/chirps3
- https://docs.isric.org/globaldata/soilgrids/index.html
- https://docs.isric.org/globaldata/soilgrids/WebDav.html
- https://geoportal.icpac.net/layers/geonode%3Aken_adm1
- https://geoportal.icpac.net/layers/geonode%3Akenya_croplands_2015

## Slice 1 investigation questions

1. Which KilimoSTAT crops expose the longest consistent county histories for production, area, and yield?
2. Are yields reported directly, derived, or mixed by crop/year, and how do flags affect trust?
3. Which counties have continuous labels and sufficient crop area for remote-sensing aggregation?
4. Which crop calendars are available at county or agro-ecological resolution?
5. Which boundary and crop-mask sources have explicit licences suitable for a public repository and preview?
6. How many valid Sentinel-2 observations remain by county and season after cloud masking?
7. Does the label publication date permit a credible historical mid-season backtest without leakage?

## Required source-snapshot evidence

Every adapter must save publisher, dataset title, URL, terms URL, retrieved timestamp, request parameters,
source version, checksum, raw storage URI, schema fingerprint, and the exact transformation code revision.
