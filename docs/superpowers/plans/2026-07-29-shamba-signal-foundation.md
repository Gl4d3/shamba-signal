# Shamba Signal Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a runnable, tested repository foundation that locks the approved Shamba Signal product, architecture, MVP, data-selection rules, and slice backlog.

**Architecture:** A dependency-light FastAPI modular monolith serves a public foundation page and stable platform contract. Domain and service packages preserve boundaries for future pipeline and forecast workers, while documentation defines local-first storage and a later AWS migration.

**Tech Stack:** Python 3.12+, FastAPI, Pydantic v2, Jinja/static HTML, pytest, Ruff, GitHub Actions, Parquet/PostgreSQL/S3-compatible interfaces documented for later slices.

## Global Constraints

- Validated analytical output is county-season yield, never inferred farm-level yield.
- MVP forecast timing is mid-season.
- One crop and one pilot county are selected through data feasibility, not hard-coded.
- Both scheduled and analyst-triggered forecast modes remain in scope.
- Advisory actions must come from approved expert playbooks.
- AWS migration follows working product slices.
- Every implementation slice ends in a testable artifact.

---

### Task 1: Repository and documentation contract

**Files:**
- Create: `README.md`
- Create: `docs/product/PRD.md`
- Create: `docs/product/MVP.md`
- Create: `docs/architecture/ARCHITECTURE.md`
- Create: `docs/roadmap/IMPLEMENTATION_SLICES.md`
- Create: `docs/data/data-source-register.md`
- Test: `tests/test_repo_contract.py`

**Interfaces:**
- Consumes: approved product decisions from the design spec.
- Produces: stable document paths used by CI, contributors, and later slice issues.

- [ ] **Step 1: Write the failing repository-contract test**

```python
from pathlib import Path


def test_repository_contains_foundation_artifacts() -> None:
    required = ["README.md", "docs/product/PRD.md", "docs/product/MVP.md"]
    assert [path for path in required if not Path(path).is_file()] == []
```

- [ ] **Step 2: Run the test and verify missing-file failure**

Run: `PYTHONPATH=src pytest tests/test_repo_contract.py -q`  
Expected: FAIL listing missing foundation files.

- [ ] **Step 3: Write the approved documents and repository metadata**

Use the exact product output, forecast timing, pilot-selection policy, advisory boundary, and AWS order from Global Constraints.

- [ ] **Step 4: Run the contract test**

Run: `PYTHONPATH=src pytest tests/test_repo_contract.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add README.md docs tests/test_repo_contract.py
git commit -m "docs: define Shamba Signal product foundation"
```

### Task 2: Product status domain contract

**Files:**
- Create: `src/shamba_signal/domain/platform.py`
- Create: `src/shamba_signal/services/platform_status.py`
- Test: `tests/test_platform_status.py`

**Interfaces:**
- Produces: `get_platform_status() -> PlatformStatus`.
- Consumers: HTTP API and foundation web page.

- [ ] **Step 1: Write the failing status-contract tests**

Assert product name, architecture, county-season output, mid-season timing, refresh modes, and the exact capability IDs.

- [ ] **Step 2: Verify RED**

Run: `PYTHONPATH=src pytest tests/test_platform_status.py -q`  
Expected: import failure because the domain/service does not exist.

- [ ] **Step 3: Implement immutable Pydantic contracts and the status service**

Expose capability states `ready`, `next`, and `planned`; mark only data feasibility as `next` in the foundation release.

- [ ] **Step 4: Verify GREEN**

Run: `PYTHONPATH=src pytest tests/test_platform_status.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/shamba_signal/domain src/shamba_signal/services tests/test_platform_status.py
git commit -m "feat: add platform status contract"
```

### Task 3: FastAPI health and platform endpoints

**Files:**
- Create: `src/shamba_signal/api/app.py`
- Create: `src/shamba_signal/cli.py`
- Test: `tests/test_health.py`
- Test: `tests/test_platform_status.py`

**Interfaces:**
- Produces: `create_app() -> FastAPI`, `GET /healthz`, `GET /api/v1/platform/status`.
- Consumes: `get_platform_status()`.

- [ ] **Step 1: Write the failing health endpoint test**

Assert status 200 and exact JSON `{status, service, release}`.

