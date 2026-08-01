import subprocess
import sys


def test_repository_validator_runs_successfully() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_repo.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Repository contract valid"
