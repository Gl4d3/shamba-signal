from shamba_signal.domain.platform import Capability, CapabilityStatus, PlatformStatus


def get_platform_status() -> PlatformStatus:
    return PlatformStatus(
        product="Shamba Signal",
        release="county-year-weather-evidence-v1",
        architecture="local FastAPI evidence dashboard backed by a versioned evaluation fixture",
        primary_output="retrospective county-year maize model evidence",
        forecast_timing="retrospective end-of-year backtest only",
        geography="all 47 Kenya counties at county-year grain",
        crop_scope="maize annual labels for 2012-2023; 2023 is provisional",
        refresh_modes=["manual reproducible experiment run"],
        capabilities=[
            Capability(
                id="official-panel",
                name="Official county-year modelling panel",
                status=CapabilityStatus.READY,
                outcome=(
                    "Reconciled 564 county-year rows across all 47 counties for 2012-2023, "
                    "with 563 usable maize-yield labels."
                ),
            ),
            Capability(
                id="temporal-baselines",
                name="Leakage-safe temporal baselines",
                status=CapabilityStatus.READY,
                outcome=(
                    "Compared previous year, county historical mean, and regularized temporal "
                    "Ridge using a frozen 2012-2021 train, 2022 selection, and provisional "
                    "2023 final test split."
                ),
            ),
            Capability(
                id="weather-value-test",
                name="Bounded ERA5 weather feature value test",
                status=CapabilityStatus.READY,
                outcome=(
                    "Weather Ridge improved on temporal Ridge but did not beat the county "
                    "historical mean, producing an explicit no-go."
                ),
            ),
            Capability(
                id="evidence-dashboard",
                name="Interactive evidence dashboard",
                status=CapabilityStatus.READY,
                outcome=(
                    "Serves national model comparison, county history, provisional-2023 "
                    "predictions and errors, method, lineage, downloads, and limitations from "
                    "the generated local fixture."
                ),
            ),
        ],
    )
