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
- fixture coverage for accepted CSV, malformed responses, portable lineage, duplicate registry IDs, and manually verified opaque files.

**Not yet implemented or claimed:**

- an accepted official source snapshot;
- county/year completeness and flag profiling;
- canonical county-season observations;
- reported-versus-derived yield reconciliation;
- Parquet publication, dataset card, quality report, or Busia confirmation.

## Source paths and measured access state

| Source | Acquisition pattern | Measured state | Next action |
|---|---|---|---|
| KilimoSTAT crops | Parameterized JSON/data endpoint | Official schema, county coverage, monthly update policy, and CC BY-NC-SA 3.0 IGO portal terms are visible; valid maize request parameters still need resolution | Discover and freeze the exact domain/subdomain/element/item/year request, then acquire the first immutable response |
| Kenya Food Systems Dashboard maize yield | Direct indicator CSV endpoint | Indicator 278 and its 2022-2024 county yield page are visible; the endpoint returns inconsistent behavior to generic clients and must pass the adapter before acceptance | Retry through the implemented adapter from a networked environment and accept only a validated CSV snapshot |
| KNBS/NIPFN maize 2012-2020 | WordPress download manager | Landing metadata confirms one 67.13 KB file, 2012-2020 scope, and Kilimodata source; stable asset URL remains hidden | Resolve the asset request or use the manual verified-file path with explicit media type and verified field list |

## Publication gates

No source can enter the target table until:

1. original response bytes are preserved without mutation;
2. SHA-256, byte size, retrieval time, final URL, media type, and portable storage ID are recorded;
3. status, redirects, content type, payload shape, and expected schema pass;
4. source terms and redistribution state are explicit;
5. schema and row count are profiled;
6. original values, units, source names, and flags are retained;
7. no credential, signed URL, local absolute path, restricted byte payload, or fabricated record enters Git.

## Verification receipt

Focused local verification for this sub-slice:

```text
PYTHONPATH=src python -m pytest -q tests/test_source_manifest.py tests/test_acquisition.py tests/test_registry.py
18 passed

python -m compileall -q src scripts
exit 0

100-character line scan
passed

manual verified CSV smoke
snapshot and manifest created with portable snapshot:// storage URI

live FSD acquisition attempt
failed before HTTP with temporary DNS resolution failure; no bytes or manifest were written
```

The DNS failure is an execution-environment limitation, not accepted source evidence. The adapter remains fail-closed.
