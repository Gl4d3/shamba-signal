# Data Source Register

**Purpose:** record candidate public evidence and the publication decision required before any source enters modelling.
**Foundation review date:** 2026-08-01
**Rule:** a landing page or valid download does not by itself prove completeness, model suitability, or redistribution permission.

| Source | Candidate role | Current foundation decision |
|---|---|---|
| Kenya KilimoSTAT crops | County production, harvested area, and yield labels | **Review required.** Verify the live endpoint, exact maize elements, county/year coverage, source flags, schema, and dataset-specific redistribution terms before accepting bytes. |
| Copernicus Sentinel-2 L2A | Multispectral condition time series | **Verified candidate access.** Record collection, processing baseline, tile, acquisition date, cloud/observation counts, and Copernicus attribution per snapshot. |
| CHIRPS v3 | Rainfall, anomaly, onset, and dry-spell features | **Review required for publication.** Capture product/version, final-versus-preliminary policy, downloaded README, and attribution terms. |
| SoilGrids | Static soil properties and uncertainty | **Verified candidate access.** Use WCS subsets or stable assets; record property, depth, quantile, version, and citation. |
| ICPAC Kenya Admin Level 1 | County geometry | **Review required.** Confirm licence and boundary vintage; compare with an explicitly licensed alternative. |
| ICPAC / RCMRD Kenya 2015 croplands | Crop-mask context | **Blocked for redistribution until clarified.** Metadata does not establish a suitable licence; do not bundle or make it the sole mask. |

## Official landing URLs

- https://statistics.kilimo.go.ke/en/cd_s_crops/
- https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html
- https://www.chc.ucsb.edu/data/chirps3
- https://docs.isric.org/globaldata/soilgrids/index.html
- https://geoportal.icpac.net/layers/geonode%3Aken_adm1
- https://geoportal.icpac.net/layers/geonode%3Akenya_croplands_2015

## Required live verification per source

1. Open the official landing page and identify the publisher.
2. Resolve the actual acquisition method and any material request parameters.
3. Validate status, redirects, content type, payload shape, and schema.
4. Preserve original bytes before transformation and compute a checksum.
5. Record retrieval time, byte size, spatial/year coverage, row counts, and relevant elements.
6. Capture exact terms evidence and distinguish access permission from redistribution permission.
7. Record browser-only, authentication, bot, or stability limitations.
8. Publish bytes only when redistribution is explicitly supported.

## Canonical source-snapshot contract

Each applicable manifest records source ID, publisher, dataset title, landing URL, exact acquisition URL or parameters, access method, source version, retrieval timestamp, spatial/temporal coverage, media type, byte size, checksum, schema fingerprint, terms snapshot, licence decision, redistribution status, portable storage identifier, and transformation code revision.

No canonical manifest may contain credentials, cookies, bearer headers, signed URLs, or unnecessary local absolute paths.
