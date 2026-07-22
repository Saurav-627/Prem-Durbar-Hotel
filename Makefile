.PHONY: help install sync migrate makemigrations collectstatic import-data seed-data seed-conference seed-all superuser run shell backup test clean docker-up docker-down docker-logs docker-clean setup

# Default shell
SHELL := /bin/bash

# Detect uv and python path
UV := $(shell which uv 2> /dev/null)
PYTHON := $(if $(UV),uv run python,python)

help: ## Show this help message (default)
	@echo "Usage: make [target]"
	@awk ' \
		/^[a-zA-Z_-]+:.*?##/ { \
			helpMessage = match($$0, /## (.*)/); \
			if (helpMessage) { \
				helpLine = substr($$0, RSTART + 3); \
				name = $$1; \
				sub(/:$$/, "", name); \
				printf "  \033[36m%-20s\033[0m %s\n", name, helpLine; \
				} \
		} \
		/^##@/ { \
			printf "\n\033[1m%s\033[0m\n", substr($$0, 5); \
		} \
	' $(MAKEFILE_LIST)

##@ Environment & Dependency Management
install: ## Install/sync virtual environment and dependencies using uv (or fallback to pip)
	@if [ -n "$(UV)" ]; then \
		echo "Found uv. Syncing dependencies..."; \
		uv sync; \
	else \
		echo "uv not found. Using pip to install requirements..."; \
		pip install -r requirements.txt; \
	fi

sync: install ## Alias for install

##@ Development & Run
run: ## Start the local development server (accessible from other devices)
	$(PYTHON) manage.py runserver

shell: ## Open a Django shell with models and database access
	$(PYTHON) manage.py shell

collectstatic: ## Collect static files into staticfiles directory
	$(PYTHON) manage.py collectstatic --noinput --clear

##@ Database & Migrations
makemigrations: ## Generate new migrations based on model changes
	$(PYTHON) manage.py makemigrations

migrate: ## Apply database migrations
	$(PYTHON) manage.py migrate

import-data: ## Load initial currency, global settings, and header menu layout from initial_data.yaml
	$(PYTHON) manage.py import_initial_data

seed-data: ## Seed hotel sample data from seed_data.yaml (rooms, dining, activities, SEO etc.)
	$(PYTHON) manage.py seed_data

seed-all: ## Import ALL YAML data in one command (initial_data + seed_data)
	$(PYTHON) manage.py seed_all --update

superuser: ## Create an administrative superuser (interactive)
	$(PYTHON) manage.py createsuperuser

backup: ## Perform manual database backup and clean old ones (keeps last 10)
	$(PYTHON) manage.py db_backup --keep 10

##@ Docker Management
docker-up: ## Start all project services using Docker Compose in background
	docker compose up -d

docker-down: ## Stop and remove Docker containers
	docker compose down

docker-logs: ## View real-time logs from Docker containers
	docker compose logs -f

docker-clean: ## Stop Docker containers and clean persistent database/cache volumes
	docker compose down -v

##@ Testing & Maintenance
test: ## Run the test suite
	$(PYTHON) manage.py test

clean: ## Clean Python cache files (__pycache__, .pyc, .pyo)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete

setup: install migrate seed-all ## Complete one-step workspace setup (install, migrate, import ALL YAML data)
	@echo "Setup completed! Run 'make run' to start the development server."
