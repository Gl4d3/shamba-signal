from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from shamba_signal.datasets.manifest import (
    SnapshotManifest,
    SourceDefinition,
    build_snapshot_manifest,
)


class AcquisitionError(RuntimeError):
    """Raised when source bytes do not satisfy the fail-closed snapshot contract."""


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    headers: dict[str, str]
    body: bytes
    final_url: str


@dataclass(frozen=True)
class PersistedSnapshot:
    raw_path: Path
    manifest_path: Path
    manifest: SnapshotManifest


def _media_type(headers: dict[str, str]) -> str:
    raw = next((value for key, value in headers.items() if key.lower() == "content-type"), "")
    return raw.split(";", 1)[0].strip().lower()


def _looks_like_html(payload: bytes) -> bool:
    prefix = payload.lstrip()[:256].lower()
    return prefix.startswith(b"<!doctype html") or prefix.startswith(b"<html")


def _schema_fields(source: SourceDefinition, payload: bytes, media_type: str) -> tuple[str, ...]:
    try:
        if source.acquisition_mode == "direct_csv":
            if media_type not in {"text/csv", "application/csv", "application/vnd.ms-excel"}:
                raise AcquisitionError("direct CSV source returned a non-CSV media type")
            text = payload.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            fields = tuple(
                item.strip()
                for item in (reader.fieldnames or ())
                if item and item.strip()
            )
            if not fields:
                raise AcquisitionError("CSV response has no header row")
            if next(reader, None) is None:
                raise AcquisitionError("CSV response contains no data rows")
            return fields

        if source.acquisition_mode == "parameterized_json":
            if media_type != "application/json":
                raise AcquisitionError("parameterized JSON source returned a non-JSON media type")
            value = json.loads(payload.decode("utf-8"))
            if isinstance(value, dict):
                candidates = value.get("results") or value.get("data") or value.get("records")
            else:
                candidates = value
            if (
                not isinstance(candidates, list)
                or not candidates
                or not isinstance(candidates[0], dict)
            ):
                raise AcquisitionError("JSON response does not contain a non-empty record list")
            return tuple(sorted(str(key) for key in candidates[0]))

        if source.acquisition_mode == "download_manager":
            raise AcquisitionError(
                "download-manager sources require a resolved file response "
                "or manual verified snapshot"
            )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AcquisitionError(
            "response could not be parsed using the declared acquisition mode"
        ) from exc
    raise AcquisitionError(f"unsupported acquisition mode: {source.acquisition_mode}")


def validate_response(
    source: SourceDefinition,
    response: HttpResponse,
    *,
    manual_verified_fields: tuple[str, ...] | None = None,
) -> tuple[str, str]:
    if response.status_code != 200:
        raise AcquisitionError(f"source returned HTTP {response.status_code}")
    if not response.final_url.startswith("https://"):
        raise AcquisitionError("final response URL must use HTTPS")
    if not response.body:
        raise AcquisitionError("source returned an empty payload")
    media_type = _media_type(response.headers)
    if media_type not in source.accepted_media_types:
        raise AcquisitionError(f"unexpected media type: {media_type or 'missing'}")
    if media_type == "text/html" or _looks_like_html(response.body):
        raise AcquisitionError("source returned HTML instead of dataset bytes")
    if response.final_url.rstrip("/") == source.landing_url.rstrip("/") and (
        source.acquisition_url.rstrip("/") != source.landing_url.rstrip("/")
    ):
        raise AcquisitionError("dataset request redirected to the landing page")

    if manual_verified_fields is not None:
        if not manual_verified_fields or any(
            not item.strip() for item in manual_verified_fields
        ):
            raise AcquisitionError("manual verified fields must be non-empty")
        fields = tuple(item.strip() for item in manual_verified_fields)
        if len(set(fields)) != len(fields):
            raise AcquisitionError("manual verified fields must not contain duplicates")
    else:
        fields = _schema_fields(source, response.body, media_type)
    missing = sorted(set(source.expected_fields) - set(fields))
    if missing:
        raise AcquisitionError(f"response schema is missing expected fields: {missing}")
    fingerprint = sha256("\n".join(sorted(fields)).encode("utf-8")).hexdigest()
    return media_type, fingerprint


def persist_response(
    *,
    source: SourceDefinition,
    response: HttpResponse,
    output_root: Path,
    retrieved_at: datetime,
    transformation_revision: str,
    manual_verified_fields: tuple[str, ...] | None = None,
) -> PersistedSnapshot:
    media_type, schema_fingerprint = validate_response(
        source, response, manual_verified_fields=manual_verified_fields
    )
    digest = sha256(response.body).hexdigest()
    extension = {
        "text/csv": "csv",
        "application/csv": "csv",
        "application/vnd.ms-excel": "csv",
        "application/json": "json",
        "application/octet-stream": "bin",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    }[media_type]
    relative_raw = Path("raw") / source.source_id / f"{digest}.{extension}"
    raw_path = output_root / relative_raw
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(response.body)

    storage_uri = f"snapshot://{relative_raw.as_posix()}"
    manifest = build_snapshot_manifest(
        source=source,
        file_path=raw_path,
        retrieved_at=retrieved_at,
        http_status=response.status_code,
        media_type=media_type,
        final_url=response.final_url,
        schema_fingerprint=schema_fingerprint,
        storage_uri=storage_uri,
        transformation_revision=transformation_revision,
    )
    manifest_path = output_root / "manifests" / source.source_id / f"{digest}.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return PersistedSnapshot(raw_path=raw_path, manifest_path=manifest_path, manifest=manifest)


def fetch_source(source: SourceDefinition, *, timeout_seconds: float = 30.0) -> HttpResponse:
    if not source.network_acquisition_ready:
        raise AcquisitionError("source network acquisition is not yet ready")
    accept = ", ".join(source.accepted_media_types)
    request = Request(
        source.acquisition_url,
        headers={
            "Accept": accept,
            "User-Agent": "ShambaSignal/0.1 (+https://github.com/Gl4d3/shamba-signal)",
        },
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310
            return HttpResponse(
                status_code=response.status,
                headers=dict(response.headers.items()),
                body=response.read(),
                final_url=response.geturl(),
            )
    except HTTPError as exc:
        raise AcquisitionError(f"source returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise AcquisitionError(f"source request failed: {exc.reason}") from exc
