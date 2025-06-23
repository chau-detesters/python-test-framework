"""
Integration tests for mocking external APIs and dependency injection.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import respx
from src.async_client import AsyncAPIClient, APIResponse

class TestMockingPatterns:
    """Advanced mocking patterns for async testing"""
    
    @pytest.mark.asyncio
    async def test_mock_with_unittest_mock(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        mock_response.headers = {"Content-Type": "application/json"}
        with patch('httpx.AsyncClient', new_callable=MagicMock) as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            async with AsyncAPIClient("http://localhost") as client:
                response = await client.get_user(1)
                assert response.status_code == 200
                assert response.data["name"] == "John Doe"
                mock_client.get.assert_called_once_with("/users/1")

    @pytest.mark.asyncio
    @respx.mock
    async def test_mock_with_respx(self):
        user_data = {"id": 1, "name": "Jane Doe", "email": "jane@example.com"}
        respx.get("http://localhost/users/1").mock(
            return_value=httpx.Response(200, json=user_data)
        )
        async with AsyncAPIClient("http://localhost") as client:
            response = await client.get_user(1)
            assert response.status_code == 200
            assert response.data["name"] == "Jane Doe"

    @pytest.mark.asyncio
    @respx.mock
    async def test_mock_multiple_endpoints(self):
        user_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        respx.get("http://localhost/users/1").mock(
            return_value=httpx.Response(200, json=user_data)
        )
        posts_data = [
            {"id": 1, "userId": 1, "title": "Post 1", "body": "Body 1"},
            {"id": 2, "userId": 1, "title": "Post 2", "body": "Body 2"}
        ]
        respx.get("http://localhost/posts?userId=1").mock(
            return_value=httpx.Response(200, json=posts_data)
        )
        async with AsyncAPIClient("http://localhost") as client:
            user_response = await client.get_user(1)
            assert user_response.status_code == 200
            assert user_response.data["name"] == "John Doe"
            posts_response = await client.get_user_posts(1)
            assert posts_response.status_code == 200
            assert len(posts_response.data) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_mock_error_scenarios(self):
        respx.get("http://localhost/users/999").mock(
            return_value=httpx.Response(404, json={"error": "User not found"})
        )
        respx.get("http://localhost/users/500").mock(
            return_value=httpx.Response(500, json={"error": "Internal server error"})
        )
        async with AsyncAPIClient("http://localhost") as client:
            response_404 = await client.get_user(999)
            assert response_404.status_code == 404
            response_500 = await client.get_user(500)
            assert response_500.status_code == 500

    @pytest.mark.asyncio
    @respx.mock
    async def test_mock_with_side_effects(self):
        call_count = 0
        def dynamic_response(request):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(500, json={"error": "Temporary error"})
            else:
                return httpx.Response(200, json={"id": 1, "name": "John Doe", "retry": call_count})
        respx.get("http://localhost/users/1").mock(side_effect=dynamic_response)
        async with AsyncAPIClient("http://localhost") as client:
            response1 = await client.get_user(1)
            assert response1.status_code == 500
            response2 = await client.get_user(1)
            assert response2.status_code == 200
            assert response2.data["retry"] == 2 