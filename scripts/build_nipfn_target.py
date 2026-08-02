from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from shamba_signal.datasets.nipfn_publication import NipfnPublication, build_nipfn_publication
from shamba_signal.datasets.target_build import (
    PilotGatePolicy,
    render_quality_json,
    render_target_csv,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a local-only annual maize target from an accepted NIPFN workbook."
    )
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--snapshot-manifest", type=Path, required=True)
    parser.add_argument(
        "--county-registry",
        type=Path,
        default=Path("data/feasibility/candidate_profiles.json"),
    )
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--primary-county", default="busia")
    parser.add_argument("--fallback-county", default="trans_nzoia")
    parser.add_argument("--minimum-periods", type=int, required=True)
    parser.add_argument("--minimum-yield-coverage", type=float, required=True)
    parser.add_argument("--maximum-review-required-fraction", type=float, required=True)
    parser.add_argument("--maximum-divergent-fraction", type=float, required=True)
    return parser.parse_args()


def _publication_manifest(
    *,
    snapshot_id: str,
    source_sha256: str,
    period_ids: list[str],
    target_rows: int,
) -> dict[str, object]:
    return {
        "publication_version": "nipfn-annual-v1",
        "source_id": "nipfn-maize-2012-2020",
        "source_sha256": source_sha256,
        "snapshot_id": snapshot_id,
        "observation_grain": "county x maize x annual observation",
        "season_mapping": "not applied",
        "period_ids": period_ids,
        "target_rows": target_rows,
        "publication_scope": "local-only pending source redistribution review",
    }


def _dataset_card(*, publication: NipfnPublication, period_ids: list[str]) -> str:
    target = publication.target
    decision = publication.decision
    return "\n".join(
        [
            "# NIPFN annual maize target dataset",
            "",
            "## Scope",
            "",
            "- Source: Kenya National Bureau of Statistics / NIPFN Maize Production by "
            "County 2012-2020.",
            "- Grain: county × maize × annual observation; no season mapping is inferred.",
            "- Source bytes and row-level output are local-only pending redistribution review.",
            "",
            "## Observed coverage",
            "",
            f"- {target.report.total_observations} canonical observations across "
            f"{target.report.target_rows} county-year rows.",
            f"- Observed years: {', '.join(period_ids)}. The claimed range is not continuous: "
            "2019 is absent.",
            f"- {target.report.rows_with_nonpositive_harvested_area} rows have zero harvested "
            "area, so derived yield is intentionally unavailable for those rows.",
            f"- {target.report.rows_divergent} rows have divergent reported and derived yield; "
            "neither value is silently selected.",
            "",
            "## Pilot gate",
            "",
            f"- Result: {decision.status}.",
            f"- Selected county: {decision.selected_county_id or 'none'}.",
            "- This validates the available annual-label slice only. It does not authorize a "
            "county-season forecast model.",
            "",
        ]
    )


def main() -> None:
    args = parse_args()
    policy = PilotGatePolicy(
        minimum_periods=args.minimum_periods,
        minimum_yield_coverage=args.minimum_yield_coverage,
        maximum_review_required_fraction=args.maximum_review_required_fraction,
        maximum_divergent_fraction=args.maximum_divergent_fraction,
    )
    publication = build_nipfn_publication(
        workbook_path=args.workbook,
        snapshot_manifest_path=args.snapshot_manifest,
        county_registry_path=args.county_registry,
        primary_county_id=args.primary_county,
        fallback_county_id=args.fallback_county,
        policy=policy,
    )
    period_ids = sorted({row.key.period_id for row in publication.target.rows})
    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / "target.csv").write_text(
        render_target_csv(publication.target.rows), encoding="utf-8"
    )
    (args.output_root / "quality_report.json").write_text(
        render_quality_json(publication.target.report), encoding="utf-8"
    )
    (args.output_root / "pilot_decision.json").write_text(
        json.dumps(asdict(publication.decision), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_root / "publication_manifest.json").write_text(
        json.dumps(
            _publication_manifest(
                snapshot_id=publication.snapshot_id,
                source_sha256=publication.source_sha256,
                period_ids=period_ids,
                target_rows=publication.target.report.target_rows,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (args.output_root / "dataset_card.md").write_text(
        _dataset_card(publication=publication, period_ids=period_ids), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "target_rows": publication.target.report.target_rows,
                "period_ids": period_ids,
                "pilot_status": publication.decision.status,
                "selected_county_id": publication.decision.selected_county_id,
                "output_root": args.output_root.as_posix(),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
