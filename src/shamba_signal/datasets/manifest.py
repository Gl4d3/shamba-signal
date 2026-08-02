from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Literal
from urllib.parse import parse_qsl, urlsplit

AcquisitionMode = Literal["direct_csv", "parameterized_json", "download_manager"]
TermsStatus = Literal["verified", "review-required", "blocked"]
RedistributionStatus = Literal["allowed", "restricted", "review-required", "blocked"]

_ALLOWED_ACQUISITION_MODES = {"direct_csv", "parameterized_json", "download_manager"}
_ALLOWED_TERMS_STATUSES = {"verified", "review-required", "blocked"}
_ALLOWED_REDISTRIBUTION_STATUSES = {
    "allowed",
    "restricted",
    "review-required",
    "blocked",
}
_FORBIDDEN_URL_QUERY_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "authorization",
    "expires",
    "key",
    "signature",
    "sig",
    "token",
}

_ALLOWED_MEDIA_TYPES = {
    "text/csv",
    "application/csv",
    "application/json",
    "application/vnd.ms-excel",
    "application/octet-stream",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def _require_text(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _validate_public_https_url(name: str, value: str) -> None:
    _require_text(name, value)
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{name} must use HTTPS")
    if parsed.username or parsed.password:
        raise ValueError(f"{name} must not contain embedded credentials")
    query_keys = {key.lower() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
    forbidden = sorted(query_keys & _FORBIDDEN_URL_QUERY_KEYS)
    if forbidden:
        raise ValueError(f"{name} must not contain secret or signed query parameters: {forbidden}")


@dataclass(frozen=True)
class SourceDefinition:
    source_id: str
    publisher: str
    dataset_title: str
    landing_url: str
    acquisition_url: str
    acquisition_mode: AcquisitionMode
    access_method: str
    spatial_coverage: str
    temporal_coverage: str
    terms_status: TermsStatus
    redistribution_status: RedistributionStatus
    expected_fields: tuple[str, ...]
    accepted_media_types: tuple[str, ...]
    network_acquisition_ready: bool

    def __post_init__(self) -> None:
        for field_name in (
            "source_id",
            "publisher",
            "dataset_title",
            "access_method",
            "spatial_coverage",
            "temporal_coverage",
        ):
            _require_text(field_name, getattr(self, field_name))
        for field_name in ("landing_url", "acquisition_url"):
            _validate_public_https_url(field_name, getattr(self, field_name))
        if self.acquisition_mode not in _ALLOWED_ACQUISITION_MODES:
            raise ValueError("unsupported acquisition_mode")
        if self.terms_status not in _ALLOWED_TERMS_STATUSES:
            raise ValueError("unsupported terms_status")
        if self.redistribution_status not in _ALLOWED_REDISTRIBUTION_STATUSES:
            raise ValueError("unsupported redistribution_status")
        if not self.expected_fields or any(not item.strip() for item in self.expected_fields):
            raise ValueError("expected_fields must contain non-empty field names")
        if len(set(self.expected_fields)) != len(self.expected_fields):
            raise ValueError("expected_fields must not contain duplicates")
        if not isinstance(self.network_acquisition_ready, bool):
            raise ValueError("network_acquisition_ready must be a boolean")
        if not self.accepted_media_types:
            raise ValueError("accepted_media_types must not be empty")
        unsupported = set(self.accepted_media_types) - _ALLOWED_MEDIA_TYPES
        if unsupported:
            raise ValueError(f"unsupported media types: {sorted(unsupported)}")
        if self.terms_status == "blocked" and self.redistribution_status != "blocked":
            raise ValueError("blocked terms require blocked redistribution")


@dataclass(frozen=True)
class SnapshotManifest:
    source_id: str
    publisher: str
    dataset_title: str
    landing_url: str
    acquisition_url: str
    final_url: str
    acquisition_mode: AcquisitionMode
    access_method: str
    spatial_coverage: str
    temporal_coverage: str
    terms_status: TermsStatus
    redistribution_status: RedistributionStatus
    retrieved_at: str
    http_status: int
    media_type: str
    byte_size: int
    sha256: str
    schema_fingerprint: str
    storage_uri: str
    transformation_revision: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def build_snapshot_manifest(
    *,
    source: SourceDefinition,
    file_path: Path,
    retrieved_at: datetime,
    http_status: int,
    media_type: str,
    final_url: str,
    schema_fingerprint: str,
    storage_uri: str,
    transformation_revision: str,
) -> SnapshotManifest:
    if retrieved_at.tzinfo is None:
        raise ValueError("retrieved_at must be timezone-aware")
    if http_status != 200:
        raise ValueError("http_status must be 200 for an accepted snapshot")
    normalized_media_type = media_type.split(";", 1)[0].strip().lower()
    if normalized_media_type not in source.accepted_media_types:
        raise ValueError("media_type is not accepted for this source")
    for field_name, value in (
        ("final_url", final_url),
        ("schema_fingerprint", schema_fingerprint),
        ("storage_uri", storage_uri),
        ("transformation_revision", transformation_revision),
    ):
        _require_text(field_name, value)
    _validate_public_https_url("final_url", final_url)
    if storage_uri.startswith("file:") or Path(storage_uri).is_absolute():
        raise ValueError("storage_uri must be portable and must not be a local absolute URI")
    if ".." in PurePosixPath(storage_uri).parts:
        raise ValueError("storage_uri must not contain parent traversal")

    payload = file_path.read_bytes()
    if not payload:
        raise ValueError("snapshot payload must not be empty")
    return SnapshotManifest(
        source_id=source.source_id,
        publisher=source.publisher,
        dataset_title=source.dataset_title,
        landing_url=source.landing_url,
        acquisition_url=source.acquisition_url,
        final_url=final_url,
        acquisition_mode=source.acquisition_mode,
        access_method=source.access_method,
        spatial_coverage=source.spatial_coverage,
        temporal_coverage=source.temporal_coverage,
        terms_status=source.terms_status,
        redistribution_status=source.redistribution_status,
        retrieved_at=retrieved_at.isoformat(),
        http_status=http_status,
        media_type=normalized_media_type,
        byte_size=len(payload),
        sha256=sha256(payload).hexdigest(),
        schema_fingerprint=schema_fingerprint,
        storage_uri=storage_uri,
        transformation_revision=transformation_revision,
    )
