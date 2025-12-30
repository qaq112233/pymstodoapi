.PHONY: help install install-dev test test-cov lint format security clean docker-build docker-run

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r api_requirements.txt

install-dev:  ## Install development dependencies
	pip install -r api_requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ --cov=api --cov-report=html --cov-report=term-missing

lint:  ## Run linters
	flake8 api/ tests/
	mypy api/ --ignore-missing-imports || true

format:  ## Format code
	black api/ tests/
	isort api/ tests/

format-check:  ## Check code formatting
	black --check api/ tests/
	isort --check-only api/ tests/

security:  ## Run security checks
	bandit -r api/ -ll
	safety check || true

clean:  ## Clean up temporary files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf htmlcov/ .coverage coverage.xml
	rm -rf dist/ build/ *.egg-info

docker-build:  ## Build Docker image
	docker build -t pymstodoapi:latest .

docker-run:  ## Run Docker container
	docker run -d -p 8000:8000 --env-file .env --name pymstodoapi pymstodoapi:latest

docker-stop:  ## Stop Docker container
	docker stop pymstodoapi && docker rm pymstodoapi

docker-logs:  ## View Docker logs
	docker logs -f pymstodoapi

docker-compose-up:  ## Start services with docker-compose
	docker-compose up -d --build

docker-compose-down:  ## Stop services with docker-compose
	docker-compose down

dev:  ## Run development server
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

check-all: format-check lint security test  ## Run all checks

ci: install-dev check-all  ## Run CI pipeline locally
