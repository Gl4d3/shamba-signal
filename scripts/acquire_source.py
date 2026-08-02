from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from shamba_signal.datasets.acquisition import (
    AcquisitionError,
    HttpResponse,
    fetch_source,
    persist_response,
)
from shamba_signal.datasets.registry import load_source_registry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Acquire and validate one registered Shamba Signal source snapshot."
    )
    parser.add_argument("source_id")
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("data/sources/maize_sources.json"),
    )
    parser.add_argument("--output-root", type=Path, default=Path("data/raw/snapshots"))
    parser.add_argument("--input-file", type=Path)
    parser.add_argument("--media-type")
    parser.add_argument("--final-url")
    parser.add_argument("--transformation-revision", required=True)
    parser.add_argument(
        "--verified-field",
        action="append",
        default=[],
        help="Field name manually verified in a supplied file; repeat for each field.",
    )
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    registry = load_source_registry(args.registry)
    source = registry.source(args.source_id)
    if source.terms_status == "blocked" or source.redistribution_status == "blocked":
        print(f"source {source.source_id} is blocked", file=sys.stderr)
        raise SystemExit(1)

    try:
        if args.input_file:
            if not args.media_type:
                raise AcquisitionError("--media-type is required with --input-file")
            response = HttpResponse(
                status_code=200,
                headers={"Content-Type": args.media_type},
                body=args.input_file.read_bytes(),
                final_url=args.final_url or source.acquisition_url,
            )
        else:
            response = fetch_source(source, timeout_seconds=args.timeout_seconds)

        snapshot = persist_response(
            source=source,
            response=response,
            output_root=args.output_root,
            retrieved_at=datetime.now(UTC),
            transformation_revision=args.transformation_revision,
            manual_verified_fields=(
                tuple(args.verified_field) if args.verified_field else None
            ),
        )
    except (AcquisitionError, OSError, ValueError, KeyError) as exc:
        print(f"snapshot acquisition failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(json.dumps(snapshot.manifest.as_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
