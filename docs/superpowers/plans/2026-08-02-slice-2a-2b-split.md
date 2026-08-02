# Slice 2A / 2B Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the completed KNBS/NIPFN annual snapshot work as Slice 2A, publish the evidence-insufficiency decision for county-season labels, and make official annual-source reconciliation the explicit Slice 2B gate before modelling.

**Architecture:** Slice 2A remains a deterministic, source-bound local package and is not renamed into a model-ready dataset. Slice 2B owns source-vintage reconciliation, annual-panel extension, and the formal target-grain decision. The platform status, roadmap, validation rules, issue tracker, and PR must all describe the same boundary.

**Tech Stack:** Python 3.12, FastAPI/Pydantic, JSON and Markdown evidence artifacts, Pytest, Ruff, GitHub CLI, agent-browser.

## Global Constraints

- Do not infer season labels from annual totals or crop calendars.
- Do not commit source PDFs, workbooks, or row-level derived data while redistribution is unresolved.
- Keep KilimoSTAT and Food Systems Dashboard out of the critical path until a real response contract is verified.
- Treat the KNBS 2024 National Agriculture Production Report as a candidate revision source, not an accepted append, until its 2020 overlap is reconciled.
- No model, satellite, AWS, Druid, or advisory work starts before Slice 2B closes.
- Keep all changes on `slice/2-target-dataset`; do not create a `CODEX/` branch.

---

### Task 1: Encode the Slice 2A / 2B contract

**Files:**
- Create: `data/sources/slice2b_source_audit.json`
- Create: `docs/data/slice-2b-forecast-readiness-decision.md`
- Modify: `docs/roadmap/IMPLEMENTATION_SLICES.md`
- Modify: `docs/data/slice-2-acquisition-status.md`
- Modify: `docs/data/target-observation-contract.md`
- Modify: `README.md`
- Modify: `memory.md`
- Modify: `scripts/validate_slice2.py`
- Modify: `tests/test_slice2_validator.py`

**Interfaces:**
- Consumes: accepted NIPFN snapshot digest `15a47b6fdc634fab7a69cd7576974d2f9eeb550218389d4a1526dd8123a92ab8` and candidate KNBS report digest `7d86dc4cbfa1d0b5204e2428fb8d84c3bada0fc1775bf0b7d557dfebcc4d70eb`.
- Produces: a machine-readable source audit and repository validation requirements for the split.

- [x] **Step 1: Write failing validator tests**

  Require the Slice 2B audit and decision document, the new roadmap headings, and removal of live statements that acquisition is still blocked or that Busia has never been evaluated.

- [x] **Step 2: Run the focused tests and confirm failure**

  Run: `uv run pytest -q tests/test_slice2_validator.py --basetemp .pytest-tmp`

- [x] **Step 3: Add the evidence artifacts and align documentation**

  Record that the direct KNBS report is 12,398,810 bytes, covers annual county area and production for 2019-2023, is marked provisional for 2023, and differs materially from the accepted workbook in 24 of 47 overlapping 2020 county rows under a 0.1 percent comparison threshold. Record Busia as matching within rounding and Trans Nzoia as materially divergent. Choose county-year as the supported target grain and publish county-season as evidence-insufficient.

- [x] **Step 4: Strengthen repository validation**

  Make `validate_slice2.py` fail if the audit/decision files disappear or the roadmap regresses to the pre-split boundary.

- [x] **Step 5: Run focused tests**

  Run: `uv run pytest -q tests/test_slice2_validator.py --basetemp .pytest-tmp`

- [x] **Step 6: Commit**

  Commit message: `docs: split annual target from forecast readiness`

### Task 2: Make the product status tell the same truth

**Files:**
- Modify: `src/shamba_signal/services/platform_status.py`
- Modify: `src/shamba_signal/web/index.html`
- Modify: `src/shamba_signal/web/static/app.js`
- Modify: `tests/test_platform_status.py`
- Modify: `tests/test_home.py`
- Modify: `memory.md`

**Interfaces:**
- Consumes: the Slice 2A / 2B decision from Task 1.
- Produces: release `slice-2a-annual-snapshot-v1`, a ready Slice 2A capability, a next Slice 2B reconciliation capability, and planned county-year baseline modelling.

- [x] **Step 1: Write failing API and homepage tests**

  Assert that the public status distinguishes source-bound annual readiness from model readiness, exposes reconciliation as next, and no longer claims county-season forecasting as the validated primary output.

- [x] **Step 2: Run focused tests and confirm failure**

  Run: `uv run pytest -q tests/test_platform_status.py tests/test_home.py --basetemp .pytest-tmp`

- [x] **Step 3: Implement the minimal truthful status update**

  Keep the accepted annual package ready, add Slice 2B as next, state that official source vintages conflict, and make county-year baseline feasibility the planned modelling outcome. Do not claim a resolved source precedence policy.

- [x] **Step 4: Run focused tests**

  Run: `uv run pytest -q tests/test_platform_status.py tests/test_home.py --basetemp .pytest-tmp`

- [x] **Step 5: Commit**

  Commit message: `feat: expose annual label reconciliation gate`

### Task 3: Verify and publish the split

**Files:**
- Create: `docs/assets/slice-2-target-dataset/slice-2a-2b-status.png`
- Rename: `docs/assets/slice-2-target-dataset/acquisition-blocked-status.png` to `docs/assets/slice-2-target-dataset/historical-acquisition-blocked-status.png`
- Modify: GitHub PR #14 and issues #3, #4, and #11.

**Interfaces:**
- Consumes: the green repository from Tasks 1 and 2.
- Produces: fresh visual evidence and aligned remote delivery state.

- [x] **Step 1: Run full local verification**

  Run the full Pytest suite, Ruff, repository validator, Slice 2 validator, compilation, API smoke, and `git diff --check`.

- [x] **Step 2: Verify the homepage in a real browser**

  Use agent-browser at desktop and mobile widths. Confirm the annual snapshot is ready, reconciliation is next, county-year modelling is planned, and no console errors occur.

- [x] **Step 3: Capture current evidence**

  Replace the historical blocker screenshot with a current, descriptive screenshot and ensure documentation calls the previous capture historical rather than current proof.

- [x] **Step 4: Commit visual proof**

  Commit message: `docs: refresh Slice 2 delivery proof`

- [x] **Step 5: Push and align GitHub**

  Push `slice/2-target-dataset`, retitle and update PR #14 for Slice 2A, update issue #3 as Slice 2A, create a Slice 2B issue, make issue #4 depend on Slice 2B, and update issue #11. Do not merge the PR.

- [x] **Step 6: Verify remote state**

  Confirm the pushed head SHA, PR contents, issue links, and current CI status.
