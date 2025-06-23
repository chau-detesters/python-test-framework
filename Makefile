.PHONY: help test smoke regression integration performance clean install docker docker-build docker-test docker-smoke docker-regression ci-local coverage report security

help:  ## Toon deze help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Installeer dependencies
	pip install -r requirements.txt

test:  ## Draai alle tests
	pytest

smoke:  ## Draai smoke tests
	pytest -m smoke -v

regression:  ## Draai regression tests
	pytest -m regression -v

integration:  ## Draai integration tests
	pytest -m integration -v

performance:  ## Draai performance tests
	pytest -m performance -v -s

parallel:  ## Draai tests parallel
	pytest -n auto

clean:  ## Verwijder reports en cache
	rm -rf reports/ .pytest_cache/ .coverage htmlcov/ __pycache__/ **/__pycache__/

docker-build:  ## Build Docker image
	docker compose build test-runner

docker-test:  ## Draai tests in Docker
	docker compose up test-runner

docker-smoke:  ## Draai smoke tests in Docker
	docker compose run test-runner pytest -m smoke -v

docker-regression:  ## Draai regression tests in Docker
	docker compose run test-runner pytest -m regression -v

ci-local:  ## Simuleer CI pipeline lokaal
	TEST_ENV=ci pytest -m "smoke or regression" --html=reports/ci-report.html -v

coverage:  ## Genereer coverage rapport
	pytest --cov=src --cov-report=html --cov-report=term

report:  ## Genereer HTML/JSON rapport
	pytest --html=reports/report.html --json-report --json-report-file=reports/report.json

security:  ## Draai security checks
	pip install safety bandit
	safety check
	bandit -r src/ 