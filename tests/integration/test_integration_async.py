"""
Integratietests voor asynchrone API interacties en async clients.
"""
import pytest
import asyncio
from typing import List
from src.async_client import AsyncAPIClient
import time

class TestAsyncIntegration:
    """Integration tests with real async workflows"""
    
    @pytest.mark.asyncio
    async def test_user_workflow_integration(self):
        async with AsyncAPIClient("https://jsonplaceholder.typicode.com") as client:
            user_response = await client.get_user(1)
            assert user_response.status_code == 200
            user = user_response.data
            posts_response = await client.get_user_posts(user["id"])
            assert posts_response.status_code == 200
            posts = posts_response.data
            assert len(posts) > 0
            for post in posts:
                assert post["userId"] == user["id"]

    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        async with AsyncAPIClient("https://jsonplaceholder.typicode.com") as client:
            num_requests = 20
            max_concurrent = 5
            async def make_request(user_id):
                return await client.get_user(user_id)
            semaphore = asyncio.Semaphore(max_concurrent)
            async def limited_request(user_id):
                async with semaphore:
                    return await make_request(user_id % 10 + 1)
            start_time = time.time()
            tasks = [limited_request(i) for i in range(num_requests)]
            responses = await asyncio.gather(*tasks)
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = sum(r.response_time for r in responses) / len(responses)
            assert all(r.status_code == 200 for r in responses)
            assert total_time < 30.0
            assert avg_time < 5.0
            print(f"Total time: {total_time:.3f}s")
            print(f"Average response time: {avg_time:.3f}s")
            print(f"Requests per second: {num_requests/total_time:.1f}") 