# Homologador Makefile

.PHONY: help install install-dev test lint format type-check build clean run

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies  
	pip install -e ".[dev]"

test:  ## Run tests
	pytest tests/ -v

lint:  ## Run linting
	flake8 homologador/
	isort --check-only homologador/
	black --check homologador/

format:  ## Format code
	isort homologador/
	black homologador/

type-check:  ## Run type checking
	mypy homologador/

build:  ## Build executable
	python scripts/final_compile.py

clean:  ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

run:  ## Run application
	python -m homologador

dev-setup:  ## Complete development setup
	$(MAKE) install-dev
	$(MAKE) format 
	$(MAKE) type-check
	$(MAKE) test
