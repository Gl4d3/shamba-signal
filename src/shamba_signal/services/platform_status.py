from shamba_signal.domain.platform import Capability, CapabilityStatus, PlatformStatus


def get_platform_status() -> PlatformStatus:
    return PlatformStatus(
        product="Shamba Signal",
        release="slice-2-annual-target-v1",
        architecture="modular decision-intelligence platform",
        primary_output="county-season yield forecast",
        forecast_timing="mid-season",
        geography=(
            "Kenya-wide annual panel with Busia confirmed for annual-label validation and "
            "Trans Nzoia retained as fallback"
        ),
        crop_scope="maize selected by feasibility and verified in an annual KNBS snapshot",
        refresh_modes=["scheduled", "analyst-triggered"],
        capabilities=[
            Capability(
                id="data-feasibility",
                name="Data feasibility and pilot selection",
                status=CapabilityStatus.READY,
                outcome="Selected maize and Busia through a reproducible 47-county scorecard.",
            ),
            Capability(
                id="target-dataset",
                name="Reproducible annual maize target dataset",
                status=CapabilityStatus.READY,
                outcome=(
                    "KNBS/NIPFN snapshot accepted: 376 county-year rows for 47 counties across "
                    "2012-2018 and 2020. 2019 is absent; season mapping and forecasting have "
                    "not started."
                ),
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
