import pytest
import asyncio
import time
from typing import Dict, Any, List

@pytest.mark.asyncio
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