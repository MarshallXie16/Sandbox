.PHONY: help install dev test lint format clean migrate upgrade

help:
	@echo "Capitalink Analytics - Makefile Commands"
	@echo ""
	@echo "  install    Install production dependencies"
	@echo "  dev        Run development server with auto-reload"
	@echo "  test       Run tests"
	@echo "  lint       Run linters (flake8)"
	@echo "  format     Format code (black, isort)"
	@echo "  clean      Remove generated files"
	@echo "  migrate    Create a new Alembic migration"
	@echo "  upgrade    Run Alembic migrations"
	@echo "  cli        Access analytics CLI"
	@echo ""

install:
	pip install -r requirements.txt

dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8008

test:
	pytest -v --cov=app --cov-report=term-missing

lint:
	flake8 app tests

format:
	black app tests
	isort app tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache htmlcov .coverage

migrate:
	alembic revision --autogenerate -m "$(message)"

upgrade:
	alembic upgrade head

cli:
	python cli.py
