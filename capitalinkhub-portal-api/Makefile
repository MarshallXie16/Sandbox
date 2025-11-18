.PHONY: help dev test lint format clean install init-db migrate

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

dev:  ## Run development server with auto-reload
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ --cov=app --cov-report=html --cov-report=term

lint:  ## Run linting checks
	@echo "Running flake8..."
	flake8 app/ --max-line-length=100 --exclude=__pycache__,*.pyc,.pytest_cache
	@echo "Running mypy..."
	mypy app/ --ignore-missing-imports

format:  ## Format code with black
	black app/ tests/ portal_cli.py main.py

init-db:  ## Initialize database tables
	python portal_cli.py portal init-db

migrate:  ## Run database migrations
	alembic upgrade head

create-migration:  ## Create a new migration (use: make create-migration msg="description")
	alembic revision --autogenerate -m "$(msg)"

api-key:  ## Generate a new API key
	python portal_cli.py portal create-api-key

members-list:  ## List portal members
	python portal_cli.py members list

clean:  ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage

shell:  ## Open Python shell with app context
	python -i -c "from app.core.config import settings; from app.core.database import get_engine; print('Portal API shell loaded')"
