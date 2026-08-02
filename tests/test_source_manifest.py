from datetime import UTC, datetime
from pathlib import Path

import pytest

from shamba_signal.datasets.manifest import SourceDefinition, build_snapshot_manifest


def make_source(**overrides: object) -> SourceDefinition:
    values: dict[str, object] = {
        "source_id": "fsd-maize-yield",
        "publisher": "Kenya Ministry of Agriculture and Livestock Development",
        "dataset_title": "Maize yield by county",
        "landing_url": "https://fsd.kilimo.go.ke/indicator",
        "acquisition_url": "https://fsd.kilimo.go.ke/api/example.csv",
        "acquisition_mode": "direct_csv",
        "access_method": "HTTPS CSV endpoint",
        "spatial_coverage": "Kenya admin level 1 counties",
        "temporal_coverage": "2022-2024",
        "terms_status": "review-required",
        "redistribution_status": "review-required",
        "expected_fields": ("county", "year", "yield"),
        "accepted_media_types": ("text/csv",),
        "network_acquisition_ready": True,
    }
    values.update(overrides)
    return SourceDefinition(**values)  # type: ignore[arg-type]


def test_build_snapshot_manifest_hashes_bytes_and_uses_portable_storage_uri(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "maize.csv"
    source_file.write_bytes(b"county,year,yield\nBusia,2020,2.1\n")

    manifest = build_snapshot_manifest(
        source=make_source(),
        file_path=source_file,
        retrieved_at=datetime(2026, 7, 30, 14, 0, tzinfo=UTC),
        http_status=200,
        media_type="text/csv; charset=utf-8",
        final_url="https://fsd.kilimo.go.ke/api/example.csv",
        schema_fingerprint="schema-123",
        storage_uri="snapshot://raw/fsd-maize-yield/abc.csv",
        transformation_revision="git:abc123",
    )

    assert manifest.byte_size == 33
    assert manifest.sha256 == (
        "91d6c9201a40ff8fbe16f0eed56c653cd77ca62f0a39b58d68f8847fa06e53b2"
    )
    assert manifest.storage_uri == "snapshot://raw/fsd-maize-yield/abc.csv"
    assert not manifest.storage_uri.startswith("file:")
    assert manifest.dataset_title == "Maize yield by county"


@pytest.mark.parametrize("field_name", ["source_id", "publisher", "dataset_title", "access_method"])
def test_source_definition_rejects_empty_required_text(field_name: str) -> None:
    with pytest.raises(ValueError, match=field_name):
        make_source(**{field_name: "   "})


def test_source_definition_rejects_non_https_acquisition_urls() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        make_source(acquisition_url="http://example.com/data.csv")


def test_manifest_rejects_local_absolute_storage_uri(tmp_path: Path) -> None:
    source_file = tmp_path / "maize.csv"
    source_file.write_text("county,year,yield\nBusia,2020,2.1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="portable"):
        build_snapshot_manifest(
            source=make_source(),
            file_path=source_file,
            retrieved_at=datetime.now(UTC),
            http_status=200,
            media_type="text/csv",
            final_url="https://fsd.kilimo.go.ke/api/example.csv",
            schema_fingerprint="schema-123",
            storage_uri=source_file.resolve().as_uri(),
            transformation_revision="git:abc123",
        )


def test_source_definition_rejects_signed_or_secret_urls() -> None:
    with pytest.raises(ValueError, match="signed query parameters"):
        make_source(acquisition_url="https://example.com/data.csv?token=secret")


def test_source_definition_rejects_unsupported_mode() -> None:
    with pytest.raises(ValueError, match="acquisition_mode"):
        make_source(acquisition_mode="ftp")
