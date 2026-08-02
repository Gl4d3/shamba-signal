from datetime import UTC, datetime
from pathlib import Path

import pytest

from shamba_signal.datasets.acquisition import (
    AcquisitionError,
    HttpResponse,
    persist_response,
    validate_response,
)
from shamba_signal.datasets.manifest import SourceDefinition


def source() -> SourceDefinition:
    return SourceDefinition(
        source_id="fsd-maize-yield",
        publisher="Kenya Ministry of Agriculture and Livestock Development",
        dataset_title="Maize yield by county",
        landing_url="https://fsd.kilimo.go.ke/indicators/maize-yield",
        acquisition_url="https://fsd.kilimo.go.ke/api/maize.csv",
        acquisition_mode="direct_csv",
        access_method="HTTPS CSV endpoint",
        spatial_coverage="Kenya admin level 1 counties",
        temporal_coverage="2022-2024",
        terms_status="review-required",
        redistribution_status="review-required",
        expected_fields=("county", "year", "yield"),
        accepted_media_types=("text/csv",),
        network_acquisition_ready=True,
    )


def response(body: bytes, **overrides: object) -> HttpResponse:
    values: dict[str, object] = {
        "status_code": 200,
        "headers": {"Content-Type": "text/csv; charset=utf-8"},
        "body": body,
        "final_url": "https://fsd.kilimo.go.ke/api/maize.csv",
    }
    values.update(overrides)
    return HttpResponse(**values)  # type: ignore[arg-type]


def test_persist_response_preserves_raw_bytes_and_writes_manifest(tmp_path: Path) -> None:
    payload = b"county,year,yield\nBusia,2023,2.4\n"
    snapshot = persist_response(
        source=source(),
        response=response(payload),
        output_root=tmp_path,
        retrieved_at=datetime(2026, 8, 2, tzinfo=UTC),
        transformation_revision="git:deadbeef",
    )

    assert snapshot.raw_path.read_bytes() == payload
    assert snapshot.manifest.byte_size == len(payload)
    assert snapshot.manifest.storage_uri.startswith("snapshot://raw/fsd-maize-yield/")
    assert snapshot.manifest_path.is_file()
    assert str(tmp_path) not in snapshot.manifest_path.read_text(encoding="utf-8")


def test_validate_response_rejects_html_masquerading_as_csv() -> None:
    with pytest.raises(AcquisitionError, match="HTML"):
        validate_response(source(), response(b"<!doctype html><html>login</html>"))


def test_validate_response_rejects_empty_payload() -> None:
    with pytest.raises(AcquisitionError, match="empty"):
        validate_response(source(), response(b""))


def test_validate_response_rejects_missing_expected_fields() -> None:
    with pytest.raises(AcquisitionError, match="missing expected fields"):
        validate_response(source(), response(b"county,year\nBusia,2023\n"))


def test_validate_response_rejects_redirect_to_landing_page() -> None:
    with pytest.raises(AcquisitionError, match="landing page"):
        validate_response(
            source(),
            response(
                b"county,year,yield\nBusia,2023,2.4\n",
                final_url="https://fsd.kilimo.go.ke/indicators/maize-yield",
            ),
        )


def test_manual_verified_fields_support_unparsed_download_manager_bytes(tmp_path: Path) -> None:
    manual_source = SourceDefinition(
        source_id="nipfn-maize-2012-2020",
        publisher="Kenya National Bureau of Statistics / NIPFN",
        dataset_title="Maize Production by County 2012-2020",
        landing_url="https://nipfn.knbs.or.ke/download/maize-production-by-county-2012-2020/",
        acquisition_url="https://nipfn.knbs.or.ke/download/maize-production-by-county-2012-2020/",
        acquisition_mode="download_manager",
        access_method="Manual verified file from official download manager",
        spatial_coverage="Kenya counties",
        temporal_coverage="2012-2020",
        terms_status="review-required",
        redistribution_status="review-required",
        expected_fields=("county", "year", "production", "yield"),
        accepted_media_types=("application/octet-stream",),
        network_acquisition_ready=False,
    )
    snapshot = persist_response(
        source=manual_source,
        response=HttpResponse(
            status_code=200,
            headers={"Content-Type": "application/octet-stream"},
            body=b"verified official workbook bytes",
            final_url=manual_source.acquisition_url,
        ),
        output_root=tmp_path,
        retrieved_at=datetime(2026, 8, 2, tzinfo=UTC),
        transformation_revision="git:deadbeef",
        manual_verified_fields=("county", "year", "production", "yield"),
    )

    assert snapshot.manifest.schema_fingerprint
    assert snapshot.raw_path.suffix == ".bin"
