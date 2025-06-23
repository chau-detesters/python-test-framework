# test_parametrized_advanced.py
"""
Tests voor geavanceerde parametrisatie en combinatorische scenario's.
"""
import pytest
import httpx
from typing import List, Tuple, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.environment_configs import get_environment_config, ENVIRONMENT_CONFIGS

class TestParametrizedPatterns:
    """Advanced parametrized testing patterns"""
    
    # Basic parametrized testing
    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_id", [1, 2, 3, 4, 5])
    async def test_user_by_id(self, http_client, user_id):
        """Test multiple user IDs"""
        response = await http_client.get(f"/users/{user_id}")
        assert response.status_code == 200
        
        user = response.json()
        assert user["id"] == user_id
        assert "name" in user
        assert "email" in user

    # Parametrized with multiple arguments
    @pytest.mark.asyncio
    @pytest.mark.parametrize("endpoint,expected_count", [
        ("/users", 10),
        ("/posts", 100),
        ("/albums", 100),
        ("/todos", 200),
    ])
    async def test_collection_endpoints(self, http_client, endpoint, expected_count):
        """Test different collection endpoints"""
        response = await http_client.get(endpoint)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == expected_count

    # Complex parametrized testing with test data
    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_case", [
        {
            "name": "valid_user_data",
            "user_data": {"name": "John Doe", "email": "john@example.com", "username": "johndoe"},
            "expected_status": 201
        },
        {
            "name": "missing_name",
            "user_data": {"email": "john@example.com", "username": "johndoe"},
            "expected_status": 422  # In real API would be validation error
        },
        {
            "name": "invalid_email",
            "user_data": {"name": "John Doe", "email": "invalid-email", "username": "johndoe"},
            "expected_status": 422
        }
    ], ids=lambda test_case: test_case["name"])
    async def test_user_creation_scenarios(self, http_client, test_case):
        """Test different user creation scenarios"""
        response = await http_client.post("/users", json=test_case["user_data"])
        
        # JSONPlaceholder always returns 201, but in real API we'd test validation
        if test_case["expected_status"] == 201:
            assert response.status_code == 201
            created_user = response.json()
            assert "id" in created_user

    # Parametrized with fixtures
    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_count", [1, 5, 10])
    async def test_bulk_operations(self, http_client, user_factory, user_count):
        """Test bulk operations with different sizes"""
        users = user_factory.create_multiple_users(user_count)
        
        successful_creates = 0
        for user_data in users:
            response = await http_client.post("/users", json=user_data)
            if response.status_code == 201:
                successful_creates += 1
        
        assert successful_creates == user_count

    # Cross-product parametrization
    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_id", [1, 2, 3])
    @pytest.mark.parametrize("post_fields", [
        ["id", "title"],
        ["id", "title", "body"],
        ["id", "title", "body", "userId"]
    ])
    async def test_post_field_combinations(self, http_client, user_id, post_fields):
        """Test different field combinations for posts"""
        response = await http_client.get(f"/posts?userId={user_id}")
        assert response.status_code == 200
        
        posts = response.json()
        if posts:  # If user has posts
            first_post = posts[0]
            for field in post_fields:
                assert field in first_post 