- [ ] **Step 2: Verify RED**

Run: `PYTHONPATH=src pytest tests/test_health.py -q`  
Expected: import or route failure.

- [ ] **Step 3: Implement the application factory and CLI**

Keep endpoint functions deterministic and external-dependency-free.

- [ ] **Step 4: Verify GREEN**

Run: `PYTHONPATH=src pytest tests/test_health.py tests/test_platform_status.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/shamba_signal/api src/shamba_signal/cli.py tests
git commit -m "feat: expose foundation API contracts"
```

### Task 4: Public foundation page

**Files:**
- Create: `src/shamba_signal/web/index.html`
- Create: `src/shamba_signal/web/static/styles.css`
- Create: `src/shamba_signal/web/static/app.js`
- Modify: `src/shamba_signal/api/app.py`
- Test: `tests/test_home.py`

**Interfaces:**
- Produces: `GET /` and `/static/*`.
- Consumes: `/api/v1/platform/status` from browser JavaScript.

- [ ] **Step 1: Write the failing page-boundary test**

Assert the page contains Shamba Signal, County-season yield forecasting, Relative yield potential, and the explicit farm-level non-claim.

- [ ] **Step 2: Verify RED**

Run: `PYTHONPATH=src pytest tests/test_home.py -q`  
Expected: 404 or missing-copy failure.

- [ ] **Step 3: Implement semantic HTML, responsive CSS, and status loading**

The visual design must be readable, restrained, keyboard-friendly, and avoid generic dashboard chrome before data exists.

- [ ] **Step 4: Verify GREEN**

Run: `PYTHONPATH=src pytest tests/test_home.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/shamba_signal/web src/shamba_signal/api/app.py tests/test_home.py
git commit -m "feat: add public foundation experience"
```

### Task 5: Data catalogue and validation

**Files:**
- Create: `data/catalog/datasets.yaml`
- Create: `scripts/validate_repo.py`
- Test: `tests/test_data_catalog.py`

**Interfaces:**
- Produces: machine-readable selection weights and candidate source metadata.
- Consumers: Slice 1 profiling and CI repository validation.

- [ ] **Step 1: Write the failing catalogue test**

Assert weights total 100, yield-label quality is 35, required source IDs exist, URLs use HTTPS, and every source has an explicit licence state.

- [ ] **Step 2: Verify RED**

Run: `PYTHONPATH=src pytest tests/test_data_catalog.py -q`  
Expected: missing-file failure.

- [ ] **Step 3: Add the catalogue and validator**

Use JSON syntax inside `.yaml` so standard-library validation remains dependency-free while preserving YAML compatibility.

- [ ] **Step 4: Verify GREEN**

Run: `PYTHONPATH=src pytest tests/test_data_catalog.py -q && PYTHONPATH=src python scripts/validate_repo.py`  
Expected: PASS and `Repository contract valid`.

- [ ] **Step 5: Commit**

```bash
git add data/catalog scripts tests/test_data_catalog.py
git commit -m "feat: add data feasibility catalogue"
```

### Task 6: CI and GitHub delivery workflow

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/ISSUE_TEMPLATE/implementation-slice.yml`
- Create: `.github/ISSUE_TEMPLATE/research-evidence.yml`
- Create: `.github/pull_request_template.md`
- Create: `.editorconfig`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `Makefile`

**Interfaces:**
- Produces: repeatable verification command and structured issue inputs.
- Consumers: GitHub Actions, contributors, and agentic implementation slices.

- [ ] **Step 1: Extend repository-contract tests with CI and issue-form paths**

- [ ] **Step 2: Verify RED before creating the files**

Run: `PYTHONPATH=src pytest tests/test_repo_contract.py -q`  
Expected: missing CI or issue form.

- [ ] **Step 3: Add CI, templates, and commands**

CI runs dependency installation, Ruff, pytest, repository validation, and Python compilation on Python 3.12.

- [ ] **Step 4: Run the full verification gate**

Run: `make verify`  
Expected: all tests pass, repository contract valid, compilation exits 0.

- [ ] **Step 5: Publish and create slice backlog**

Publish the verified tree to `Gl4d3/shamba-signal`, then create one GitHub issue per Slice 1–9 with acceptance criteria copied from the roadmap.
