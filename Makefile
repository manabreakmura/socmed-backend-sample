dev:
	uv run fastapi dev src/main.py

lint:
	uv run ruff check && uv run ruff format --check && uv run ty check

test:
	uv run pytest

install:
	uv sync

upgrade:
	uv sync --upgrade

ci: install lint test