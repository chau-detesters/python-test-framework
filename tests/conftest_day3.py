# conftest_day3.py - Additional fixtures for day 3
import pytest
import httpx
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.environment_configs import get_environment_config

@pytest.fixture(scope="session")
def environment_config():
    """Get current environment configuration"""
    return get_environment_config()

@pytest.fixture
def skip_in_production(environment_config):
    """Skip test if running in production"""
    if environment_config.is_production():
        pytest.skip("Test skipped in production environment")

@pytest.fixture(params=["dev", "staging"])
def multi_env_client(request):
    """HTTP client that tests across multiple environments"""
    config = get_environment_config(request.param)
    
    async def _create_client():
        return httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout
        )
    
    return _create_client 