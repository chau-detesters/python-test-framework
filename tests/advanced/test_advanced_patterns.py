# test_advanced_patterns.py
"""
Tests voor geavanceerde testpatronen, fixtures en custom pytest features.
"""
import pytest
from typing import Dict, Any, List

@pytest.mark.asyncio
class TestAdvancedPatterns:
    
    async def test_user_creation_with_factory(self, http_client, user_factory, cleanup_tracker):
        """Test user creation using factory pattern"""
        # Generate test data
        user_data = user_factory.create_user(
            name="Test User",
            email="test@example.com"
        )
        
        # Make API call
        response = await http_client.post("/users", json=user_data)
        
        # JSONPlaceholder returns 201 for POST but doesn't actually create
        assert response.status_code == 201
        created_user = response.json()
        
        # Track for cleanup
        cleanup_tracker["users"].append(created_user.get("id"))
        
        # Validate response
        assert created_user["name"] == user_data["name"]
        assert created_user["email"] == user_data["email"]

    async def test_batch_user_creation(self, http_client, user_factory):
        """Test creating multiple users in batch"""
        users_data = user_factory.create_multiple_users(3)
        created_users = []
        
        for user_data in users_data:
            response = await http_client.post("/users", json=user_data)
            assert response.status_code == 201
            created_users.append(response.json())
        
        assert len(created_users) == 3
        
        # Validate each user has unique data
        emails = [user["email"] for user in created_users]
        assert len(set(emails)) == 3  # All emails should be unique

    async def test_user_with_posts_workflow(self, user_with_posts, http_client):
        """Test complete user workflow with posts"""
        user_with_posts_data = user_with_posts
        user_data = user_with_posts_data["user"]
        posts_data = user_with_posts_data["posts"]
        
        # Verify user exists (simulated)
        user_response = await http_client.get(f"/users/{user_data['id']}")
        
        # Verify posts exist for user (simulated)
        posts_response = await http_client.get(f"/posts?userId={user_data['id']}")
        assert posts_response.status_code == 200
        
        # In real scenario, we'd verify our created posts are returned
        print(f"User {user_data['name']} has {len(posts_data)} posts")

    @pytest.mark.parametrize("user_count", [1, 3, 5])
    async def test_dynamic_user_creation(self, http_client, user_factory, user_count):
        """Test creating different amounts of users"""
        users = user_factory.create_multiple_users(user_count)
        
        success_count = 0
        for user_data in users:
            response = await http_client.post("/users", json=user_data)
            if response.status_code == 201:
                success_count += 1
        
        assert success_count == user_count 