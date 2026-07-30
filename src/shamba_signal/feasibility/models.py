from __future__ import annotations

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


@dataclass(frozen=True)
class ScoreWeights:
    yield_label_quality: int
    historical_depth: int
    spatial_resolution: int
    satellite_usability: int
    license_and_redistribution: int
    access_stability: int

    def __post_init__(self) -> None:
        values = self.as_dict()
        if any(value < 0 for value in values.values()):
            raise ValueError("score weights must be non-negative")
        if sum(values.values()) != 100:
            raise ValueError("score weights must sum to 100")

    @classmethod
    def approved(cls) -> "ScoreWeights":
        return cls(35, 20, 15, 10, 10, 10)

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "ScoreWeights":
        return cls(**{name: int(values[name]) for name in DIMENSIONS})

    def as_dict(self) -> dict[str, int]:
        return {name: int(getattr(self, name)) for name in DIMENSIONS}


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
        if any(not 0 <= float(value) <= 100 for value in self.dimensions.values()):
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
            dimensions={name: float(values["dimensions"][name]) for name in DIMENSIONS},
            evidence_refs=tuple(str(item) for item in values["evidence_refs"]),
            limitations=tuple(str(item) for item in values.get("limitations", [])),
            rationales={name: str(values["rationales"][name]) for name in DIMENSIONS}
            if values.get("rationales")
            else None,
        )
