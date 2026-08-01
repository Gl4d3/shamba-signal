from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Literal, Mapping

DIMENSIONS = (
    "yield_label_quality",
    "historical_depth",
    "spatial_resolution",
    "satellite_usability",
    "license_and_redistribution",
    "access_stability",
)
Weight = int | float


@dataclass(frozen=True)
class ScoreWeights:
    yield_label_quality: Weight
    historical_depth: Weight
    spatial_resolution: Weight
    satellite_usability: Weight
    license_and_redistribution: Weight
    access_stability: Weight

    def __post_init__(self) -> None:
        values = self.as_dict()
        for name, value in values.items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(f"score weight {name} must be a finite number")
            if value < 0:
                raise ValueError("score weights must be non-negative")
        if not math.isclose(sum(values.values()), 100.0, rel_tol=0.0, abs_tol=1e-9):
            raise ValueError("score weights must sum to 100")

    @classmethod
    def approved(cls) -> "ScoreWeights":
        return cls(35, 20, 15, 10, 10, 10)

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "ScoreWeights":
        parsed: dict[str, Weight] = {}
        for name in DIMENSIONS:
            value = values[name]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"score weight {name} must be numeric")
            parsed[name] = value
        return cls(**parsed)

    def as_dict(self) -> dict[str, Weight]:
        return {name: getattr(self, name) for name in DIMENSIONS}


@dataclass(frozen=True)
class CandidateProfile:
    candidate_id: str
    candidate_type: Literal["crop", "county"]
    name: str
    dimensions: Mapping[str, float]
    evidence_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    rationales: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        if set(self.dimensions) != set(DIMENSIONS):
            raise ValueError(f"candidate dimensions must be exactly {DIMENSIONS}")
        for name, value in self.dimensions.items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(f"candidate score {name} must be a finite number")
            if not 0 <= value <= 100:
                raise ValueError("candidate scores must be between 0 and 100")
        if not self.evidence_refs:
            raise ValueError("candidate must reference at least one evidence record")
        if self.rationales is not None and set(self.rationales) != set(DIMENSIONS):
            raise ValueError("candidate rationales must cover every score dimension")

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "CandidateProfile":
        return cls(
            candidate_id=str(values["candidate_id"]),
            candidate_type=values["candidate_type"],
            name=str(values["name"]),
            dimensions=cls._parse_dimensions(values["dimensions"]),
            evidence_refs=tuple(str(item) for item in values["evidence_refs"]),
            limitations=tuple(str(item) for item in values.get("limitations", [])),
            rationales={name: str(values["rationales"][name]) for name in DIMENSIONS}
            if values.get("rationales")
            else None,
        )

    @staticmethod
    def _parse_dimensions(values: Mapping[str, Any]) -> dict[str, float]:
        dimensions: dict[str, float] = {}
        for name in DIMENSIONS:
            value = values[name]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"candidate score {name} must be numeric")
            dimensions[name] = float(value)
        return dimensions
