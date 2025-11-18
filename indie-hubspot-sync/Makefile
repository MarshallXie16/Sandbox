# Makefile for indie-hubspot-sync

.PHONY: help install test lint format clean run-api run-cli init

# Default target
help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make init       - Initialize tracking database"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linters"
	@echo "  make format     - Format code"
	@echo "  make run-api    - Start API server"
	@echo "  make run-cli    - Show CLI help"
	@echo "  make sync       - Run sync (all entities)"
	@echo "  make clean      - Remove generated files"

# Install dependencies
install:
	pip install -r requirements.txt

# Initialize database
init:
	python sync_cli.py init

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ --cov=app --cov-report=html --cov-report=term

# Lint code
lint:
	flake8 app/ tests/
	mypy app/

# Format code
format:
	black app/ tests/
	isort app/ tests/

# Run API server (development)
run-api:
	uvicorn app.api.main:app --reload --port 8000

# Run API server (production)
run-api-prod:
	uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Show CLI help
run-cli:
	python sync_cli.py --help

# Run sync
sync:
	python sync_cli.py sync-all

# Dry run sync
sync-dry:
	python sync_cli.py sync-all --dry-run

# Clean generated files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

# Development setup
dev-setup: install init
	@echo "Development environment ready!"
	@echo "Run 'make run-api' to start the API server"
	@echo "Run 'make sync-dry' to test a sync"

# Production setup
prod-setup: install init
	@echo "Production environment ready!"
	@echo "Configure .env with production credentials"
	@echo "Run 'make run-api-prod' to start the API server"
