from argparse import Namespace

import pytest

from scripts import acquire_source


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
