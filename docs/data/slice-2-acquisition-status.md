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
- non-persisting source probe with machine-readable `ready`, `blocked`, `not-ready`, `manual-required`, `unreachable`, and `invalid-response` states;
- manual verified-file path for official download managers that do not expose a stable asset URL;
- canonical county/crop/period observations with original values, units, flags, quality class, and snapshot lineage;
- approved unit conversion for tonnes, kilograms, hectares, acres, and yield units;
- safe derived-yield and reported-versus-derived reconciliation contracts;
- KilimoSTAT documented-field adapter with conservative source-flag handling;
- duplicate target-key/element rejection;
- deterministic target CSV and quality JSON renderers;
- quality reporting for county/period coverage, missingness, reported/derived yield, reconciliation, quality classes, source flags, canonical units, and duplicate policy;
- an explicit Busia → Trans Nzoia → insufficient-evidence pilot gate with caller-supplied thresholds;
- a machine-readable fallback audit that rejects KCHSP crop-sales data for yield and keeps KIHBS 2005-2006 as a separate research-only candidate;
- fixture coverage across acquisition, lineage, registry, probes, county aliases, units, grain matching, source adaptation, reconciliation, target rendering, pilot decisions, and fallback governance.

**Not yet implemented or claimed:**

- an accepted official source snapshot;
- county/year completeness and flag profiling from real records;
- Food Systems Dashboard and KNBS workbook row adapters;
- a published county-season target table;
- Parquet publication, dataset card, real-data quality report, or Busia confirmation.

## Source paths and measured access state

| Source | Acquisition pattern | Measured state | Next action |
|---|---|---|---|
| KilimoSTAT crops | Parameterized JSON/data endpoint | Official schema, county coverage, monthly update policy, and CC BY-NC-SA 3.0 IGO portal terms are visible; valid maize request parameters still need resolution | Discover and freeze the exact domain/subdomain/element/item/year request, then acquire the first immutable response |
| FSD maize yield | Indicator `16` CSV endpoint | Download link resolves to indicator 16; page identifies tonnes per hectare and 2021; CSV retrieval times out in the available web environment and the header contract remains provisional | Run `make probe-sources` from a networked environment after the schema is inspected and explicitly enabled |
| FSD maize production | Indicator `277` CSV endpoint | Download link resolves to indicator 277; page identifies tonnes and 2022-2024; generic retrieval returns an anomalous error response | Inspect one valid response, freeze exact headers, enable the source, then probe and acquire |
| FSD maize area | Indicator `133` CSV endpoint | Download link resolves to indicator 133; page identifies hectares and currently displays 2026; generic retrieval returns an anomalous error response | Inspect one valid response, verify period coverage, freeze exact headers, enable the source, then probe and acquire |
| KNBS/NIPFN maize 2012-2020 | WordPress download manager | Landing metadata confirms one 67.13 KB file, 2012-2020 scope, and Kilimodata source; stable asset URL remains hidden | Resolve the asset request or use the manual verified-file path after the workbook schema is inspected |

All three FSD entries remain `network_acquisition_ready: false`. Discovering an endpoint is not equivalent to verifying its response schema. The probe deliberately reports those sources as `not-ready` and does not make a request; the NIPFN download-manager entry reports `manual-required` until its file path is resolved.

## 2026-08-02 live acquisition checkpoint

No official payload was accepted, persisted, or added to Git during this checkpoint.

| Source | Attempt | Observed result | Classification |
| --- | --- | --- | --- |
| KNBS/NIPFN maize 2012-2020 | Browser loaded the official landing page and resolved the download-manager asset in page state; browser-managed download then timed out. | Windows socket error `10060`; no file was created and the ephemeral asset URL was not recorded. | Manual file still required. |
| KilimoSTAT county crops | Browser opened the official crop-statistics landing URL. | Connection timed out before the first document loaded; no request parameters were guessed and no response body was received. | Unreachable from this environment. |
| FSD maize yield | Browser opened the official maize-yield indicator page. | Connection timed out before the first document loaded; production and area endpoints were not attempted because the same origin was unavailable. | Unreachable from this environment. |

### Recovery checklist

1. In a normal browser connection, download the KNBS/NIPFN **Maize Production by County 2012-2020** workbook from its official landing page.
2. Do not open, save, edit, rename, or convert the file after download. Place the original file outside the repository, for example under `D:\proj-d\side-projects\shamba-signal-private-snapshots\nipfn-maize-2012-2020\`.
3. Provide the exact local file path to the implementation worker. The worker will inspect the workbook before declaring actual verified fields or selecting the `.xls`/`.xlsx` media type.
4. If the KNBS workbook cannot be obtained, provide a successful KilimoSTAT browser request with its visible county, item, element, year, and download parameters. Do not provide cookies, bearer tokens, signed URLs, or credentials.

This checkpoint is an acquisition blocker, not an evidence-insufficiency pilot decision: Busia and Trans Nzoia have not been evaluated against real records.

## Public fallback decisions

- **KCHSP 2020 Q1-Q2 Crop Output:** rejected for the yield target. Its official 20-field data dictionary covers crop sales and prices but exposes neither total production nor harvested area.
- **KIHBS 2005-2006 Agriculture:** research-only candidate. It exposes crop area, crop code, harvested quantity, and unit, but it is old household microdata with district-era geography, linkage/unit/weighting questions, and access constraints. It may not replace the current county-season target.

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
8. the pilot gate is run on accepted records using versioned thresholds;
9. no credential, signed URL, local absolute path, restricted byte payload, or fabricated record enters Git.

## Verification receipt

The exact Slice 2 code/test surface was reconstructed from the branch files and verified locally:

```text
PYTHONPATH=src /opt/pyvenv/bin/python -m pytest -q \
  tests/test_source_manifest.py \
  tests/test_acquisition.py \
  tests/test_registry.py \
  tests/test_target_observations.py \
  tests/test_kilimostat_adapter.py \
  tests/test_target_build.py \
  tests/test_probe.py \
  tests/test_probe_cli.py \
  tests/test_fallback_candidates.py
.....................................................................    [100%]
69 passed

PYTHONPATH=src /opt/pyvenv/bin/python -m compileall -q src scripts
exit 0

100-character line scan
passed
```

The source probe tests prove that response bodies are never returned or persisted by the diagnostic path. The target builder is deterministic under reordered fixture observations, and the pilot gate exercises primary-confirmed, fallback-selected, and insufficient-evidence outcomes.

The original focused verification receipt above is historical branch evidence. The current Windows checkpoint ran the complete local suite with a workspace-local Pytest temp directory after restoring the lock and import contracts; the 2026-08-02 live acquisition results are recorded separately above. No bytes or manifests were written. The adapters remain fail-closed.
