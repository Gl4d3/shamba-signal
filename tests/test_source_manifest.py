from datetime import datetime, timezone
from pathlib import Path

import pytest

from shamba_signal.datasets.manifest import SourceDefinition, build_snapshot_manifest


def test_build_snapshot_manifest_hashes_bytes_and_preserves_source_contract(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "maize.csv"
    source_file.write_bytes(b"county,year,yield\nBusia,2020,2.1\n")
    source = SourceDefinition(
        source_id="fsd-maize-yield",
        publisher="Kenya Ministry of Agriculture and Livestock Development",
        landing_url="https://fsd.kilimo.go.ke/indicator",
        acquisition_url="https://fsd.kilimo.go.ke/api/example.csv",
        acquisition_mode="direct_csv",
        terms_status="review-required",
    )

    manifest = build_snapshot_manifest(
        source=source,
        file_path=source_file,
        retrieved_at=datetime(2026, 7, 30, 14, 0, tzinfo=timezone.utc),
        media_type="text/csv",
    )

    assert manifest.source_id == "fsd-maize-yield"
    assert manifest.byte_size == 33
    assert manifest.sha256 == (
        "91d6c9201a40ff8fbe16f0eed56c653cd77ca62f0a39b58d68f8847fa06e53b2"
    )
    assert manifest.retrieved_at == "2026-07-30T14:00:00+00:00"
    assert manifest.storage_uri.endswith("maize.csv")
    assert manifest.terms_status == "review-required"


def test_source_definition_rejects_non_https_acquisition_urls() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        SourceDefinition(
            source_id="bad",
            publisher="Example",
            landing_url="https://example.com",
            acquisition_url="http://example.com/data.csv",
            acquisition_mode="direct_csv",
            terms_status="verified",
        )
