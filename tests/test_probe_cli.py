import json
import os
import subprocess
import sys
from pathlib import Path


def write_registry(tmp_path: Path) -> Path:
    path = tmp_path / "registry.json"
    path.write_text(
        json.dumps(
            {
                "registry_version": "0.1.0",
                "selected_crop": "maize",
                "target_grain": "county x crop x season",
                "sources": [
                    {
                        "source_id": "fsd-maize-yield",
                        "publisher": "Publisher",
                        "dataset_title": "Dataset",
                        "landing_url": "https://example.com/landing",
                        "acquisition_url": "https://example.com/data.csv",
                        "acquisition_mode": "direct_csv",
                        "access_method": "HTTPS CSV endpoint",
                        "spatial_coverage": "Kenya counties",
                        "temporal_coverage": "2021",
                        "terms_status": "review-required",
                        "redistribution_status": "review-required",
                        "expected_fields": ["county", "year", "yield"],
                        "accepted_media_types": ["text/csv"],
                        "network_acquisition_ready": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def run_probe(*args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = "src"
    return subprocess.run(
        [sys.executable, "scripts/probe_sources.py", *args],
        cwd=Path(__file__).parents[1],
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def test_probe_cli_writes_machine_readable_report(tmp_path: Path) -> None:
    registry = write_registry(tmp_path)
    output = tmp_path / "probe.json"

    result = run_probe("--registry", str(registry), "--output", str(output))

    assert result.returncode == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload[0]["source_id"] == "fsd-maize-yield"
    assert payload[0]["status"] == "not-ready"
    assert "body" not in payload[0]


def test_probe_cli_can_fail_when_all_sources_are_required_ready(tmp_path: Path) -> None:
    registry = write_registry(tmp_path)

    result = run_probe("--registry", str(registry), "--require-all-ready")

    assert result.returncode == 1
    assert '"status": "not-ready"' in result.stdout
