"""
Async-specifieke pytest fixtures voor asynchrone tests.
"""
import pytest
import asyncio
from src.async_client import AsyncAPIClient
from src.async_test_helpers import AsyncTestHelper

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for the test session"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def api_client():
    """Async API client fixture"""
    async with AsyncAPIClient("https://jsonplaceholder.typicode.com") as client:
        yield client

@pytest.fixture
def async_helper():
    """Async test helper fixture"""
    return AsyncTestHelper()

@pytest.fixture
async def mock_api_client():
    """Mock API client for testing"""
    async with AsyncAPIClient("http://localhost") as client:
        yield client 