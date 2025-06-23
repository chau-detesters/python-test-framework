"""
Async tests with respx for HTTP mocking and scenarios.
"""
import pytest
import httpx
from src.async_client import AsyncAPIClient

@pytest.mark.asyncio
async def test_respx_success_response(respx_mock):
    respx_mock.get("https://api.example.com/users/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Mocked User"})
    )
    async with AsyncAPIClient(base_url="https://api.example.com") as client:
        response = await client.get_user(1)
        assert response.status_code == 200
        assert response.data["name"] == "Mocked User"

@pytest.mark.asyncio
async def test_respx_404_response(respx_mock):
    respx_mock.get("https://api.example.com/users/404").mock(
        return_value=httpx.Response(404, json={"detail": "Not found"})
    )
    async with AsyncAPIClient(base_url="https://api.example.com") as client:
        response = await client.get_user(404)
        assert response.status_code == 404
        assert response.data is None

@pytest.mark.asyncio
async def test_respx_500_response(respx_mock):
    respx_mock.get("https://api.example.com/users/1").mock(
        return_value=httpx.Response(500, json={"detail": "Server error"})
    )
    async with AsyncAPIClient(base_url="https://api.example.com") as client:
        response = await client.get_user(1)
        assert response.status_code == 500
        assert response.data is None

@pytest.mark.asyncio
async def test_respx_dynamic_side_effects(respx_mock):
    calls = []
    def dynamic_response(request):
        calls.append(request.url)
        if "2" in str(request.url):
            return httpx.Response(200, json={"id": 2, "name": "Dynamic User"})
        return httpx.Response(404, json={"detail": "Not found"})
    respx_mock.get("https://api.example.com/users/2").mock(side_effect=dynamic_response)
    respx_mock.get("https://api.example.com/users/3").mock(side_effect=dynamic_response)
    async with AsyncAPIClient(base_url="https://api.example.com") as client:
        response2 = await client.get_user(2)
        response3 = await client.get_user(3)
        assert response2.status_code == 200
        assert response2.data["name"] == "Dynamic User"
        assert response3.status_code == 404
        assert response3.data is None
    assert len(calls) == 2 