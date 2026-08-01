# Data Source Register

**Purpose:** record candidate public evidence and the publication decision required before any source enters modelling.  
**Slice 1 review date:** 2026-08-01  
**Rule:** a landing page or valid download does not by itself prove completeness, model suitability, or redistribution permission.

## Slice 1 decision

The metadata-level feasibility scorecard selects **maize** and **Busia**, with **Trans Nzoia** as the first fallback. This decision ranks acquisition prospects; it does not assert that the target labels, satellite observations, or crop-mask overlap have passed Slice 2 acceptance.

The canonical record is [the pilot-selection decision](pilot-selection-decision.md). Machine-readable evidence and scores are under `data/feasibility/`.

| Source | Candidate role | Current decision |
|---|---|---|
| Kenya KilimoSTAT crops | Primary county production, harvested area, yield, source, and flag records | **Review required.** Resolve the exact maize acquisition, schema, county/year continuity, source flags, and extract-specific terms before accepting bytes. |
| KNBS/NIPFN maize production by county, 2012–2020 | Historical county maize evidence and cross-check | **Review required.** Landing metadata is known; capture the actual file, checksum, schema, units, flags, and terms. |
| Kenya Food Systems Dashboard maize yield | Recent county-yield continuity | **Review required.** Validate the CSV response, media type, schema, years, and download-specific attribution before caching. |
| Kenya Space Agency / AfriCultuReS crop calendars | Season timing, phenology, and Trans Nzoia fallback evidence | **Review required.** Capture product version, geometry, crop coverage, and downloadable-layer terms. |
| PlantVillage Crop Type Kenya | Open 10 m crop-type, field-boundary, and crop-density evidence in western Kenya | **Verified candidate access.** CC BY 4.0; preserve attribution and confirm spatial overlap/class balance for Busia. |
| NASA Harvest Busia and Kenya crop maps | Busia-specific cropland context and sensitivity comparison | **Review required.** Do not redistribute because the dataset page does not specify a licence. |
| Copernicus Sentinel-2 L2A | Multispectral condition time series | **Verified candidate access.** Record collection, processing baseline, tile, acquisition date, cloud/observation counts, and attribution per snapshot. |
| CHIRPS v3 | Rainfall, anomaly, onset, and dry-spell features | **Review required for publication.** Capture product/version, final-versus-preliminary policy, downloaded README, and attribution terms. |
| SoilGrids | Static soil properties and uncertainty | **Verified candidate access.** Use WCS subsets or stable assets; record property, depth, quantile, version, and citation. |
| ICPAC Kenya Admin Level 1 | County geometry | **Review required.** Confirm licence and boundary vintage; compare with an explicitly licensed alternative. |
| ICPAC / RCMRD Kenya 2015 croplands | Crop-mask comparison | **Blocked for redistribution until clarified.** Do not bundle or make it the sole mask. |

## Required Slice 2 validation

1. Resolve and download the official maize records without bypassing access controls.
2. Preserve original bytes and compute SHA-256 checksums.
3. Profile county/year coverage, row counts, elements, units, flags, duplicates, and missingness.
4. Keep reported yield separate from any derived yield and validate positive, period-compatible inputs before division.
5. Measure Sentinel observation availability by forecast cutoff and Busia crop-label overlap.
6. Confirm Busia only if the measured gates pass; otherwise switch to Trans Nzoia and record why.
7. Publish no source bytes whose redistribution state remains unresolved.

## Official landing URLs

- https://statistics.kilimo.go.ke/en/cd_s_crops/
- https://nipfn.knbs.or.ke/download/maize-production-by-county-2012-2020/
- https://fsd.kilimo.go.ke/indicators/food-supply-chains/production-systems-and-input-supply/maize-yield/admin-1/table
- https://africultures.ksa.go.ke/en/services/africultures-s2-crop-service/s2-p04-crop-calendar-assessment-and-monitoring/
- https://collections.eurodatacube.com/plantvillage-crops-kenya/
- https://data.harvestportal.org/en/dataset/crop-maps
- https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html
- https://www.chc.ucsb.edu/data/chirps3
- https://docs.isric.org/globaldata/soilgrids/index.html
- https://geoportal.icpac.net/layers/geonode%3Aken_adm1

## Canonical source-snapshot contract

Each applicable manifest records source ID, publisher, dataset title, landing URL, exact acquisition URL or parameters, access method, source version, retrieval timestamp, spatial/temporal coverage, media type, byte size, checksum, schema fingerprint, terms snapshot, licence decision, redistribution status, portable storage identifier, and transformation code revision.

No canonical manifest may contain credentials, cookies, bearer headers, signed URLs, or unnecessary local absolute paths.
