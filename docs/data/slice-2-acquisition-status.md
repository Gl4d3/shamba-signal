# Slice 2 Acquisition Status

## Active outcome

Slice 2A is complete: retain the accepted private annual county-year snapshot. Slice 2B is next: reconcile official annual source vintages and extend the annual panel before deciding county-year baseline feasibility.

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
- duplicate target-key/element rejection;
- deterministic target CSV and quality JSON renderers;
- quality reporting for county/period coverage, missingness, reported/derived yield, reconciliation, quality classes, source flags, canonical units, and duplicate policy;
- an explicit Busia → Trans Nzoia → insufficient-evidence pilot gate with caller-supplied thresholds;
- a machine-readable fallback audit that rejects KCHSP crop-sales data for yield and keeps KIHBS 2005-2006 as a separate research-only candidate;
- fixture coverage across acquisition, lineage, registry, probes, county aliases, units, grain matching, source adaptation, reconciliation, target rendering, pilot decisions, and fallback governance.

**Not yet implemented or claimed:**

- season mapping or a season-specific target table; county-season is evidence-insufficient and
  annual totals must not be crop-calendar disaggregated;
- KilimoSTAT and Food Systems Dashboard row adapters; both are off the critical path because no
  current verified response contract is accessible;
- source redistribution approval or Git publication of the source-derived rows;
- Parquet publication;
- a trained model, forecast, or production decision-support workflow.

## 2026-08-02 accepted KNBS/NIPFN snapshot

The original workbook was manually obtained from the official NIPFN landing page and retained only
outside Git. Its accepted snapshot identity is:

- source SHA-256: `15a47b6fdc634fab7a69cd7576974d2f9eeb550218389d4a1526dd8123a92ab8`;
- media type: XLSX;
- source sheet: the single tidy worksheet with `County`, `Year`, `Indicator`, and `Value`;
- verified data fields: `Area (HA)`, `Production (MT)`, and `Yield(MT/HA)`;
- observed coverage: 47 counties × 8 annual years × 3 indicators = 1,128 observations;
- observed years: 2012-2018 and 2020. The source title's 2012-2020 range is not continuous:
  2019 is absent.

The local-only annual build produces 376 county-year target rows. Reported and derived yield are
consistent for 373 rows, divergent for Mandera 2012, and unavailable as a derived value for two
zero-area rows (Nairobi 2020 and Wajir 2016). Both Busia and Trans Nzoia have all eight observed
annual years; the explicit policy requiring eight periods, complete yield coverage, no
review-required rows, and no divergent rows confirms **Busia**. This is an annual-label validation
decision only, not a seasonal continuity claim or model-readiness result.

## Source paths and historical access evidence

| Source | Acquisition pattern | Measured state | Next action |
|---|---|---|---|
| KilimoSTAT crops | Historical candidate endpoint | No current verified response contract is accessible | Off the critical path; do not use for Slice 2B reconciliation |
| FSD maize yield | Historical candidate endpoint | No current verified response contract is accessible | Off the critical path; do not use for Slice 2B reconciliation |
| FSD maize production | Historical candidate endpoint | No current verified response contract is accessible | Off the critical path; do not use for Slice 2B reconciliation |
| FSD maize area | Historical candidate endpoint | No current verified response contract is accessible | Off the critical path; do not use for Slice 2B reconciliation |
| KNBS/NIPFN maize 2012-2020 | WordPress download manager | Landing metadata confirms one 67.13 KB file, 2012-2020 scope, and Kilimodata source; stable asset URL remains hidden | Resolve the asset request or use the manual verified-file path after the workbook schema is inspected |

All three FSD entries remain `network_acquisition_ready: false`. Discovering an endpoint is not equivalent to verifying its response schema. The probe deliberately reports those sources as `not-ready` and does not make a request; the NIPFN download-manager entry reports `manual-required` until its file path is resolved.

## 2026-08-02 automated browser checkpoint (historical)

Before the manual workbook retrieval, the automated browser could not complete an official payload
download. This is retained as access evidence, not the current Slice 2 state.

| Source | Attempt | Observed result | Classification |
| --- | --- | --- | --- |
| KNBS/NIPFN maize 2012-2020 | Browser loaded the official landing page and resolved the download-manager asset in page state; browser-managed download then timed out. | Windows socket error `10060`; no file was created and the ephemeral asset URL was not recorded. | Manual file still required. |
| KilimoSTAT county crops | Browser opened the official crop-statistics landing URL. | Connection timed out before the first document loaded; no request parameters were guessed and no response body was received. | Unreachable from this environment. |
| FSD maize yield | Browser opened the official maize-yield indicator page. | Connection timed out before the first document loaded; production and area endpoints were not attempted because the same origin was unavailable. | Unreachable from this environment. |

### Recovery checklist

1. In a normal browser connection, download the KNBS/NIPFN **Maize Production by County 2012-2020** workbook from its official landing page.
2. Do not open, save, edit, rename, or convert the file after download. Place the original file outside the repository, for example under `D:\proj-d\side-projects\shamba-signal-private-snapshots\nipfn-maize-2012-2020\`.
3. Provide the exact local file path to the implementation worker. The worker will inspect the workbook before declaring actual verified fields or selecting the `.xls`/`.xlsx` media type.

This historical checkpoint predates the accepted workbook. It is retained as recovery evidence only: Busia and Trans Nzoia have since been evaluated against accepted annual records.

## Public fallback decisions

- **KCHSP 2020 Q1-Q2 Crop Output:** rejected for the yield target. Its official 20-field data dictionary covers crop sales and prices but exposes neither total production nor harvested area.
- **KIHBS 2005-2006 Agriculture:** research-only candidate. It exposes crop area, crop code, harvested quantity, and unit, but it is old household microdata with district-era geography, linkage/unit/weighting questions, and access constraints. It may not replace the current county-year target.

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
