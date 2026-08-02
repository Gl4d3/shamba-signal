from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from shamba_signal.domain.platform import PlatformStatus
from shamba_signal.services.platform_status import get_platform_status

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = PACKAGE_ROOT / "web"


def create_app() -> FastAPI:
    application = FastAPI(
        title="Shamba Signal API",
        version="0.1.0",
        description=(
            "County-year annual-label readiness for Kenya; no forecast or decision support."
        ),
    )
    application.mount("/static", StaticFiles(directory=WEB_ROOT / "static"), name="static")

    @application.get("/healthz", tags=["operations"])
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "shamba-signal-api",
            "release": get_platform_status().release,
        }

    @application.get(
        "/api/v1/platform/status",
        tags=["platform"],
        response_model=PlatformStatus,
    )
    def platform_status() -> PlatformStatus:
        return get_platform_status()

    @application.get("/", response_class=HTMLResponse, include_in_schema=False)
    def home() -> HTMLResponse:
        return HTMLResponse((WEB_ROOT / "index.html").read_text(encoding="utf-8"))

    return application


app = create_app()
