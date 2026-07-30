from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Literal

AcquisitionMode = Literal["direct_csv", "parameterized_json", "download_manager"]
TermsStatus = Literal["verified", "review-required"]


@dataclass(frozen=True)
class SourceDefinition:
    source_id: str
    publisher: str
    landing_url: str
    acquisition_url: str
    acquisition_mode: AcquisitionMode
    terms_status: TermsStatus

    def __post_init__(self) -> None:
        for field_name in ("landing_url", "acquisition_url"):
            if not getattr(self, field_name).startswith("https://"):
                raise ValueError(f"{field_name} must use HTTPS")


@dataclass(frozen=True)
class SnapshotManifest:
    source_id: str
    publisher: str
    landing_url: str
    acquisition_url: str
    acquisition_mode: AcquisitionMode
    terms_status: TermsStatus
    retrieved_at: str
    media_type: str
    byte_size: int
    sha256: str
    storage_uri: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def build_snapshot_manifest(
    *,
    source: SourceDefinition,
    file_path: Path,
    retrieved_at: datetime,
    media_type: str,
) -> SnapshotManifest:
    if retrieved_at.tzinfo is None:
        raise ValueError("retrieved_at must be timezone-aware")
    payload = file_path.read_bytes()
    return SnapshotManifest(
        source_id=source.source_id,
        publisher=source.publisher,
        landing_url=source.landing_url,
        acquisition_url=source.acquisition_url,
        acquisition_mode=source.acquisition_mode,
        terms_status=source.terms_status,
        retrieved_at=retrieved_at.isoformat(),
        media_type=media_type,
        byte_size=len(payload),
        sha256=sha256(payload).hexdigest(),
        storage_uri=file_path.resolve().as_uri(),
    )
