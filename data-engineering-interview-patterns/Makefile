.PHONY: setup test test-cov lint format clean

setup:
	uv sync

test:
	uv run pytest -v

test-cov:
	uv run pytest --cov=patterns --cov-report=html

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
	uv run ruff check --fix .

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache htmlcov .coverage
