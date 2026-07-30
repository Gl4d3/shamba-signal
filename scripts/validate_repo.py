import csv
import json
from pathlib import Path

REQUIRED_FILES = (
    "README.md",
    "docs/product/PRD.md",
    "docs/product/MVP.md",
    "docs/architecture/ARCHITECTURE.md",
    "docs/roadmap/IMPLEMENTATION_SLICES.md",
    "docs/data/data-source-register.md",
    "docs/data/pilot-selection-decision.md",
    "data/catalog/datasets.yaml",
    "data/feasibility/evidence.json",
    "data/feasibility/candidate_profiles.json",
    "data/feasibility/scorecard.csv",
    "data/feasibility/selection.json",
)


def validate_required_files() -> list[str]:
    return [path for path in REQUIRED_FILES if not Path(path).is_file()]


def validate_catalog() -> list[str]:
    errors: list[str] = []
    catalog = json.loads(Path("data/catalog/datasets.yaml").read_text(encoding="utf-8"))
    weights = catalog["pilot_selection"]["weights"]
    if sum(weights.values()) != 100:
        errors.append("pilot-selection weights must total 100")
    for source in catalog["sources"]:
        if source["license_status"] not in {"verified", "review-required"}:
            errors.append(f"invalid license status for {source['id']}")
        if not source["access_url"].startswith("https://"):
            errors.append(f"non-HTTPS source URL for {source['id']}")
    return errors


def validate_feasibility_selection() -> list[str]:
    errors: list[str] = []
    selection = json.loads(
        Path("data/feasibility/selection.json").read_text(encoding="utf-8")
    )
    if sum(selection["weights"].values()) != 100:
        errors.append("feasibility selection weights must total 100")
    if selection["selected_crop"]["candidate_id"] != "maize":
        errors.append("Slice 1 selected crop must be maize")
    if selection["selected_county"]["candidate_id"] != "busia":
        errors.append("Slice 1 selected county must be busia")
    if not selection["sensitivity"]["crop_winner_stable"]:
        errors.append("crop winner must be stable across registered scenarios")
    if not selection["sensitivity"]["county_winner_stable"]:
        errors.append("county winner must be stable across registered scenarios")

    rows = list(
        csv.DictReader(
            Path("data/feasibility/scorecard.csv").read_text(encoding="utf-8").splitlines()
        )
    )
    counties = [row for row in rows if row["candidate_type"] == "county"]
    crops = [row for row in rows if row["candidate_type"] == "crop"]
    if len(counties) != 47:
        errors.append("feasibility scorecard must contain all 47 counties")
    if len(crops) < 2:
        errors.append("feasibility scorecard must compare multiple crop candidates")
    return errors


def main() -> None:
    errors = [
        *validate_required_files(),
        *validate_catalog(),
        *validate_feasibility_selection(),
    ]
    if errors:
        message = "Repository validation failed:\n- " + "\n- ".join(errors)
        raise SystemExit(message)
    print("Repository contract valid")


if __name__ == "__main__":
    main()
