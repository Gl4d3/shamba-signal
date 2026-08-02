from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from shamba_signal.datasets.nipfn import canonicalize_nipfn_record, read_nipfn_workbook
from shamba_signal.datasets.target import CanonicalObservation, load_county_registry
from shamba_signal.datasets.target_build import (
    PilotDecision,
    PilotGatePolicy,
    TargetDatasetBuild,
    build_target_dataset,
    evaluate_pilot,
)

NIPFN_SOURCE_ID = "nipfn-maize-2012-2020"


@dataclass(frozen=True)
class NipfnPublication:
    snapshot_id: str
    source_sha256: str
    observations: tuple[CanonicalObservation, ...]
    target: TargetDatasetBuild
    decision: PilotDecision


def _load_snapshot_manifest(path: Path, workbook_path: Path) -> tuple[str, str]:
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load NIPFN snapshot manifest: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError("NIPFN snapshot manifest must be an object")
    if payload.get("source_id") != NIPFN_SOURCE_ID:
        raise ValueError("NIPFN snapshot manifest has an unexpected source_id")
    snapshot_id = payload.get("storage_uri")
    manifest_digest = payload.get("sha256")
    if not isinstance(snapshot_id, str) or not snapshot_id.startswith("snapshot://"):
        raise ValueError("NIPFN snapshot manifest must contain a portable snapshot URI")
    if not isinstance(manifest_digest, str) or len(manifest_digest) != 64:
        raise ValueError("NIPFN snapshot manifest must contain a SHA-256 digest")
    actual_digest = sha256(workbook_path.read_bytes()).hexdigest()
    if actual_digest != manifest_digest:
        raise ValueError("NIPFN workbook bytes do not match the accepted snapshot manifest")
    return snapshot_id, actual_digest


def build_nipfn_publication(
    *,
    workbook_path: Path,
    snapshot_manifest_path: Path,
    county_registry_path: Path,
    primary_county_id: str,
    fallback_county_id: str,
    policy: PilotGatePolicy,
) -> NipfnPublication:
    """Create the annual target build bound to one accepted official workbook."""
    snapshot_id, source_sha256 = _load_snapshot_manifest(
        snapshot_manifest_path, workbook_path
    )
    registry = load_county_registry(county_registry_path)
    observations = tuple(
        canonicalize_nipfn_record(
            record,
            registry=registry,
            snapshot_id=snapshot_id,
        )
        for record in read_nipfn_workbook(workbook_path)
    )
    target = build_target_dataset(observations)
    decision = evaluate_pilot(
        target.report,
        primary_county_id=primary_county_id,
        fallback_county_id=fallback_county_id,
        policy=policy,
    )
    return NipfnPublication(
        snapshot_id=snapshot_id,
        source_sha256=source_sha256,
        observations=observations,
        target=target,
        decision=decision,
    )
