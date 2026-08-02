from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Callable, Literal, Sequence

from shamba_signal.datasets.acquisition import (
    AcquisitionError,
    HttpResponse,
    fetch_source,
    validate_response,
)
from shamba_signal.datasets.manifest import SourceDefinition
from shamba_signal.datasets.registry import SourceRegistry

ProbeStatus = Literal[
    "ready",
    "blocked",
    "not-ready",
    "manual-required",
    "unreachable",
    "invalid-response",
]
ErrorCategory = Literal["policy", "configuration", "network", "validation"]
Fetcher = Callable[..., HttpResponse]


@dataclass(frozen=True)
class SourceProbeResult:
    source_id: str
    status: ProbeStatus
    attempted: bool
    acquisition_url: str
    final_url: str | None = None
    http_status: int | None = None
    media_type: str | None = None
    byte_size: int | None = None
    schema_fingerprint: str | None = None
    error_category: ErrorCategory | None = None
    error_detail: str | None = None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _result_without_attempt(
    source: SourceDefinition,
    *,
    status: ProbeStatus,
    category: ErrorCategory,
    detail: str,
) -> SourceProbeResult:
    return SourceProbeResult(
        source_id=source.source_id,
        status=status,
        attempted=False,
        acquisition_url=source.acquisition_url,
        error_category=category,
        error_detail=detail,
    )


def _clean_error(value: str) -> str:
    return " ".join(value.split())[:300]


def probe_source(
    source: SourceDefinition,
    *,
    fetcher: Fetcher = fetch_source,
    timeout_seconds: float = 30.0,
) -> SourceProbeResult:
    if source.terms_status == "blocked" or source.redistribution_status == "blocked":
        return _result_without_attempt(
            source,
            status="blocked",
            category="policy",
            detail="source terms or redistribution status is blocked",
        )
    if not source.network_acquisition_ready:
        if source.acquisition_mode == "download_manager":
            return _result_without_attempt(
                source,
                status="manual-required",
                category="configuration",
                detail="official download manager requires a resolved asset or verified manual file",
            )
        return _result_without_attempt(
            source,
            status="not-ready",
            category="configuration",
            detail="network acquisition is disabled until the endpoint schema is verified",
        )

    try:
        response = fetcher(source, timeout_seconds=timeout_seconds)
        media_type, schema_fingerprint = validate_response(source, response)
    except AcquisitionError as exc:
        detail = _clean_error(str(exc))
        network_failure = detail.startswith("source request failed:")
        return SourceProbeResult(
            source_id=source.source_id,
            status="unreachable" if network_failure else "invalid-response",
            attempted=True,
            acquisition_url=source.acquisition_url,
            error_category="network" if network_failure else "validation",
            error_detail=detail,
        )

    return SourceProbeResult(
        source_id=source.source_id,
        status="ready",
        attempted=True,
        acquisition_url=source.acquisition_url,
        final_url=response.final_url,
        http_status=response.status_code,
        media_type=media_type,
        byte_size=len(response.body),
        schema_fingerprint=schema_fingerprint,
    )


def probe_registry(
    registry: SourceRegistry,
    *,
    source_ids: Sequence[str] | None = None,
    fetcher: Fetcher = fetch_source,
    timeout_seconds: float = 30.0,
) -> tuple[SourceProbeResult, ...]:
    if source_ids is None:
        sources = registry.sources
    else:
        sources = tuple(registry.source(source_id) for source_id in source_ids)
    return tuple(
        probe_source(source, fetcher=fetcher, timeout_seconds=timeout_seconds)
        for source in sorted(sources, key=lambda item: item.source_id)
    )


def render_probe_json(results: Sequence[SourceProbeResult]) -> str:
    payload = [item.as_dict() for item in sorted(results, key=lambda item: item.source_id)]
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
