.PHONY: help test smoke regression integration performance clean install docker docker-build docker-test docker-smoke docker-regression ci-local coverage report security

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

test:  ## Run all tests
	pytest

smoke:  ## Run smoke tests
	pytest -m smoke -v

regression:  ## Run regression tests
	pytest -m regression -v

integration:  ## Run integration tests
	pytest -m integration -v

performance:  ## Run performance tests
	pytest -m performance -v -s

parallel:  ## Run tests in parallel
	pytest -n auto

clean:  ## Remove reports and cache
	rm -rf reports/ .pytest_cache/ .coverage htmlcov/ __pycache__/ **/__pycache__/

docker-build:  ## Build Docker image
	docker compose build test-runner

docker-test:  ## Run tests in Docker
	docker compose up test-runner

docker-smoke:  ## Run smoke tests in Docker
	docker compose run test-runner pytest -m smoke -v

docker-regression:  ## Run regression tests in Docker
	docker compose run test-runner pytest -m regression -v

ci-local:  ## Simulate CI pipeline locally
	TEST_ENV=ci pytest -m "smoke or regression" --html=reports/ci-report.html -v

coverage:  ## Generate coverage report
	pytest --cov=src --cov-report=html --cov-report=term

report:  ## Generate HTML/JSON report
	pytest --html=reports/report.html --json-report --json-report-file=reports/report.json

security:  ## Run security checks
	pip install safety bandit
	safety check
	bandit -r src/ 