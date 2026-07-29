import json
from pathlib import Path

REQUIRED_FILES = (
    "README.md",
    "docs/product/PRD.md",
    "docs/product/MVP.md",
    "docs/architecture/ARCHITECTURE.md",
    "docs/roadmap/IMPLEMENTATION_SLICES.md",
    "docs/data/data-source-register.md",
    "data/catalog/datasets.yaml",
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


def main() -> None:
    errors = [*validate_required_files(), *validate_catalog()]
    if errors:
        message = "Repository validation failed:\n- " + "\n- ".join(errors)
        raise SystemExit(message)
    print("Repository contract valid")


if __name__ == "__main__":
    main()
