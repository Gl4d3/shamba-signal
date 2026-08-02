from __future__ import annotations

import argparse
import sys
from pathlib import Path

from shamba_signal.datasets.probe import probe_registry, render_probe_json
from shamba_signal.datasets.registry import load_source_registry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe registered data sources without persisting response bodies."
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("data/sources/maize_sources.json"),
    )
    parser.add_argument(
        "--source-id",
        action="append",
        default=[],
        help="Probe one registered source; repeat to select several sources.",
    )
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--require-all-ready",
        action="store_true",
        help="Exit with status 1 unless every selected source is ready.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.timeout_seconds <= 0:
        print("--timeout-seconds must be positive", file=sys.stderr)
        raise SystemExit(2)
    try:
        registry = load_source_registry(args.registry)
        results = probe_registry(
            registry,
            source_ids=tuple(args.source_id) or None,
            timeout_seconds=args.timeout_seconds,
        )
    except (OSError, KeyError, ValueError) as exc:
        print(f"source probe configuration failed: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    report = render_probe_json(results)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")

    if args.require_all_ready and any(item.status != "ready" for item in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
