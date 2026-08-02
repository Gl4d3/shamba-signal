from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import acquire_source
from shamba_signal.datasets.manifest import SourceDefinition


def test_verified_fields_without_input_file_fail_before_network_fetch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        acquire_source,
        "parse_args",
        lambda: Namespace(
            source_id="nipfn-maize-2012-2020",
            registry=None,
            output_root=None,
            input_file=None,
            media_type=None,
            final_url=None,
            transformation_revision="git:test",
            verified_field=["County"],
            timeout_seconds=1.0,
        ),
    )

    def fail_fetch(*_: object, **__: object) -> None:
        raise AssertionError("fetch_source must not be called")

    monkeypatch.setattr(acquire_source, "fetch_source", fail_fetch)

    with pytest.raises(SystemExit, match="1"):
        acquire_source.main()

    assert "--verified-field requires --input-file" in capsys.readouterr().err


def test_verified_fields_cannot_bypass_direct_csv_file_validation(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    direct_csv_source = SourceDefinition(
        source_id="direct-csv",
        publisher="Publisher",
        dataset_title="CSV",
        landing_url="https://example.com/landing",
        acquisition_url="https://example.com/data.csv",
        acquisition_mode="direct_csv",
        access_method="HTTPS CSV",
        spatial_coverage="Kenya",
        temporal_coverage="2020",
        terms_status="review-required",
        redistribution_status="review-required",
        expected_fields=("county", "year", "yield"),
        accepted_media_types=("text/csv",),
        network_acquisition_ready=False,
    )
    monkeypatch.setattr(
        acquire_source,
        "parse_args",
        lambda: Namespace(
            source_id="direct-csv",
            registry=Path("registry.json"),
            output_root=Path("snapshots"),
            input_file=Path("arbitrary.bin"),
            media_type="text/csv",
            final_url=None,
            transformation_revision="git:test",
            verified_field=["county", "year", "yield"],
            timeout_seconds=1.0,
        ),
    )
    monkeypatch.setattr(
        acquire_source,
        "load_source_registry",
        lambda _: SimpleNamespace(source=lambda _: direct_csv_source),
    )

    with pytest.raises(SystemExit, match="1"):
        acquire_source.main()

    assert (
        "--verified-field is only supported for download-manager sources"
        in capsys.readouterr().err
    )
