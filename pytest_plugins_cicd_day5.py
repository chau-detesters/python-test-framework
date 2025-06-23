# Pytest Plugins & CI/CD Integration - Dag 5
# Enterprise-ready test automation met custom plugins en CI/CD

# requirements_day5.txt
"""
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-html==4.1.1
pytest-json-report==1.5.0
pytest-xdist==3.5.0
pytest-cov==4.0.0
pytest-mock==3.12.0
allure-pytest==2.13.2
requests==2.31.0
httpx==0.25.2
pydantic==2.5.0
"""

# conftest_enterprise.py - Enterprise-level conftest.py
import pytest
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import httpx

# Custom pytest hooks
def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Add custom markers
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "api: mark test as API test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "critical: mark test as critical for deployment")
    
    # Setup test environment
    config.test_start_time = time.time()
    
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

def pytest_unconfigure(config):
    """Clean up after pytest run"""
    if hasattr(config, 'test_start_time'):
        total_time = time.time() - config.test_start_time
        print(f"\nTotal test execution time: {total_time:.2f} seconds")

def pytest_collection_modifyitems(config, items):
    """Modify test collection - add markers based on test names"""
    for item in items:
        # Auto-mark API tests
        if "api" in item.name.lower() or "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        
        # Auto-mark slow tests
        if "slow" in item.name.lower() or "performance" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # Auto-mark integration tests
        if "integration" in item.name.lower() or "workflow" in item.name.lower():
            item.add_marker(pytest.mark.integration)

def pytest_runtest_makereport(item, call):
    """Create custom test reports"""
    if call.when == "call":
        # Add custom attributes to test report
        setattr(item, "test_execution_time", call.duration)
        
        # Log failed test details
        if call.excinfo is not None:
            test_name = item.name
            error_info = str(call.excinfo.value)
            print(f"\nFAILED TEST: {test_name}")
            print(f"ERROR: {error_info}")

# Session-level fixtures
@pytest.fixture(scope="session")
def test_session_info():
    """Provide test session information"""
    return {
        "start_time": datetime.now(),
        "environment": os.getenv("TEST_ENV", "local"),
        "build_id": os.getenv("BUILD_ID", "local"),
        "git_commit": os.getenv("GIT_COMMIT", "unknown")
    }

@pytest.fixture(scope="session")
def global_test_config():
    """Global test configuration"""
    return {
        "base_url": os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com"),
        "timeout": int(os.getenv("API_TIMEOUT", "30")),
        "retries": int(os.getenv("API_RETRIES", "3")),
        "parallel_workers": int(os.getenv("PARALLEL_WORKERS", "4"))
    }

@pytest.fixture(scope="session")
async def global_http_client(global_test_config):
    """Global HTTP client for the entire test session"""
    async with httpx.AsyncClient(
        base_url=global_test_config["base_url"],
        timeout=global_test_config["timeout"]
    ) as client:
        yield client

# Custom pytest plugin - pytest_custom_plugin.py
import pytest
import json
import time
from typing import Dict, List, Any
from pathlib import Path

class TestMetricsCollector:
    """Collect test execution metrics"""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.start_time = time.time()
    
    def add_test_result(self, test_name: str, status: str, duration: float, error: str = None):
        """Add a test result to the collection"""
        self.test_results.append({
            "test_name": test_name,
            "status": status,
            "duration": duration,
            "error": error,
            "timestamp": time.time()
        })
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASSED"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAILED"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIPPED"])
        
        total_duration = sum(r["duration"] for r in self.test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": passed_tests / total_tests * 100 if total_tests > 0 else 0,
                "total_duration": total_duration,
                "average_duration": avg_duration
            },
            "test_results": self.test_results,
            "generated_at": time.time()
        }

