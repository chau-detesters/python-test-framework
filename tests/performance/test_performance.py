"""
Basic performance tests for API endpoints.
"""
import pytest
import time
import httpx

@pytest.mark.asyncio
class TestPerformance:
    
    async def test_response_time_under_threshold(self, http_client):
        """Test that the response time of /users stays below the threshold."""
        start_time = time.time()
        response = await http_client.get("/users")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0, f"Response time {response_time}s exceeded 2s threshold"

    @pytest.mark.parametrize("endpoint", ["/users", "/posts", "/albums"])
    async def test_multiple_endpoints_performance(self, http_client, endpoint):
        """Test that the response time of different endpoints is acceptable."""
        start_time = time.time()
        response = await http_client.get(endpoint)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 3.0 