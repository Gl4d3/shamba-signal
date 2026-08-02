# Slice 2 Target Dataset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible county × maize × season target dataset from official public records, preserve reported and derived yield semantics, and confirm Busia or switch to Trans Nzoia from measured evidence.

**Architecture:** Source-specific acquisition adapters write immutable raw bytes plus portable manifests. A canonicalization layer parses source-specific fields into typed observations, validates units and keys, separates reported from derived yield, produces a versioned target table, and publishes a quality report and dataset card. Any inaccessible, ambiguous, or licence-unclear source fails closed.

**Tech Stack:** Python 3.12+, standard library first, JSON/CSV, Parquet only through an explicitly locked implementation, pytest, Ruff.

## Global constraints

- Target grain remains county × crop × season.
- No source bytes are fabricated or silently transformed before manifesting.
- No credentials, cookies, bearer headers, signed URLs, or local absolute paths enter canonical manifests.
- Reported yield and derived yield remain distinguishable.
- Derived yield requires positive harvested area, compatible period/grain, and compatible units.
- Duplicate canonical keys, schema drift, invalid units, and ambiguous county mappings fail publication.
- Busia remains provisional until measured label continuity and observation gates pass.
- A rigorous no-go result is acceptable when public data is inaccessible or insufficient.

---

### Task 1: Source contracts and immutable manifests

**Files:**
- `data/sources/maize_sources.json`
- `src/shamba_signal/datasets/manifest.py`
- `src/shamba_signal/datasets/registry.py`
- `tests/test_source_manifest.py`
- `tests/test_registry.py`

- [x] Validate non-empty identifiers and metadata, HTTPS URLs, allowed acquisition modes, allowed terms states, timezone-aware retrieval, non-empty payloads, and accepted media types.
- [x] Store portable repository/object identifiers rather than local absolute file URIs.
- [x] Record dataset title, access method, spatial/temporal coverage, schema fingerprint, licence/redistribution decision, and transformation revision.
- [x] Reject embedded credentials and common token/signature query parameters from canonical URLs.

### Task 2: Acquisition and response validation

**Files:**
- `src/shamba_signal/datasets/acquisition.py`
- `scripts/acquire_source.py`
- `tests/test_acquisition.py`

- [x] Accept only expected status/media/schema combinations.
- [x] Preserve raw bytes before parsing.
- [x] Fail closed on HTML masquerading as CSV, empty payloads, redirects to landing pages, and unresolved download-manager pages.
- [x] Support a documented manual verified snapshot path when an official download manager does not expose a stable asset URL.
- [x] Use bounded timeout, explicit `Accept`, and a project-identifying user agent for live requests.
- [ ] Acquire and checksum the first accepted official snapshot from a networked environment.

### Task 3: Canonical observations and yield reconciliation

**Files:**
- `src/shamba_signal/datasets/target.py`
- `src/shamba_signal/datasets/adapters.py`
- `tests/test_target_observations.py`
- `tests/test_kilimostat_adapter.py`
- `tests/fixtures/county_profiles.json`
- `docs/data/target-observation-contract.md`

- [x] Canonicalize county code/name, crop, period, element, value, unit, source, flag, snapshot ID, and quality state.
- [x] Resolve county aliases against the existing 47-county registry and reject unknown or ambiguous mappings.
- [x] Preserve original fields, original units, and source flags.
- [x] Keep reported yield separate from derived yield and expose reconciliation status without silently selecting a target.
- [x] Derive tonnes per hectare only from positive, same-grain, period-compatible production and harvested-area observations.
- [x] Reject duplicate target-key/element observations rather than averaging or overwriting them.
- [x] Map the documented KilimoSTAT record fields into canonical observations with conservative flag handling.

### Task 4: Target dataset and quality decision

**Files:**
- `src/shamba_signal/datasets/target_build.py`
- `tests/test_target_build.py`
- Create deterministic publication command.
- Create versioned table, manifest, quality report, data dictionary, and dataset card.
- Create Busia-confirm/fallback decision record.

- [x] Enforce unique county/crop/period target keys and fail on duplicate elements.
- [x] Produce deterministic CSV/JSON renderers for target rows and quality metadata.
- [x] Report county/period coverage, missing labels, quality classes, source-flag counts, canonical units, duplicate policy, and reported-versus-derived counts.
- [x] Implement an explicit, configurable Busia → Trans Nzoia → insufficient-evidence gate without hidden threshold defaults.
- [ ] Run the pilot gate on accepted official records and confirm Busia, switch to Trans Nzoia, or publish an insufficiency result.
- [ ] Publish the versioned target table, manifest, quality report, data dictionary, and dataset card from accepted official snapshots.
- [ ] Ensure a clean regeneration matches committed publishable artifacts byte-for-byte or value-for-value as specified.

### Task 5: Integration and acceptance

- [ ] Extend repository validation with target-data contracts.
- [ ] Update platform status, README, roadmap, source register, and issue control surface truthfully.
- [ ] Run the full available local gate and record unavailable infrastructure checks separately.
- [ ] Resolve every review thread with evidence before merge.
