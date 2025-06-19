# Tunda Soko Backend - E2E Testing Commands

.PHONY: help install-e2e setup-e2e test-e2e test-auth test-workflow test-api clean-e2e

help: ## Show this help message
	@echo "Tunda Soko E2E Testing Commands"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-e2e: ## Install E2E testing dependencies
	pip install -r requirements-e2e.txt
	@echo "✅ E2E testing dependencies installed"

setup-e2e: ## Setup E2E test environment
	python tests/db_setup.py setup
	@echo "✅ E2E test environment setup completed"

test-e2e: ## Run all E2E tests
	python tests/run_e2e.py

test-auth: ## Run authentication tests only
	python tests/run_e2e.py --marker auth

test-workflow: ## Run workflow tests only
	python tests/run_e2e.py --marker workflow

test-api: ## Run API integration tests only
	python tests/run_e2e.py --marker api

test-fast: ## Run E2E tests excluding slow tests
	pytest tests/e2e/ -v -m "e2e and not slow"

test-debug: ## Run E2E tests with debug output
	pytest tests/e2e/ -v -s -m e2e

clean-e2e: ## Clean up E2E test data
	python tests/db_setup.py cleanup
	@echo "✅ E2E test data cleaned up"

reset-e2e: clean-e2e setup-e2e ## Reset E2E test environment
	@echo "🔄 E2E test environment reset completed"

# Development shortcuts
dev-server: ## Start Django development server
	python manage.py runserver

dev-test: ## Run E2E tests with server check skipped (assumes server is running)
	python tests/run_e2e.py --skip-server-check

# CI/CD commands
ci-test: ## Run E2E tests for CI/CD (no cleanup)
	python tests/run_e2e.py --skip-cleanup

coverage: ## Run E2E tests with coverage report
	pytest tests/e2e/ -v -m e2e --cov=. --cov-report=html:tests/reports/coverage --cov-report=term-missing

# Quick test commands
test-user-reg: ## Test user registration workflow
	python tests/run_e2e.py --test test_auth_workflow.py::TestUserRegistrationWorkflow

test-user-login: ## Test user login workflow
	python tests/run_e2e.py --test test_auth_workflow.py::TestUserLoginWorkflow

test-marketplace: ## Test complete marketplace workflow
	python tests/run_e2e.py --test test_marketplace_workflow.py::TestCompleteMarketplaceWorkflow 