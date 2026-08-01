from shamba_signal.domain.platform import Capability, CapabilityStatus, PlatformStatus


def get_platform_status() -> PlatformStatus:
    return PlatformStatus(
        product="Shamba Signal",
        release="foundation-v0",
        architecture="modular decision-intelligence platform",
        primary_output="county-season yield forecast",
        forecast_timing="mid-season",
        geography="Kenya-wide with one data-selected county deep dive",
        crop_scope="one crop selected by data feasibility",
        refresh_modes=["scheduled", "analyst-triggered"],
        capabilities=[
            Capability(
                id="data-feasibility",
                name="Data feasibility and pilot selection",
                status=CapabilityStatus.NEXT,
                outcome="Select the crop, county, historical window, and usable target labels.",
            ),
            Capability(
                id="yield-forecasting",
                name="County-season yield forecasting",
                status=CapabilityStatus.PLANNED,
                outcome="Estimate mid-season yield with calibrated prediction intervals.",
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
