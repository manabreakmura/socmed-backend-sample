dev:
	fastapi dev src/main.py

test:
	mypy && ruff check && ruff format --check && pytest

sec:
	bandit -c pyproject.toml -r .
