import json

from shamba_signal.datasets.acquisition import AcquisitionError, HttpResponse
from shamba_signal.datasets.manifest import SourceDefinition
from shamba_signal.datasets.probe import probe_registry, probe_source, render_probe_json
from shamba_signal.datasets.registry import SourceRegistry


def make_source(**overrides: object) -> SourceDefinition:
    values: dict[str, object] = {
        "source_id": "fsd-maize-yield",
        "publisher": "Kenya Ministry of Agriculture and Livestock Development",
        "dataset_title": "Maize yield by county",
        "landing_url": "https://fsd.kilimo.go.ke/indicator",
        "acquisition_url": "https://fsd.kilimo.go.ke/api/maize.csv",
        "acquisition_mode": "direct_csv",
        "access_method": "HTTPS CSV endpoint",
        "spatial_coverage": "Kenya counties",
        "temporal_coverage": "2021",
        "terms_status": "review-required",
        "redistribution_status": "review-required",
        "expected_fields": ("county", "year", "yield"),
        "accepted_media_types": ("text/csv",),
        "network_acquisition_ready": True,
    }
    values.update(overrides)
    return SourceDefinition(**values)  # type: ignore[arg-type]


def valid_fetcher(_: SourceDefinition, *, timeout_seconds: float = 30.0) -> HttpResponse:
    assert timeout_seconds == 12.0
    return HttpResponse(
        status_code=200,
        headers={"Content-Type": "text/csv; charset=utf-8"},
        body=b"county,year,yield\nBusia,2021,2.1\n",
        final_url="https://fsd.kilimo.go.ke/api/maize.csv",
    )


def test_probe_source_reports_ready_without_persisting_bytes() -> None:
    result = probe_source(make_source(), fetcher=valid_fetcher, timeout_seconds=12.0)

    assert result.status == "ready"
    assert result.attempted is True
    assert result.http_status == 200
    assert result.media_type == "text/csv"
    assert result.byte_size == 33
    assert result.schema_fingerprint
    assert result.error_category is None


def test_probe_source_marks_not_ready_without_attempting_network() -> None:
    called = False

    def fetcher(_: SourceDefinition, *, timeout_seconds: float = 30.0) -> HttpResponse:
        nonlocal called
        called = True
        raise AssertionError("fetcher must not run")

    result = probe_source(
        make_source(network_acquisition_ready=False),
        fetcher=fetcher,
    )

    assert result.status == "not-ready"
    assert result.attempted is False
    assert called is False


def test_probe_source_marks_download_manager_as_manual_required() -> None:
    result = probe_source(
        make_source(
            source_id="nipfn-maize",
            acquisition_mode="download_manager",
            network_acquisition_ready=False,
        )
    )

    assert result.status == "manual-required"
    assert result.attempted is False


def test_probe_source_marks_blocked_source_without_attempt() -> None:
    result = probe_source(
        make_source(
            terms_status="blocked",
            redistribution_status="blocked",
        )
    )

    assert result.status == "blocked"
    assert result.attempted is False


def test_probe_source_classifies_network_failure_as_unreachable() -> None:
    def failed(_: SourceDefinition, *, timeout_seconds: float = 30.0) -> HttpResponse:
        raise AcquisitionError("source request failed: DNS lookup failed")

    result = probe_source(make_source(), fetcher=failed)

    assert result.status == "unreachable"
    assert result.error_category == "network"
    assert "DNS lookup failed" in result.error_detail


def test_probe_source_classifies_invalid_payload_without_returning_body() -> None:
    def bad(_: SourceDefinition, *, timeout_seconds: float = 30.0) -> HttpResponse:
        return HttpResponse(
            status_code=200,
            headers={"Content-Type": "text/csv"},
            body=b"<!doctype html><html>login</html>",
            final_url="https://fsd.kilimo.go.ke/api/maize.csv",
        )

    result = probe_source(make_source(), fetcher=bad)

    assert result.status == "invalid-response"
    assert result.error_category == "validation"
    assert "HTML" in result.error_detail
    assert "body" not in result.as_dict()


def test_probe_registry_is_deterministic_and_filterable() -> None:
    registry = SourceRegistry(
        registry_version="0.3.0",
        selected_crop="maize",
        target_grain="county x crop x season",
        sources=(
            make_source(source_id="z-source"),
            make_source(source_id="a-source", network_acquisition_ready=False),
        ),
    )

    results = probe_registry(
        registry,
        source_ids=("z-source",),
        fetcher=valid_fetcher,
        timeout_seconds=12.0,
    )

    assert [item.source_id for item in results] == ["z-source"]
    parsed = json.loads(render_probe_json(results))
    assert parsed[0]["status"] == "ready"
    assert render_probe_json(results).endswith("\n")
