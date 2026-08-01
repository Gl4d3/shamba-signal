# Slice 1 Data Feasibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Select one defensible MVP crop and one deep-dive county from public-data evidence using a reproducible scoring pipeline.

**Architecture:** A standard-library Python feasibility package loads a versioned evidence catalogue and candidate profiles, validates the approved score contract, calculates weighted scores, runs sensitivity analysis, and writes machine-readable plus human-readable selection artifacts. Data acquisition remains source-adapter work for Slice 2; Slice 1 records access, licensing, coverage, and evidence quality without redistributing restricted data.

**Tech Stack:** Python 3.12+, JSON, CSV, pytest, Ruff.

## Global Constraints

- The validated forecast grain remains county × crop × season.
- One crop and one pilot county are selected by evidence, not hard-coded product preference.
- Approved weights are 35/20/15/10/10/10 for label quality, historical depth, spatial resolution, satellite usability, licensing, and access stability.
- Scores must be traceable to cited evidence records.
- Weight totals must equal 100.
- Sensitivity analysis must show whether plausible weight changes change the winner.
- No restricted or license-unclear source data may be redistributed.

---

### Task 1: Feasibility domain and score contract

**Files:**
- Create: `src/shamba_signal/feasibility/models.py`
- Create: `src/shamba_signal/feasibility/scoring.py`
- Test: `tests/test_feasibility_scoring.py`

**Interfaces:**
- Produces: `CandidateProfile`, `ScoreWeights`, `score_candidate()`, `rank_candidates()`, and `run_sensitivity_analysis()`.

- [ ] Write failing tests for weight validation, weighted score calculation, deterministic ranking, and sensitivity winner stability.
- [ ] Run the focused tests and confirm they fail because the package is absent.
- [ ] Implement the smallest domain and scoring code that passes.
- [ ] Run the focused tests and full suite.

### Task 2: Versioned evidence and candidate profiles

**Files:**
- Create: `data/feasibility/evidence.json`
- Create: `data/feasibility/candidate_profiles.json`
- Modify: `data/catalog/datasets.yaml`
- Test: `tests/test_feasibility_catalog.py`

**Interfaces:**
- Consumes: score dimensions and identifiers from Task 1.
- Produces: evidence-backed crop and county candidate inputs.

- [ ] Write failing tests for evidence references, 100-point dimension coverage, candidate uniqueness, and score bounds.
- [ ] Add official/public source evidence for yield labels, calendars, crop masks, satellite, rainfall, soil, and boundaries.
- [ ] Add crop candidates and county candidates with explicit evidence references and limitations.
- [ ] Run focused and full tests.

### Task 3: Reproducible selection command and artifacts

**Files:**
- Create: `src/shamba_signal/feasibility/report.py`
- Create: `scripts/run_feasibility.py`
- Create: `data/feasibility/scorecard.csv`
- Create: `data/feasibility/selection.json`
- Create: `docs/data/pilot-selection-decision.md`
- Test: `tests/test_feasibility_report.py`

**Interfaces:**
- Consumes: candidate profiles and score functions.
- Produces: stable CSV/JSON/Markdown outputs and exit code 0 when validation succeeds.

- [ ] Write a failing end-to-end test that runs the command against fixtures and checks the selected crop, county, totals, and sensitivity result.
- [ ] Implement deterministic artifact generation.
- [ ] Generate and commit the scorecard, selection record, and decision report.
- [ ] Run the command twice and verify byte-stable outputs.

### Task 4: Repository integration and review

**Files:**
- Modify: `README.md`
- Modify: `Makefile`
- Modify: `scripts/validate_repo.py`
- Modify: `docs/roadmap/IMPLEMENTATION_SLICES.md`

- [ ] Add the feasibility command to the developer workflow.
- [ ] Require the Slice 1 artifacts in repository validation.
- [ ] Document selection status and scientific caveats.
- [ ] Run Ruff, pytest, repository validation, compilation, and the feasibility command.
- [ ] Open a Slice 1 pull request linked to issue #2.
