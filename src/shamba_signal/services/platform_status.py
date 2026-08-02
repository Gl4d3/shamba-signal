from shamba_signal.domain.platform import Capability, CapabilityStatus, PlatformStatus


def get_platform_status() -> PlatformStatus:
    return PlatformStatus(
        product="Shamba Signal",
        release="slice-2a-annual-snapshot-v1",
        architecture="modular decision-intelligence platform",
        primary_output="county-year baseline feasibility",
        forecast_timing="not scheduled",
        geography=(
            "Kenya-wide annual panel with Busia confirmed for annual-label validation and "
            "Trans Nzoia retained as fallback"
        ),
        crop_scope="maize in a source-bound annual snapshot; source precedence is unresolved",
        refresh_modes=["scheduled", "analyst-triggered"],
        capabilities=[
            Capability(
                id="data-feasibility",
                name="Data feasibility and pilot selection",
                status=CapabilityStatus.READY,
                outcome="Selected maize and Busia through a reproducible 47-county scorecard.",
            ),
            Capability(
                id="annual-snapshot",
                name="Slice 2A annual snapshot package",
                status=CapabilityStatus.READY,
                outcome=(
                    "Ready as a source-bound private annual snapshot package; it is not "
                    "model-ready and does not resolve source precedence."
                ),
            ),
            Capability(
                id="annual-label-reconciliation",
                name="Slice 2B official annual label reconciliation",
                status=CapabilityStatus.NEXT,
                outcome=(
                    "Reconcile conflicting official 2020 vintages and extend the annual panel "
                    "before modelling."
                ),
            ),
            Capability(
                id="county-year-baseline",
                name="County-year baseline feasibility",
                status=CapabilityStatus.PLANNED,
                outcome=(
                    "Assess whether reconciled annual labels support a baseline feasibility study."
                ),
            ),
            Capability(
                id="stress-attribution",
                name="Crop-stress attribution",
                status=CapabilityStatus.PLANNED,
                outcome=(
                    "Explain rainfall, heat, moisture, and vegetation signals behind forecasts."
                ),
            ),
            Capability(
                id="guardrailed-advisory",
                name="Guardrailed decision support",
                status=CapabilityStatus.PLANNED,
                outcome="Select evidence-linked actions from approved agricultural playbooks.",
            ),
        ],
    )