# Plugin implementation
metrics_collector = TestMetricsCollector()

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Hook to collect test metrics"""
    if call.when == "call":
        status = "PASSED" if call.excinfo is None else "FAILED"
        error = str(call.excinfo.value) if call.excinfo else None
        
        metrics_collector.add_test_result(
            test_name=item.nodeid,
            status=status,
            duration=call.duration,
            error=error
        )

def pytest_sessionfinish(session, exitstatus):
    """Generate final report when session finishes"""
    report = metrics_collector.generate_report()
    
    # Save JSON report
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    with open(reports_dir / "metrics_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    summary = report["summary"]
    print(f"\n{'='*50}")
    print(f"TEST EXECUTION SUMMARY")
    print(f"{'='*50}")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Total Duration: {summary['total_duration']:.2f}s")
    print(f"Average Duration: {summary['average_duration']:.3f}s")
    print(f"{'='*50}")

# test_enterprise_patterns.py - Enterprise testing patterns
import pytest
import asyncio
import time
from typing import Dict, Any, List
import httpx

@pytest.mark.api
@pytest.mark.smoke
class TestEnterpriseAPI:
    """Enterprise-level API testing patterns"""
    
    @pytest.mark.critical
    async def test_health_check(self, global_http_client):
        """Critical health check test"""
        response = await global_http_client.get("/users/1")
        assert response.status_code == 200, "API health check failed"
    
    @pytest.mark.regression
    async def test_user_crud_operations(self, global_http_client, user_factory):
        """Complete CRUD operations test"""
        # Create
        user_data = user_factory.create_user()
        create_response = await global_http_client.post("/users", json=user_data)
        assert create_response.status_code == 201
        
        # Read
        read_response = await global_http_client.get("/users/1")
        assert read_response.status_code == 200
        
        # Update (PUT)
        updated_data = user_factory.create_user(name="Updated Name")
        update_response = await global_http_client.put("/users/1", json=updated_data)
        assert update_response.status_code == 200
        
        # Delete
        delete_response = await global_http_client.delete("/users/1")
        assert delete_response.status_code == 200

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_load_performance(self, global_http_client):
        """Load performance test"""
        num_requests = 50
        max_concurrent = 10
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def make_request(user_id):
            async with semaphore:
                start_time = time.time()
                response = await global_http_client.get(f"/users/{user_id % 10 + 1}")
                end_time = time.time()
                return response.status_code, end_time - start_time
        
        start_time = time.time()
        tasks = [make_request(i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Analyze results
        success_count = sum(1 for status, _ in results if status == 200)
        response_times = [duration for _, duration in results]
        avg_response_time = sum(response_times) / len(response_times)
        
        # Assertions
        assert success_count == num_requests, f"Only {success_count}/{num_requests} requests succeeded"
        assert avg_response_time < 2.0, f"Average response time {avg_response_time:.3f}s too high"
        assert total_time < 30.0, f"Total execution time {total_time:.3f}s too high"
        
        # Performance metrics for reporting
        pytest.current_test_metrics = {
            "requests_per_second": num_requests / total_time,
            "average_response_time": avg_response_time,
            "success_rate": success_count / num_requests * 100
        }

# CI/CD configuration files

# .github/workflows/tests.yml - GitHub Actions workflow
GITHUB_WORKFLOW = """
name: Test Automation Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
        test-suite: [smoke, regression, integration]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements_day5.txt
    
    - name: Run ${{ matrix.test-suite }} tests
      env:
        TEST_ENV: ci
        API_BASE_URL: https://jsonplaceholder.typicode.com
        PARALLEL_WORKERS: 4
      run: |
        pytest -m ${{ matrix.test-suite }} \\
               --html=reports/report-${{ matrix.test-suite }}.html \\
               --json-report --json-report-file=reports/report-${{ matrix.test-suite }}.json \\
               --cov=src --cov-report=xml \\
               --maxfail=5 \\
               -n auto
    
    - name: Upload test reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-reports-${{ matrix.python-version }}-${{ matrix.test-suite }}
        path: reports/
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true

  performance:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements_day5.txt
    
    - name: Run performance tests
      env:
        TEST_ENV: ci
        API_BASE_URL: https://jsonplaceholder.typicode.com
      run: |
        pytest -m performance \\
               --html=reports/performance-report.html \\
               --json-report --json-report-file=reports/performance-report.json \\
               -v -s
    
    - name: Performance analysis
      run: |
        python scripts/analyze_performance.py reports/performance-report.json

  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      run: |
        pip install safety bandit
        safety check --json --output reports/safety-report.json || true
        bandit -r src/ -f json -o reports/bandit-report.json || true
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: reports/
"""

# docker/Dockerfile - Docker container for tests
DOCKERFILE = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_day5.txt .
RUN pip install --no-cache-dir -r requirements_day5.txt

# Copy test code
COPY . .

# Create reports directory
RUN mkdir -p reports

# Set environment variables
ENV PYTHONPATH=/app
ENV TEST_ENV=docker

# Default command
CMD ["pytest", "--html=reports/report.html", "--json-report", "--json-report-file=reports/report.json", "-v"]
"""

# docker-compose.yml - Docker Compose for test environment
DOCKER_COMPOSE = """
version: '3.8'

services:
  test-runner:
    build: 
      context: .
      dockerfile: docker/Dockerfile
    environment:
      - TEST_ENV=docker
      - API_BASE_URL=https://jsonplaceholder.typicode.com
      - PARALLEL_WORKERS=4
    volumes:
      - ./reports:/app/reports
      - ./src:/app/src
      - ./tests:/app/tests
    command: >
      pytest 
        --html=reports/report.html 
        --json-report --json-report-file=reports/report.json
        --cov=src --cov-report=html --cov-report=xml
        -n auto
        -v

  smoke-tests:
    extends: test-runner
    command: >
      pytest -m smoke
        --html=reports/smoke-report.html
        --json-report --json-report-file=reports/smoke-report.json
        -v

  regression-tests:
    extends: test-runner
    command: >
      pytest -m regression
        --html=reports/regression-report.html
        --json-report --json-report-file=reports/regression-report.json
        -n auto
        -v

  performance-tests:
    extends: test-runner
    command: >
      pytest -m performance
        --html=reports/performance-report.html
        --json-report --json-report-file=reports/performance-report.json
        -v -s
"""

