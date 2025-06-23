"""
Tests voor async semaphores in performance context.
"""
import pytest
import asyncio
import time
import respx
import httpx
from src.async_client import AsyncAPIClient

@pytest.mark.asyncio
@respx.mock
async def test_rate_limited_batch_requests():
    n = 50
    max_concurrent = 5
    semaphore = asyncio.Semaphore(max_concurrent)
    respx.get("https://api.example.com/users/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Mocked User"})
    )
    results = []

    async def limited_get_user(client, user_id):
        async with semaphore:
            return await client.get_user(user_id)

    async with AsyncAPIClient(base_url="https://api.example.com", timeout=5) as client:
        start = time.time()
        tasks = [limited_get_user(client, 1) for _ in range(n)]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start

    print(f"Total requests: {n}")
    print(f"Max concurrent: {max_concurrent}")
    print(f"Total time: {elapsed:.3f}s")
    print(f"Requests per second: {n/elapsed:.1f}")
    assert len(results) == n
    assert all(r.status_code == 200 for r in results) 