from __future__ import annotations

import argparse
from pathlib import Path

from shamba_signal.feasibility.report import generate_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the Shamba Signal feasibility scorecard")
    parser.add_argument(
        "--evidence", type=Path, default=Path("data/feasibility/evidence.json")
    )
    parser.add_argument(
        "--profiles", type=Path, default=Path("data/feasibility/candidate_profiles.json")
    )
    parser.add_argument("--output", type=Path, default=Path("data/feasibility"))
    args = parser.parse_args()
    result = generate_artifacts(
        evidence_path=args.evidence,
        profiles_path=args.profiles,
        output_dir=args.output,
    )
    print(f"selected crop={result.selected_crop} county={result.selected_county}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
