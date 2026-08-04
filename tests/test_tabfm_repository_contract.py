from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_makefile_exposes_isolated_tabfm_commands() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "tabfm-test:" in makefile
    assert "tabfm-run:" in makefile
    assert "--project experiments/tabfm" in makefile
    assert "TABFM_PANEL" in makefile
    assert "TABFM_WEATHER_CACHE" in makefile
    assert "verify: lint test validate compile smoke" in makefile


def test_readme_keeps_original_result_first_and_labels_extension() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    original = readme.index("The result")
    extension = readme.index("Exploratory TabFM extension")
    assert original < extension
    assert "No TabFM score is claimed" in readme
    assert "2023 fold is post-hoc" in readme
    assert "non-commercial" in readme


def test_tabfm_method_note_documents_protocol_and_private_outputs() -> None:
    note = (
        ROOT / "docs/modelling/tabfm-temporal-benchmark.md"
    ).read_text(encoding="utf-8")

    assert "2018–2023" in note
    assert "2018–2022" in note
    assert "tabfm-non-commercial-v1.0" in note
    assert "predictions.csv" in note
    assert "future untouched year" in note
