install:
	uv sync

dev:
	fastapi dev src/main.py

lint:
	ruff check && ruff format --check && mypy

test:
	pytest

sec:
	bandit -c pyproject.toml -r .

ci: install lint test sec