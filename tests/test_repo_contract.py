from pathlib import Path


REQUIRED_FILES = [
    'README.md',
    'docs/product/PRD.md',
    'docs/product/MVP.md',
    'docs/architecture/ARCHITECTURE.md',
    'docs/roadmap/IMPLEMENTATION_SLICES.md',
    'docs/data/data-source-register.md',
    'docs/superpowers/specs/2026-07-29-shamba-signal-foundation-design.md',
    'docs/superpowers/plans/2026-07-29-shamba-signal-foundation.md',
    '.github/workflows/ci.yml',
    '.github/ISSUE_TEMPLATE/implementation-slice.yml',
]


def test_repository_contains_foundation_artifacts() -> None:
    missing = [path for path in REQUIRED_FILES if not Path(path).is_file()]
    assert missing == []


def test_ci_uses_official_github_python_actions() -> None:
    workflow = Path('.github/workflows/ci.yml').read_text()
    assert 'actions/checkout@v6' in workflow
    assert 'actions/setup-python@v6' in workflow
    assert 'astral-sh/setup-uv' not in workflow
