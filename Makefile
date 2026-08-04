.PHONY: install lint test validate compile smoke feasibility probe-sources verify run tabfm-test tabfm-run

install:
	uv sync --locked --extra dev

lint:
	uv run ruff check src tests scripts

test:
	uv run pytest -q

validate:
	uv run python scripts/validate_repo.py
	uv run python scripts/validate_slice2.py

compile:
	uv run python -m compileall -q src scripts

smoke:
	uv run python scripts/smoke_api.py

feasibility:
	uv run python scripts/run_feasibility.py

probe-sources:
	uv run python scripts/probe_sources.py

verify: lint test validate compile smoke

run:
	uv run uvicorn shamba_signal.api.app:app --reload --host 127.0.0.1 --port 8000

tabfm-test:
	uv run --project experiments/tabfm --extra dev pytest experiments/tabfm/tests -q

tabfm-run:
	@test -n "$(TABFM_PANEL)" || (echo "TABFM_PANEL is required" && exit 2)
	@test -n "$(TABFM_WEATHER_CACHE)" || (echo "TABFM_WEATHER_CACHE is required" && exit 2)
	uv run --project experiments/tabfm shamba-tabfm \
		--panel "$(TABFM_PANEL)" \
		--weather-cache "$(TABFM_WEATHER_CACHE)" \
		--output-root "$${TABFM_OUTPUT_ROOT:-data/processed/tabfm-experiment-v1}" \
		--device "$${TABFM_DEVICE:-auto}"
