# Test Directory Structure

This directory contains all test files for the Python Test Framework project. The tests are organized by type and functionality.

---

## 📈 Code Coverage (for Beginners)

**Code coverage** measures how much of your code is exercised by your tests. High coverage helps ensure your code is well-tested and less likely to have hidden bugs.

### Why is coverage important?
- It shows which parts of your code are tested and which are not.
- Helps you find untested edge cases.
- Encourages writing more robust tests.

### How to check coverage

1. **Install dependencies** (if you haven't already):
   ```bash
   pip install -r requirements-dev.txt
   ```
   This will install `pytest`, `pytest-cov`, and other tools.

2. **Run all tests with coverage:**
   ```bash
   pytest --cov=src --cov-report=term-missing -v
   ```
   - `--cov=src` tells pytest to measure coverage for the `src/` directory.
   - `--cov-report=term-missing` shows which lines are not covered.
   - `-v` gives verbose output.

3. **Generate an HTML coverage report (optional):**
   ```bash
   pytest --cov=src --cov-report=html
   ```
   - This creates an `htmlcov/` folder. Open `htmlcov/index.html` in your browser to see a visual report.

#### Example output
```
---------- coverage: platform darwin, python 3.11.8 ----------
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
src/openapi_client.py         180      0   100%
...
---------------------------------------------------------
TOTAL                        900      0   100%
```

#### Troubleshooting
- If you see `ModuleNotFoundError`, make sure you installed all dependencies.
- If coverage is less than 100%, check the `Missing` column for lines not covered and add tests for them.
- If you want to test a specific file or folder, use:
  ```bash
  pytest --cov=src/path/to/file.py
  ```

---

## Directory Organization

```
tests/
├── integration/          # Integration tests
│   ├── graphql/         # GraphQL-specific tests
│   │   ├── test_graphql_queries.py
│   │   └── test_graphql_mutations.py
│   ├── test_schema_drift_detection.py
│   └── test_openapi_validation.py
├── unit/                # Unit tests
│   └── test_enterprise_patterns.py
├── performance/         # Performance tests
│   └── test_performance.py
├── security/           # Security tests
│   └── test_security.py
├── async/              # Async-specific tests
│   └── test_user_service_consumer.py
├── data_driven/        # Data-driven tests
│   └── test_provider_verification.py
├── data/               # Test data and fixtures
│   └── test_fixtures/
└── conftest.py         # Shared pytest fixtures and configuration

```

## Test Categories

1. **Integration Tests** (`integration/`)
   - GraphQL API tests
   - Schema validation
   - OpenAPI compliance tests

2. **Unit Tests** (`unit/`)
   - Enterprise pattern tests
   - Individual component tests

3. **Performance Tests** (`performance/`)
   - Response time tests
   - Load testing
   - Benchmarking

4. **Security Tests** (`security/`)
   - Authentication tests
   - Authorization tests
   - Security vulnerability checks

5. **Async Tests** (`async/`)
   - Asynchronous operation tests
   - WebSocket tests
   - Event-driven tests

6. **Data-Driven Tests** (`data_driven/`)
   - Provider verification
   - Parameterized tests
   - Data validation tests

## Configuration

The `conftest.py` file contains shared pytest fixtures and configurations, including:
- HTTP client fixtures
- Test data factories
- Environment configurations
- Cleanup utilities
- Mock objects

## Running Tests

To run all tests:
```bash
pytest
```

To run tests in a specific directory:
```bash
pytest tests/integration/
pytest tests/performance/
```

To run tests with specific markers:
```bash
pytest -m "slow"
pytest -m "integration"
``` 