# Slice 2 Acquisition Status

## Active outcome

Build an immutable, reproducible maize county-season target dataset and confirm Busia or switch to Trans Nzoia through downloaded-data evidence.

## Source paths discovered

| Source | Acquisition pattern | Current state | Next adapter action |
|---|---|---|---|
| KilimoSTAT crops | Parameterized data API / JSON endpoint | Official crop table, schema, county coverage, monthly update policy, and terms verified | Resolve valid maize element/item/year parameters and save the first content-addressed snapshot |
| Kenya Food Systems Dashboard maize yield | Direct indicator CSV API | Indicator endpoint located at `/api/indicators/278/countries/ken/csv?adminLevel=LEVEL_1`; generic download clients receive an unusual response | Implement browser-compatible headers/response validation and verify CSV schema before accepting bytes |
| KNBS/NIPFN maize 2012–2020 | WordPress download-manager page | Landing page, 67.13 KB file metadata, 2012–2020 scope, and Kilimodata source verified; stable asset URL is not exposed in parsed HTML | Resolve the download-manager asset request or record a manual verified acquisition with checksum |

## Implemented

- `SourceDefinition` enforces HTTPS acquisition URLs.
- `SnapshotManifest` records publisher, source/landing URLs, acquisition mode, terms status, retrieval timestamp, media type, byte size, SHA-256, and storage URI.
- Manifest behavior is covered by a red-green test cycle.
- Source acquisition states are versioned in `data/sources/maize_sources.json`.

## Publication gates

No source can enter the target table until:

1. response bytes are saved without mutation;
2. SHA-256 and byte size are recorded;
3. retrieval timestamp, source URL, terms status, and media type are recorded;
4. schema and row count are profiled;
5. original values, units, sources, and flags are retained;
6. redistribution status is explicit.

## Known environmental constraint

The current isolated runtime cannot resolve public hosts directly, and the external fetch layer does not successfully return the dashboard CSV bytes. This affects acquisition execution, not the source-manifest code. The adapters will treat inaccessible or ambiguous responses as failed snapshots rather than manufacturing data.
