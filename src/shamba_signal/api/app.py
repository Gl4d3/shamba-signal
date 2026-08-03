import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from shamba_signal.domain.platform import PlatformStatus
from shamba_signal.services.platform_status import get_platform_status

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = PACKAGE_ROOT / "web"


def create_app(evaluation_fixture_path: Path | None = None) -> FastAPI:
    application = FastAPI(
        title="Shamba Signal API",
        version="0.1.0",
        description=(
            "Kenya county-year maize evidence and retrospective model evaluation; "
            "no operational forecast or decision support."
        ),
    )
    application.mount("/static", StaticFiles(directory=WEB_ROOT / "static"), name="static")
    fixture_path = evaluation_fixture_path or Path(
        "data/processed/weather-experiment-v1/evaluation_fixture.json"
    )

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

    @application.get("/api/v1/evaluation", tags=["evidence"])
    def evaluation() -> dict[str, object]:
        if not fixture_path.is_file():
            raise HTTPException(
                status_code=503,
                detail="The private evaluation fixture is not available in this checkout.",
            )
        try:
            payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=503, detail="Evaluation fixture is unreadable."
            ) from exc
        if not isinstance(payload, dict):
            raise HTTPException(status_code=503, detail="Evaluation fixture is invalid.")
        return payload

    @application.get("/", response_class=HTMLResponse, include_in_schema=False)
    def home() -> HTMLResponse:
        return HTMLResponse((WEB_ROOT / "index.html").read_text(encoding="utf-8"))

    return application


app = create_app()
