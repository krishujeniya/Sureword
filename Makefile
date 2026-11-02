.PHONY: help install dev test lint format typecheck validate evaluate clean docker-build docker-run

PYTHON ?= uv run python
UV ?= uv

help:
	@echo "FieldCheck — Developer Operations"
	@echo "================================="
	@echo "make install       Install dependencies in editable development mode"
	@echo "make dev           Run local FastAPI development server (uvicorn)"
	@echo "make test          Run pytest suite across unit and integration tests"
	@echo "make lint          Run static linting with Ruff"
	@echo "make format        Format codebase with Ruff"
	@echo "make typecheck     Run strict static type analysis with Mypy"
	@echo "make validate      Validate held-out test and dev dataset manifests"
	@echo "make evaluate      Run deterministic benchmark evaluation"
	@echo "make clean         Remove build, cache, and test artifacts"
	@echo "make docker-build  Build production Docker image"
	@echo "make docker-run    Run Docker container on port 8000"

install:
	$(UV) pip install -e ".[dev]"

dev:
	$(PYTHON) -m uvicorn fieldcheck.app:app --host 127.0.0.1 --port 8000 --reload

test:
	$(PYTHON) -m pytest tests/ -v

lint:
	$(PYTHON) -m ruff check src tests scripts

format:
	$(PYTHON) -m ruff format src tests scripts

typecheck:
	$(PYTHON) -m mypy src tests

validate:
	$(PYTHON) scripts/validate_manifest.py --dev data/manifests/dev.jsonl --test data/manifests/test.jsonl

evaluate:
	$(PYTHON) scripts/evaluate.py --config configs/experiment.json --manifest data/manifests/test.jsonl --output artifacts/ci_eval

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	rm -rf .pytest_cache .ruff_cache .mypy_cache dist build artifacts/ci_eval fieldcheck.db

docker-build:
	docker build -t fieldcheck:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env fieldcheck:latest
