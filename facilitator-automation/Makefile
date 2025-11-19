.PHONY: help install dev test lint clean migrate upgrade downgrade api cli

help:
	@echo "Facilitator Automation - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Install dev dependencies and setup"
	@echo ""
	@echo "Database:"
	@echo "  make migrate    - Create new migration"
	@echo "  make upgrade    - Run migrations (upgrade to head)"
	@echo "  make downgrade  - Rollback one migration"
	@echo ""
	@echo "Run:"
	@echo "  make api        - Run API server (development mode)"
	@echo "  make cli        - Show CLI help"
	@echo ""
	@echo "Testing:"
	@echo "  make test       - Run tests"
	@echo "  make test-cov   - Run tests with coverage"
	@echo "  make lint       - Run linters"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean      - Remove temporary files"

install:
	pip install -r requirements.txt

dev: install
	@echo "Development environment ready!"
	@echo "1. Copy .env.example to .env and configure"
	@echo "2. Run: make upgrade (to run migrations)"
	@echo "3. Run: make api (to start API server)"

migrate:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

api:
	uvicorn main:app --reload --port 8080

cli:
	python cli.py --help

test:
	pytest -v

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	flake8 app --max-line-length=100 --exclude=__pycache__,alembic
	@echo "Linting complete!"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage
	@echo "Cleanup complete!"

.DEFAULT_GOAL := help
