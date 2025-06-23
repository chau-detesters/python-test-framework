"""
Async tests for various async patterns and edge cases.
"""
import pytest
import asyncio
import time
from typing import List, Dict, Any
from src.async_client import AsyncAPIClient, APIResponse

class TestAsyncPatterns:
    """Advanced async testing patterns"""
    
    @pytest.mark.asyncio
    async def test_basic_async_client(self):
        async with AsyncAPIClient("https://jsonplaceholder.typicode.com") as client:
            response = await client.get_user(1)
            assert response.status_code == 200
            assert response.data is not None
            assert response.data["id"] == 1
            assert response.response_time < 5.0

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        async with AsyncAPIClient("https://jsonplaceholder.typicode.com") as client:
            user_ids = [1, 2, 3, 4, 5]
            tasks = [client.get_user(user_id) for user_id in user_ids]
            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            end_time = time.time()
            total_time = end_time - start_time
            assert len(responses) == len(user_ids)
            for i, response in enumerate(responses):
                assert response.status_code == 200
                assert response.data["id"] == user_ids[i]
            print(f"Concurrent requests took: {total_time:.3f}s")
            assert total_time < 10.0

    @pytest.mark.asyncio
    async def test_async_error_handling(self):
        async with AsyncAPIClient("https://jsonplaceholder.typicode.com") as client:
            response = await client.get_user(999)
            assert response.status_code == 404
            assert response.data is None

    @pytest.mark.asyncio
    async def test_batch_operations(self):
        async with AsyncAPIClient("https://jsonplaceholder.typicode.com") as client:
            users_data = [
                {"name": f"User {i}", "email": f"user{i}@example.com", "username": f"user{i}"}
                for i in range(1, 6)
            ]
            responses = await client.batch_create_users(users_data)
            assert len(responses) == 5
            for response in responses:
                assert response.status_code == 201
                assert response.data is not None

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        async with AsyncAPIClient("https://jsonplaceholder.typicode.com", timeout=0.001) as client:
            with pytest.raises(Exception):
                await client.get_user(1) 