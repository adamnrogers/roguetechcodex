.PHONY: build up down pipeline logs logs-api shell-api shell-pipeline fresh ps help \
        dev dev-down dev-build dev-pipeline dev-logs \
        standalone-run standalone-build portraits portraits-zip \
        copy-db

# Load .env if present
ifneq (,$(wildcard .env))
  include .env
  export
endif

COMPOSE     = docker compose -f docker-compose.yml
COMPOSE_DEV = docker compose -f docker-compose.yml -f docker-compose.dev.yml

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

# ── Production ────────────────────────────────────────────────────────────────

build: ## Build all Docker images
	$(COMPOSE) build

up: ## Start api and frontend in production mode (requires roguetech.db)
	$(COMPOSE) up api frontend

down: ## Stop all services
	$(COMPOSE) down

pipeline: ## Run data ingestion pipeline (rebuilds roguetech.db)
	$(COMPOSE) --profile pipeline run --rm pipeline python -m pipeline.ingest --full-rebuild

fresh: ## Full rebuild: re-ingest data then start services
	$(COMPOSE) --profile pipeline run --rm pipeline python -m pipeline.ingest --full-rebuild
	$(COMPOSE) up api frontend

logs: ## Tail logs for all running services
	$(COMPOSE) logs -f

logs-api: ## Tail api logs only
	$(COMPOSE) logs -f api

shell-api: ## Open a shell in the running api container
	$(COMPOSE) exec api /bin/bash

shell-pipeline: ## Run an interactive pipeline shell (useful for debugging)
	$(COMPOSE) run --rm pipeline /bin/bash

ps: ## Show running containers
	$(COMPOSE) ps

# ── Development (source-mounted, hot reload) ──────────────────────────────────

dev: ## Start dev servers with hot reload — no image rebuild needed for code changes
	$(COMPOSE_DEV) up api frontend

dev-down: ## Stop dev services
	$(COMPOSE_DEV) down

dev-build: ## Rebuild dev images (run after requirements.txt or package.json changes)
	$(COMPOSE_DEV) build api frontend

dev-pipeline: ## Run pipeline in dev mode (source-mounted)
	$(COMPOSE_DEV) --profile pipeline run --rm pipeline python -m pipeline.ingest --full-rebuild

dev-logs: ## Tail dev logs
	$(COMPOSE_DEV) logs -f

# ── Standalone ────────────────────────────────────────────────────────────────

standalone-run: ## Run standalone mode locally — no exe, builds frontend then serves API + SPA
	cd frontend/src && npm run build
	PYTHONPATH=. python3 -m standalone

standalone-build: ## Build standalone exe with PyInstaller (requires roguetech.db at repo root)
	pip3 install pyinstaller
	pip3 install -r api/requirements.txt
	cd frontend/src && npm run build
	pyinstaller standalone/roguetech.spec

copy-db: ## Copy rebuilt DB from the db_data volume to ./roguetech.db (run after make pipeline or make dev-pipeline)
	$(COMPOSE) --profile pipeline run --rm --no-deps \
		-v "$(CURDIR)":/out \
		--entrypoint cp pipeline /data/db/roguetech.db /out/roguetech.db

portraits: ## Convert DDS portraits for dev/Docker → frontend/src/public/portraits/
	pip3 install -r pipeline/requirements.txt -q
	python3 pipeline/portraits.py --output-dir portraits

portraits-zip: ## Build portraits.zip for standalone release
	rm -rf portraits-staging
	pip3 install -r pipeline/requirements.txt -q
	python3 pipeline/portraits.py --output-dir portraits-staging/portraits
	python3 -c "import shutil; shutil.make_archive('portraits', 'zip', 'portraits-staging', 'portraits')"
	rm -rf portraits-staging
	@echo "portraits.zip ready for release"
