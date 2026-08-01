from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class CapabilityStatus(StrEnum):
    READY = "ready"
    NEXT = "next"
    PLANNED = "planned"


class Capability(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    status: CapabilityStatus
    outcome: str


class PlatformStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    product: str
    release: str
    architecture: str
    primary_output: str
    forecast_timing: str
    geography: str
    crop_scope: str
    refresh_modes: list[str]
    capabilities: list[Capability]
