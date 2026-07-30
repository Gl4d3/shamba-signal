# Slice 2 County-Season Target Dataset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible, versioned maize county-season target dataset and confirm Busia or switch to Trans Nzoia through downloaded-data evidence.

**Architecture:** Source-specific acquisition adapters write immutable raw files and normalized source manifests. A canonicalization layer preserves original columns while producing county, crop, year/season, element, value, unit, source, flag, and derivation fields. Quality gates publish a dataset only after uniqueness, unit, reconciliation, completeness, and pilot-overlap checks pass.

**Tech Stack:** Python 3.12+, standard library acquisition/manifest code, pandas/pyarrow for transformation, pytest, Parquet.

## Global Constraints

- The target grain is county × crop × season.
- Raw snapshots are immutable and content-addressed by SHA-256.
- Original value, unit, source, and flag fields are never discarded.
- Reported yield and derived yield remain distinguishable.
- Duplicate target keys, invalid units, and schema drift fail publication.
- Busia is confirmed only after label completeness and spatial-overlap gates; Trans Nzoia is the fallback.
- No source data is committed when redistribution terms do not permit it.

---

### Task 1: Source snapshot contract

**Files:**
- Create: `src/shamba_signal/datasets/manifest.py`
- Create: `data/sources/maize_sources.json`
- Test: `tests/test_source_manifest.py`

**Produces:** deterministic SHA-256 manifests carrying source ID, publisher, URL, retrieval time, media type, byte size, checksum, terms status, and local storage URI.

### Task 2: Acquisition adapters

**Files:**
- Create: `src/shamba_signal/datasets/acquisition.py`
- Create: `scripts/acquire_maize_sources.py`
- Test: `tests/test_source_acquisition.py`

**Produces:** adapters for direct CSV/JSON sources and an explicit manual-resolution state for download-manager pages that do not expose a stable asset URL.

### Task 3: Canonical maize record schema

**Files:**
- Create: `src/shamba_signal/datasets/maize_targets.py`
- Create: `tests/fixtures/maize_source_rows.csv`
- Test: `tests/test_maize_targets.py`

**Produces:** typed county/crop/season records with reported/derived yield provenance and stable unit normalization.

### Task 4: Quality profile and pilot confirmation

**Files:**
- Create: `src/shamba_signal/datasets/quality.py`
- Create: `scripts/build_maize_targets.py`
- Create: `docs/data/maize-target-quality-report.md`
- Create: `data/targets/maize_county_season.parquet`
- Create: `data/targets/maize_county_season.dataset.json`
- Test: `tests/test_target_quality.py`

**Produces:** completeness, uniqueness, flag, reconciliation, and county coverage evidence plus a signed Busia/Trans Nzoia decision.

### Task 5: Repository integration

- Update the API status, README, roadmap, validator, and issue #3.
- Run the full test suite, acquisition fixture tests, deterministic rebuild, repository validation, and compilation.
- Open a stacked PR against `slice/1-data-feasibility`.
