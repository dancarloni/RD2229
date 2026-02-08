# Makefile per automatizzare operazioni comuni di sviluppo

.PHONY: help install install-dev test lint format type-check clean docs pre-commit install-pre-commit

help: ## Mostra questo messaggio di aiuto
	@echo "Comandi disponibili:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Installa le dipendenze di produzione
	pip install -r requirements.txt

install-dev: ## Installa le dipendenze di sviluppo
	pip install -r requirements-dev.txt

install-pre-commit: ## Installa i pre-commit hooks
	pre-commit install

test: ## Esegue tutti i test
	pytest

test-cov: ## Esegue i test con coverage
	pytest --cov=src --cov=sections_app --cov-report=html --cov-report=term

lint: ## Esegue il linting del codice
	ruff check .

format: ## Formatta il codice
	ruff format .
	ruff check . --fix

type-check: ## Esegue il type checking con mypy
	mypy .

security: ## Esegue controlli di sicurezza
	bandit -r src sections_app

pre-commit: ## Esegue tutti i pre-commit hooks
	pre-commit run --all-files

clean: ## Pulisce i file generati
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

docs: ## Costruisce la documentazione
	mkdocs build

docs-serve: ## Serve la documentazione in locale
	mkdocs serve

requirements: ## Aggiorna i requirements files con pip-tools
	pip-compile requirements.in -o requirements.txt
	pip-compile requirements-dev.in -o requirements-dev.txt

check-all: lint type-check security test ## Esegue tutti i controlli (lint, type-check, security, test)

ci: check-all ## Pipeline CI completa