# scripts/analyze_performance.py - Performance analysis script
PERFORMANCE_ANALYZER = """
#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

def analyze_performance_report(report_path: str):
    \"\"\"Analyze performance test results\"\"\"
    
    with open(report_path) as f:
        report = json.load(f)
    
    tests = report.get('tests', [])
    performance_tests = [t for t in tests if 'performance' in t.get('nodeid', '').lower()]
    
    print("\\nPerformance Analysis Report")
    print("=" * 40)
    
    if not performance_tests:
        print("No performance tests found")
        return
    
    total_duration = sum(t.get('duration', 0) for t in performance_tests)
    avg_duration = total_duration / len(performance_tests)
    
    print(f"Total Performance Tests: {len(performance_tests)}")
    print(f"Average Test Duration: {avg_duration:.3f}s")
    print(f"Total Duration: {total_duration:.3f}s")
    
    # Find slowest tests
    slowest_tests = sorted(performance_tests, key=lambda x: x.get('duration', 0), reverse=True)[:5]
    
    print("\\nSlowest Tests:")
    for i, test in enumerate(slowest_tests, 1):
        print(f"{i}. {test.get('nodeid', 'Unknown')}: {test.get('duration', 0):.3f}s")
    
    # Check for failures
    failed_tests = [t for t in performance_tests if t.get('outcome') == 'failed']
    if failed_tests:
        print(f"\\nFailed Performance Tests: {len(failed_tests)}")
        for test in failed_tests:
            print(f"- {test.get('nodeid', 'Unknown')}")
    
    # Performance thresholds
    slow_threshold = 5.0  # seconds
    slow_tests = [t for t in performance_tests if t.get('duration', 0) > slow_threshold]
    
    if slow_tests:
        print(f"\\nTests exceeding {slow_threshold}s threshold:")
        for test in slow_tests:
            print(f"- {test.get('nodeid', 'Unknown')}: {test.get('duration', 0):.3f}s")
    
    print("\\nAnalysis complete.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_performance.py <report.json>")
        sys.exit(1)
    
    analyze_performance_report(sys.argv[1])
"""

# pytest.ini - Complete pytest configuration
PYTEST_INI = """
[tool:pytest]
minversion = 7.0
addopts = 
    --strict-markers
    --strict-config
    --html=reports/report.html
    --self-contained-html
    --json-report
    --json-report-file=reports/report.json
    --cov=src
    --cov-report=html:reports/htmlcov
    --cov-report=xml:reports/coverage.xml
    --cov-report=term-missing
    --tb=short
    --maxfail=10
    -ra

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    smoke: Quick smoke tests for basic functionality
    regression: Comprehensive regression tests
    integration: Integration tests across multiple components
    performance: Performance and load tests
    api: API-specific tests
    slow: Tests that take longer than 5 seconds
    critical: Critical tests that must pass for deployment
    skip_prod: Tests that should not run in production
    unit: Unit tests
    
filterwarnings =
    ignore::urllib3.exceptions.InsecureRequestWarning
    ignore::DeprecationWarning

asyncio_mode = auto

# Parallel execution
# Use with: pytest -n auto
"""

# Makefile - Common commands
MAKEFILE = """
.PHONY: help test smoke regression integration performance clean install docker

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements_day5.txt

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

clean:  ## Clean up reports and cache
	rm -rf reports/ .pytest_cache/ .coverage htmlcov/ __pycache__/ **/__pycache__/

docker-build:  ## Build Docker image
	docker build -f docker/Dockerfile -t test-automation .

docker-test:  ## Run tests in Docker
	docker-compose up test-runner

docker-smoke:  ## Run smoke tests in Docker
	docker-compose up smoke-tests

docker-regression:  ## Run regression tests in Docker
	docker-compose up regression-tests

ci-local:  ## Simulate CI environment locally
	TEST_ENV=ci pytest -m "smoke or regression" --html=reports/ci-report.html -v

coverage:  ## Generate coverage report
	pytest --cov=src --cov-report=html --cov-report=term

report:  ## Generate comprehensive test report
	pytest --html=reports/report.html --json-report --json-report-file=reports/report.json

security:  ## Run security checks
	safety check
	bandit -r src/
"""