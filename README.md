[![Test Automation Pipeline](https://github.com/chaunguyen/python-test-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/chaunguyen/python-test-framework/actions/workflows/ci.yml)

# Python Test Framework

A modern, enterprise-ready Python test framework for API and backend testing. Supports async, parametrized, data-driven, mocking, metrics, parallelization, and advanced enterprise test patterns.

---

## 🐣 Prerequisites

- Python 3.9 or higher (check with `python3 --version`)
- [Docker](https://docs.docker.com/get-docker/) (for Docker-based runs)
- `make` utility (pre-installed on Mac/Linux; for Windows, use WSL or Git Bash)

---

## 🏁 Setup

```bash
# (Recommended) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install
```

---

## �� Project Structure

```
python-test-framework/
│
├── consumer/                  # Consumer-side service code
│   ├── __init__.py
│   └── service.py
│
├── provider/                  # Provider-side service code
│   ├── __init__.py
│   └── service.py
│
├── tests/                     # All test files and fixtures
│   ├── __init__.py
│   ├── conftest.py             # Shared test fixtures
│   ├── conftest_async.py       # Async testfixtures
│   ├── conftest_day3.py
│   ├── test_api_basics.py
│   ├── test_async_patterns.py
│   ├── test_cleanup_tracker.py
│   ├── test_comment_factory.py
│   ├── test_cross_product_parametrization.py
│   ├── test_custom_ids.py
│   ├── test_data_driven.py
│   ├── test_data_driven_json.py
│   ├── test_data_factory.py
│   ├── test_data_validation.py
│   ├── test_environment_specific.py
│   ├── test_extended_data_driven.py
│   ├── test_fixture_scope.py
│   ├── test_helpers_async.py
│   ├── test_integration_async.py
│   ├── test_mocking_patterns.py
│   ├── test_parametrized_advanced.py
│   ├── test_performance.py
│   ├── test_performance_parametrized.py
│   ├── test_pydantic_emailstr.py
│   ├── pytest_metrics_collector.py  # Custom metrics plugin
│   ├── pytest_enterprise_plugin.py  # Enterprise plugin (markers, hooks)
│   └── test_enterprise_patterns.py  # Enterprise test examples
│
├── pacts/                     # Generated Pact contract files
│
├── scripts/                   # Utility and workflow scripts
│   └── run_pact_tests.py
│
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Pytest configuration
├── .github/                   # GitHub Actions workflows
│   └── workflows/
│       └── ci.yml
├── README.md                  # Project documentation
└── ... (other config files)
```

---

## 🚀 Quickstart

### Local
```bash
make install         # Install dependencies
make test            # Run all tests
make smoke           # Run smoke tests
make parallel        # Run tests in parallel
make coverage        # Generate coverage report
make help            # Show all available make commands
```

### Run a Single Test
```bash
pytest tests/test_api_basics.py::test_some_function
```

### Docker
```bash
docker compose up --build test-runner
# or with Makefile
make docker-test
```

### GitHub Actions (CI/CD)
- Tests run automatically on push, PR, and daily schedule.
- See `.github/workflows/ci.yml` for details.

---

## 🛠️ Troubleshooting

- **Python not found?** Install Python 3.9+ from [python.org](https://www.python.org/downloads/).
- **make: command not found?** On Windows, use WSL or Git Bash, or run the commands in the Makefile manually.
- **Docker issues?** Make sure Docker Desktop is running. See [Docker install guide](https://docs.docker.com/get-docker/).
- **Permission errors?** Try running with `sudo` (Linux/Mac) or as Administrator (Windows).
- **Still stuck?** Open an issue on GitHub for help!

---

## 🧪 Test Markers & Patterns

- `@pytest.mark.smoke` — Smoke tests
- `@pytest.mark.regression` — Regression tests
- `@pytest.mark.api` — API tests
- `@pytest.mark.integration` — Integration tests
- `@pytest.mark.performance` — Performance tests
- `@pytest.mark.critical` — Critical for deployment
- Combine markers: `pytest -m "api and not slow" -v`

---

## 🏢 Enterprise Test Patterns — Examples

### 1. Async API Test
```python
import pytest

@pytest.mark.asyncio
@pytest.mark.api
async def test_health_check(global_http_client):
    """Critical health check test"""
    response = await global_http_client.get("/users/1")
    assert response.status_code == 200
```

### 2. Test with Factory & Parametrize
```python
@pytest.mark.regression
@pytest.mark.parametrize("user_id", [1, 2, 3])
def test_user_lookup(http_client, user_id):
    resp = http_client.get(f"/users/{user_id}")
    assert resp.status_code == 200
```

### 3. Mocking with respx
```python
import respx

@respx.mock
def test_mocked_api(http_client):
    respx.get("https://jsonplaceholder.typicode.com/users/1").respond(json={"id": 1, "name": "Mocked"})
    resp = http_client.get("/users/1")
    assert resp.json()["name"] == "Mocked"
```

### 4. Parallel Execution
```bash
pytest -n auto -v
```

### 5. Custom Metrics & Reporting
- Metrics are collected automatically (see `reports/metrics_report.json`).
- HTML and JSON reports are generated after each run.

---

## 🐳 Docker & Compose

- Build and run all tests in an isolated container:
```bash
docker compose up --build test-runner
```
- Mounts `src/`, `tests/`, and `reports/` for easy development.

---

## 🛠️ Makefile Commands

- `make test` — Run all tests
- `make smoke` — Run smoke tests
- `make regression` — Run regression tests
- `make integration` — Run integration tests
- `make performance` — Run performance tests
- `make parallel` — Run tests in parallel
- `make coverage` — Generate coverage report
- `make report` — Generate HTML/JSON report
- `make clean` — Remove reports and cache
- `make docker-test` — Run tests in Docker
- `make help` — Show all commands

---

## 🤝 Contributing

Contributions are welcome! Please open issues or pull requests for improvements, bugfixes, or new features.

- Fork the repo and create your branch
- Add tests for your feature/fix
- Run `make test` and ensure all tests pass
- Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## ⭐ Why use this framework?
- Modern async & API testing
- Enterprise patterns and best practices
- Parallel, parametrized, and data-driven
- Custom metrics, reporting, and CI/CD ready
- Dockerized and easy to extend

---

## 📣 Community

- Issues and feature requests welcome via GitHub Issues
- PRs and feedback encouraged!
- Maintained by [chaunguyen](https://github.com/chaunguyen)

---

## Code of Conduct

Please note that this project is released with a [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.
