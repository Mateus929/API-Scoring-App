.PHONY: help
.DEFAULT_GOAL := help

help:
	python3 -m n2t --help

install: ## Install requirements
	python3 -m pip install --upgrade pip
	python3 -m pip install --upgrade poetry
	poetry install --no-root

lock: ## Lock project dependencies
	poetry lock

update: ## Update project dependencies
	poetry update

format: ## Run code formatters
	poetry run ruff format src tests
	poetry run ruff check  src tests --fix

lint: ## Run code linters
	poetry run ruff format src tests --check
	poetry run ruff check  src tests
	poetry run mypy src tests
