PYTHON ?= python3

.PHONY: install test lint verify run validate

install:
	uv sync --extra dev

test:
	PYTHONPATH=src $(PYTHON) -m pytest

lint:
	uv run ruff check src tests scripts

validate:
	PYTHONPATH=src $(PYTHON) scripts/validate_repo.py

verify: test validate
	PYTHONPATH=src $(PYTHON) -m compileall -q src scripts

run:
	PYTHONPATH=src $(PYTHON) -m uvicorn shamba_signal.api.app:app --reload --host 127.0.0.1 --port 8000
