# Retro High-Score Arcade - development commands.
# Run "make help" to see all targets. Each recipe shows the underlying command.

.DEFAULT_GOAL := help
.PHONY: help install up up-d down down-v seed lint lint-python lint-frontend \
        test test-unit test-integration test-e2e clean

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-18s %s\n", $$1, $$2}'

install: ## Install all dependencies (Python via uv + Node via npm)
	cd auth && uv sync --extra dev
	cd backend && uv sync --extra dev
	cd frontend && npm install
	cd e2e && npm install && npx playwright install --with-deps chromium

up: ## Start the full stack (docker compose up --build)
	docker compose up --build

up-d: ## Start the stack in the background
	docker compose up --build -d

down: ## Stop the stack
	docker compose down

down-v: ## Stop the stack and wipe the database volume
	docker compose down -v

seed: ## Populate the DB with mock players and scores (stack must be up)
	python3 scripts/seed_demo_data.py

lint-python: ## Ruff lint on backend/ and auth/
	cd backend && uv run ruff check app/ tests/
	cd auth && uv run ruff check app/ tests/

lint-frontend: ## ESLint on frontend/src/
	cd frontend && npm run lint

lint: lint-python lint-frontend ## Lint all services

test-unit: ## Unit tests (pytest + vitest, no running services needed)
	cd backend && uv run pytest tests/unit/ -v
	cd auth && uv run pytest tests/unit/ -v
	cd frontend && npm test -- --reporter=verbose

test-integration: ## Integration tests (pytest -m integration + vitest)
	cd backend && uv run pytest tests/integration/ -v -m integration
	cd auth && uv run pytest tests/integration/ -v -m integration
	cd frontend && npm test -- --reporter=verbose

test-e2e: ## E2E tests (Playwright; requires the compose stack running)
	cd e2e && npx playwright test

test: test-unit test-integration test-e2e ## Run all test tiers

clean: ## Remove caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf frontend/node_modules frontend/dist
	rm -rf e2e/node_modules e2e/playwright-report e2e/test-results
