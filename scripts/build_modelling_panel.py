from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from shamba_signal.datasets.knbs_report import (
    KNBS_REPORT_SHA256,
    canonicalize_knbs_maize_record,
    read_knbs_maize_annex,
)
from shamba_signal.datasets.modelling_panel import (
    build_modelling_panel,
    compare_revision_year,
    render_modelling_panel_csv,
)
from shamba_signal.datasets.nipfn_publication import build_nipfn_publication
from shamba_signal.datasets.target import load_county_registry
from shamba_signal.datasets.target_build import PilotGatePolicy

REPORT_SNAPSHOT_ID = (
    "snapshot://candidates/knbs-national-agriculture-production-report-2024/"
    f"{KNBS_REPORT_SHA256}.pdf"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the private 2012-2023 county-year maize modelling panel."
    )
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--workbook-manifest", type=Path, required=True)
    parser.add_argument("--report-pdf", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--county-registry",
        type=Path,
        default=Path("data/feasibility/candidate_profiles.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workbook = build_nipfn_publication(
        workbook_path=args.workbook,
        snapshot_manifest_path=args.workbook_manifest,
        county_registry_path=args.county_registry,
        primary_county_id="busia",
        fallback_county_id="trans_nzoia",
        policy=PilotGatePolicy(
            minimum_periods=1,
            minimum_yield_coverage=0,
            maximum_review_required_fraction=1,
            maximum_divergent_fraction=1,
        ),
    )
    registry = load_county_registry(args.county_registry)
    report_records = read_knbs_maize_annex(args.report_pdf)
    report_observations = tuple(
        observation
        for record in report_records
        for observation in canonicalize_knbs_maize_record(
            record,
            registry=registry,
            snapshot_id=REPORT_SNAPSHOT_ID,
        )
    )
    panel = build_modelling_panel(workbook.observations, report_observations)
    comparisons = compare_revision_year(
        workbook.observations,
        report_observations,
        year=2020,
    )

    years = sorted({row.year for row in panel})
    county_counts = Counter(row.county_id for row in panel)
    split_counts = Counter(row.split for row in panel)
    materially_different = sum(item.materially_different for item in comparisons)
    if len(panel) != 564 or years != list(range(2012, 2024)):
        raise ValueError("modelling panel must contain 564 county-year rows for 2012-2023")
    if len(county_counts) != 47 or set(county_counts.values()) != {12}:
        raise ValueError("modelling panel must contain 12 years for each of 47 counties")
    if split_counts != {"train": 470, "validation": 47, "test": 47}:
        raise ValueError("modelling panel temporal split does not match the registered policy")
    if len(comparisons) != 47 or materially_different != 24:
        raise ValueError("2020 source-vintage comparison does not match the verified audit")

    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / "modelling_panel.csv").write_text(
        render_modelling_panel_csv(panel), encoding="utf-8"
    )
    (args.output_root / "revision_comparison_2020.json").write_text(
        json.dumps([asdict(item) for item in comparisons], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "package_version": "county-year-maize-modelling-v1",
        "observation_grain": "county x maize x year",
        "row_count": len(panel),
        "usable_label_count": sum(row.usable_for_modelling for row in panel),
        "county_count": len(county_counts),
        "years": years,
        "split_counts": dict(sorted(split_counts.items())),
        "active_source_policy": {
            "2012-2018": "nipfn-workbook-2012-2020",
            "2019-2023": "knbs-report-2024",
            "2020_superseded_vintage": "preserved in revision_comparison_2020.json",
        },
        "source_sha256": {
            "nipfn_workbook": workbook.source_sha256,
            "knbs_report_2024": KNBS_REPORT_SHA256,
        },
        "materially_different_2020_counties": materially_different,
        "provisional_test_rows": sum(row.provisional for row in panel if row.split == "test"),
        "redistribution": "private local-only pending source terms review",
        "season_mapping": "not applied",
    }
    (args.output_root / "package_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_root / "dataset_card.md").write_text(
        "\n".join(
            [
                "# County-year maize modelling panel",
                "",
                "- 564 county-year rows across 47 counties and 2012-2023.",
                "- The NIPFN workbook supplies 2012-2018; the KNBS 2024 report supplies 2019-2023.",
                "- The older 2020 vintage is preserved separately and is not silently overwritten.",
                (
                    "- Training uses 2012-2021, validation uses 2022, and testing uses "
                    "provisional 2023."
                ),
                (
                    "- Yield is reported for the workbook years and derived from "
                    "production/area for report years."
                ),
                "- The package is private and annual; it contains no inferred season labels.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
