from shamba_signal.domain.platform import Capability, CapabilityStatus, PlatformStatus


def get_platform_status() -> PlatformStatus:
    return PlatformStatus(
        product="Shamba Signal",
        release="slice-1-feasibility-v0",
        architecture="modular decision-intelligence platform",
        primary_output="county-season yield forecast",
        forecast_timing="mid-season",
        geography="Kenya-wide with Busia as the selected county deep dive",
        crop_scope="maize selected by data feasibility; Trans Nzoia is the county fallback",
        refresh_modes=["scheduled", "analyst-triggered"],
        capabilities=[
            Capability(
                id="data-feasibility",
                name="Data feasibility and pilot selection",
                status=CapabilityStatus.READY,
                outcome="Selected maize and Busia through a reproducible 47-county scorecard.",
            ),
            Capability(
                id="yield-forecasting",
                name="County-season yield forecasting",
                status=CapabilityStatus.NEXT,
                outcome="Build and validate the official maize county-season target dataset.",
            ),
            Capability(
                id="stress-attribution",
                name="Crop-stress attribution",
                status=CapabilityStatus.PLANNED,
                outcome="Explain rainfall, heat, moisture, and vegetation signals behind forecasts.",
            ),
            Capability(
                id="guardrailed-advisory",
                name="Guardrailed decision support",
                status=CapabilityStatus.PLANNED,
                outcome="Select evidence-linked actions from approved agricultural playbooks.",
            ),
        ],
    )
