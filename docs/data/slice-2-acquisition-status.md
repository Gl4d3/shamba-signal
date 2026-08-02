# Slice 2 Acquisition Status

## Active outcome

Build an immutable, reproducible maize county-season target dataset and confirm Busia or switch to Trans Nzoia through downloaded-data evidence.

## Current implementation state

**Implemented:**

- typed source registry and snapshot-manifest contracts;
- non-empty metadata, HTTPS, allowed mode/status, media-type, and secret-URL validation;
- fail-closed HTTP response validation for status, empty bodies, HTML masquerading as data, landing-page redirects, media type, and expected schema;
- byte-preserving content-addressed snapshot storage with portable `snapshot://` identifiers;
- deterministic manifest JSON with SHA-256, schema fingerprint, retrieval time, coverage, licence state, final URL, and transformation revision;
- live HTTPS acquisition command with bounded timeout and explicit user agent;
- manual verified-file path for official download managers that do not expose a stable asset URL;
- canonical county/crop/period observations with original values, units, flags, quality class, and snapshot lineage;
- approved unit conversion for tonnes, kilograms, hectares, acres, and yield units;
- safe derived-yield and reported-versus-derived reconciliation contracts;
- duplicate target-key/element rejection;
- fixture coverage for acquisition failures, portable lineage, source registry, county aliases, units, grain matching, and reconciliation.

**Not yet implemented or claimed:**

- an accepted official source snapshot;
- county/year completeness and flag profiling from real records;
- source-specific row-to-observation adapters;
- a published county-season target table;
- Parquet publication, dataset card, quality report, or Busia confirmation.

## Source paths and measured access state

| Source | Acquisition pattern | Measured state | Next action |
|---|---|---|---|
| KilimoSTAT crops | Parameterized JSON/data endpoint | Official schema, county coverage, monthly update policy, and CC BY-NC-SA 3.0 IGO portal terms are visible; valid maize request parameters still need resolution | Discover and freeze the exact domain/subdomain/element/item/year request, then acquire the first immutable response |
| FSD maize yield | Indicator `16` CSV endpoint | Download link resolves to indicator 16; page identifies tonnes per hectare and 2021; CSV retrieval times out in the available web environment and the header contract remains provisional | Inspect one valid response in a networked environment, freeze exact headers, then enable acquisition |
| FSD maize production | Indicator `277` CSV endpoint | Download link resolves to indicator 277; page identifies tonnes and 2022-2024; generic retrieval returns an anomalous error response | Inspect one valid response, freeze exact headers, then enable acquisition |
| FSD maize area | Indicator `133` CSV endpoint | Download link resolves to indicator 133; page identifies hectares and currently displays 2026; generic retrieval returns an anomalous error response | Inspect one valid response, verify period coverage, freeze exact headers, then enable acquisition |
| KNBS/NIPFN maize 2012-2020 | WordPress download manager | Landing metadata confirms one 67.13 KB file, 2012-2020 scope, and Kilimodata source; stable asset URL remains hidden | Resolve the asset request or use the manual verified-file path after the workbook schema is inspected |

All three FSD entries remain `network_acquisition_ready: false`. Discovering an endpoint is not equivalent to verifying its response schema.

## Canonical target gates

A source record can enter canonical observations only when:

1. its county resolves unambiguously against the 47-county registry;
2. crop and period identifiers are non-empty;
3. the element maps to production, harvested area, or reported yield;
4. original value and unit are retained;
5. the value is finite and non-negative;
6. the unit is explicitly supported and converted to `t`, `ha`, or `t/ha`;
7. source, flag, quality class, and snapshot ID are retained.

Derived yield additionally requires positive harvested area and the same county, crop, and period. Reported and derived yield remain separate; reconciliation never silently selects one.

## Publication gates

No source can enter the target table until:

1. original response bytes are preserved without mutation;
2. SHA-256, byte size, retrieval time, final URL, media type, and portable storage ID are recorded;
3. status, redirects, content type, payload shape, and expected schema pass;
4. source terms and redistribution state are explicit;
5. schema and row count are profiled;
6. original values, units, source names, and flags are retained;
7. duplicate target observations and ambiguous county mappings fail;
8. no credential, signed URL, local absolute path, restricted byte payload, or fabricated record enters Git.

## Verification receipt

Acquisition and manifest sub-slice:

```text
PYTHONPATH=src python -m pytest -q tests/test_source_manifest.py tests/test_acquisition.py tests/test_registry.py
18 passed before the endpoint-registry correction
```

Canonical target and corrected-registry sub-slice:

```text
PYTHONPATH=src python -m pytest -q tests/test_registry.py tests/test_target_observations.py
27 passed

python -m compileall -q src
exit 0

100-character line and excessive-blank-line scan
passed
```

A live FSD acquisition attempt failed before HTTP with temporary DNS resolution failure; no bytes or manifest were written. The available web fetcher also returned timeout or anomalous 400 responses for the three download URLs. These are environment/access findings, not accepted source evidence. The adapters remain fail-closed.
