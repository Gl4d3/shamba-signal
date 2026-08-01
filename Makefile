.PHONY: install lint test validate compile smoke feasibility verify run

install:
	uv sync --locked --extra dev

lint:
	uv run ruff check src tests scripts

test:
	uv run pytest -q

validate:
	uv run python scripts/validate_repo.py

compile:
	uv run python -m compileall -q src scripts

smoke:
	uv run python scripts/smoke_api.py

feasibility:
	uv run python scripts/run_feasibility.py

verify: lint test validate compile smoke

run:
	uv run uvicorn shamba_signal.api.app:app --reload --host 127.0.0.1 --port 8000
