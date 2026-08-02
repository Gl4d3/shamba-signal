from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from shamba_signal.datasets.manifest import SourceDefinition


@dataclass(frozen=True)
class SourceRegistry:
    registry_version: str
    selected_crop: str
    target_grain: str
    sources: tuple[SourceDefinition, ...]

    def source(self, source_id: str) -> SourceDefinition:
        matches = [item for item in self.sources if item.source_id == source_id]
        if not matches:
            raise KeyError(f"unknown source_id: {source_id}")
        return matches[0]


def _require_text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def load_source_registry(path: Path) -> SourceRegistry:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load source registry: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError("source registry root must be an object")

    raw_sources = payload.get("sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        raise ValueError("source registry must contain a non-empty sources list")

    sources: list[SourceDefinition] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_sources):
        if not isinstance(raw, dict):
            raise ValueError(f"sources[{index}] must be an object")
        source = SourceDefinition(
            source_id=_require_text("source_id", raw.get("source_id")),
            publisher=_require_text("publisher", raw.get("publisher")),
            dataset_title=_require_text("dataset_title", raw.get("dataset_title")),
            landing_url=_require_text("landing_url", raw.get("landing_url")),
            acquisition_url=_require_text("acquisition_url", raw.get("acquisition_url")),
            acquisition_mode=_require_text(
                "acquisition_mode", raw.get("acquisition_mode")
            ),  # type: ignore[arg-type]
            access_method=_require_text("access_method", raw.get("access_method")),
            spatial_coverage=_require_text(
                "spatial_coverage", raw.get("spatial_coverage")
            ),
            temporal_coverage=_require_text(
                "temporal_coverage", raw.get("temporal_coverage")
            ),
            terms_status=_require_text(
                "terms_status", raw.get("terms_status")
            ),  # type: ignore[arg-type]
            redistribution_status=_require_text(
                "redistribution_status", raw.get("redistribution_status")
            ),  # type: ignore[arg-type]
            expected_fields=tuple(raw.get("expected_fields", ())),
            accepted_media_types=tuple(raw.get("accepted_media_types", ())),
            network_acquisition_ready=raw.get("network_acquisition_ready"),
        )
        if source.source_id in seen:
            raise ValueError(f"duplicate source_id: {source.source_id}")
        seen.add(source.source_id)
        sources.append(source)

    return SourceRegistry(
        registry_version=_require_text("registry_version", payload.get("registry_version")),
        selected_crop=_require_text("selected_crop", payload.get("selected_crop")),
        target_grain=_require_text("target_grain", payload.get("target_grain")),
        sources=tuple(sources),
    )
