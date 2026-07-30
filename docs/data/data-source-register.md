# Data Source Register

**Purpose:** record the public evidence used to select the MVP crop and pilot county, then govern entry into the modelling pipeline.  
**Review date:** 2026-07-30  
**Rule:** no source enters modelling until access, schema, coverage, checksum, and licensing are captured in an immutable source snapshot.

## Slice 1 decision

- **Selected crop:** maize
- **Selected deep-dive county:** Busia
- **Fallback county:** Trans Nzoia
- **Status:** selected for Slice 2, subject to downloaded-record completeness and observation checks

| Source | Role | Coverage / characteristics | Access and licensing decision |
|---|---|---|---|
| Kenya KilimoSTAT crops | Primary official county production, area, yield, source, and flag evidence | National and county crop statistics; portal states monthly updates | Primary label candidate. Portal states CC BY-NC-SA 3.0 IGO plus dataset-specific terms. Capture the exact downloaded notice before public caching. |
| KNBS/NIPFN maize production by county 2012–2020 | Historical maize panel | Kenya counties over nine years | Metadata and download are available. Capture file terms, checksum, schema, and source flags before redistribution. |
| Kenya Food Systems Dashboard maize yield | Recent yield continuity and cross-check | County maize yield from 2021; related recent production and harvested-area indicators | Interactive table and CSV download. Capture download-specific terms and endpoint behaviour. |
| Kenya Space Agency / AfriCultuReS crop calendar | County season timing and phenology | County crop calendars; dedicated Trans-Nzoia and Narok–Nakuru layers | Technically valuable. Capture product version and downloadable-layer terms. |
| PlantVillage Crop Type Kenya | Open field/crop evidence for the Busia pilot | 10 m crop-type labels, field boundaries, and crop density in western Kenya; May–June 2019 | **CC BY 4.0.** Primary redistributable spatial-evidence anchor for Busia feasibility. |
| NASA Harvest crop maps | Busia-specific cropland and Kenya crop-mask comparison | Busia 2020 and Kenya 2019 raster resources | Page exposes TIFF resources but no licence. Do not redistribute until terms are confirmed. |
| Copernicus Sentinel-2 L2A | Multispectral crop-condition time series | Global data from 2015; analysis-ready surface reflectance | Primary optical source. Record collection, processing baseline, tile, cloud mask, and observation counts. |
| CHIRPS v3 | Rainfall, anomaly, onset, and dry-spell features | 1981 to near-present; 0.05° land grid | Primary rainfall candidate. Retain downloaded README attribution and define preliminary/final product policy. |
| SoilGrids | Static soil properties and uncertainty | Global 250 m grids with WCS and WebDAV access | Use WCS subsets or cached WebDAV/VRT assets; do not depend on the beta REST API. |
| ICPAC Kenya Admin Level 1 | Candidate county geometry | Kenya administrative level 1 | Technically usable, but licensing needs confirmation before redistribution. Compare with an explicitly licensed alternative. |

## Official source URLs

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

## Slice 2 source-snapshot gates

1. Download and checksum the official maize records.
2. Measure county-year completeness and identify duplicated county/crop/year keys.
3. Separate reported yield from yield derived from production and harvested area.
4. Normalize units without discarding original values, units, sources, or flags.
5. Verify the Busia overlap of maize labels, crop masks, and administrative geometry.
6. Measure valid Sentinel observations at the mid-season forecast cutoff.
7. Switch the pilot to Trans Nzoia if Busia fails label, overlap, or observation thresholds.
8. Record publisher, dataset title, URL, terms URL, retrieved timestamp, request parameters, source version, checksum, raw storage URI, schema fingerprint, and transformation revision for every snapshot.
