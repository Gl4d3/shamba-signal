import subprocess
from pathlib import Path

REQUIRED_FILES = (
    "README.md",
    "docs/product/PRD.md",
    "docs/product/MVP.md",
    "docs/architecture/ARCHITECTURE.md",
    "docs/roadmap/IMPLEMENTATION_SLICES.md",
    "docs/data/data-source-register.md",
    "docs/superpowers/specs/2026-07-29-shamba-signal-foundation-design.md",
    "docs/superpowers/plans/2026-07-29-shamba-signal-foundation.md",
    ".github/workflows/ci.yml",
    ".github/ISSUE_TEMPLATE/implementation-slice.yml",
)


def test_repository_contains_foundation_artifacts() -> None:
    assert [path for path in REQUIRED_FILES if not Path(path).is_file()] == []


def test_ci_is_locked_read_only_and_hardened() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text()
    assert "cancel-in-progress: true" in workflow
    assert "persist-credentials: false" in workflow
    assert "uv sync --locked --extra dev" in workflow
    assert "permissions:\n  contents: read" in workflow
    for uses_line in [line.strip() for line in workflow.splitlines() if "uses:" in line]:
        reference = uses_line.split("@", maxsplit=1)[1].split()[0]
        assert len(reference) == 40
        assert all(character in "0123456789abcdef" for character in reference)


def test_environment_variants_are_ignored_but_example_is_retained() -> None:
    lines = Path(".gitignore").read_text().splitlines()
    assert ".env" in lines
    assert ".env.*" in lines
    assert "!.env.example" in lines
    assert lines.index(".env.*") < lines.index("!.env.example")

    ignored = subprocess.run(
        ["git", "check-ignore", "--no-index", "--quiet", ".env.local"],
        check=False,
    )
    example = subprocess.run(
        ["git", "check-ignore", "--no-index", "--quiet", ".env.example"],
        check=False,
    )
    assert ignored.returncode == 0
    assert example.returncode == 1
