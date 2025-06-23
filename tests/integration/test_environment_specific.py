# test_environment_specific.py
"""
Integration tests for environment-specific behavior and configuration.
"""
import pytest
import httpx
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.environment_configs import get_environment_config, Environment

@pytest.mark.parametrize("env_name", ["dev", "staging"])
class TestEnvironmentSpecific:
    """Tests that run across multiple environments"""
    
    @pytest.mark.asyncio
    async def test_health_check_per_environment(self, env_name):
        """Test health check across environments"""
        config = get_environment_config(env_name)
        
        async with httpx.AsyncClient(base_url=config.base_url, timeout=config.timeout) as client:
            # Most APIs have a health/status endpoint
            try:
                response = await client.get("/users/1")  # Using users/1 as health check
                assert response.status_code == 200
            except httpx.TimeoutException:
                pytest.fail(f"Timeout connecting to {env_name} environment")

    @pytest.mark.asyncio
    async def test_rate_limiting_per_environment(self, env_name):
        """Test rate limiting behavior per environment"""
        config = get_environment_config(env_name)
        
        if config.is_production:
            pytest.skip("Skipping rate limit tests in production")
        
        async with httpx.AsyncClient(base_url=config.base_url, timeout=config.timeout) as client:
            # Make multiple rapid requests
            responses = []
            for i in range(5):
                response = await client.get(f"/users/{i+1}")
                responses.append(response.status_code)
            
            # Should get successful responses (JSONPlaceholder doesn't rate limit)
            assert all(status == 200 for status in responses) 