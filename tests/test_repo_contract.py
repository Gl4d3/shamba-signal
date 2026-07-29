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
