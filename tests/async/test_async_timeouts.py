"""
Async tests voor timeouts en error handling in API calls.
"""
import pytest
import asyncio
import httpx
import respx
from src.async_client import AsyncAPIClient

@pytest.mark.asyncio
async def test_request_within_timeout():
    async with AsyncAPIClient(base_url="https://httpbin.org", timeout=5) as client:
        response = await client._session.get("/delay/2")  # endpoint wacht 2 seconden
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_request_exceeds_timeout():
    async with AsyncAPIClient(base_url="https://httpbin.org", timeout=1) as client:
        with pytest.raises(httpx.ReadTimeout):
            await client._session.get("/delay/3")  # endpoint wacht 3 seconden

@pytest.mark.asyncio
async def test_batch_requests_with_timeouts():
    async with AsyncAPIClient(base_url="https://httpbin.org", timeout=2) as client:
        tasks = [
            client._session.get("/delay/1"),  # zal slagen
            client._session.get("/delay/3"),  # zal timeout geven
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Controleer resultaat type voor status_code
        if isinstance(results[0], Exception):
            assert isinstance(results[0], httpx.ReadTimeout)
        else:
            assert results[0].status_code == 200
        assert isinstance(results[1], httpx.ReadTimeout)

@pytest.mark.asyncio
async def test_per_request_timeout():
    async with AsyncAPIClient(base_url="https://httpbin.org", timeout=5) as client:
        # Override de globale timeout per request
        with pytest.raises(httpx.ReadTimeout):
            await client._session.get("/delay/2", timeout=0.5)

@respx.mock
@pytest.mark.asyncio
async def test_mocked_timeout():
    route = respx.get("https://api.example.com/users/1").mock(side_effect=httpx.ReadTimeout("Timeout!"))
    async with AsyncAPIClient(base_url="https://api.example.com", timeout=1) as client:
        with pytest.raises(httpx.ReadTimeout):
            await client.get_user(1) 