.PHONY: install lint test validate compile smoke feasibility probe-sources verify run

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
