# conftest.py
"""
Central pytest configuration and fixtures for the test framework.
Contains global, session, and module-scope fixtures, and hooks for test data loading.
"""
import pytest
import httpx
from faker import Faker
import sys
import os
import respx

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import TestConfig
from src.test_data_factory import UserFactory, PostFactory, CommentFactory

pytest_plugins = [
    "tests.pytest_metrics_collector",
    "tests.pytest_enterprise_plugin"
]

@pytest.fixture(scope="session")
def fake():
    """Faker instance for test data generation"""
    return Faker()

@pytest.fixture(scope="session") 
def base_url():
    """Base URL for API testing"""
    return "https://jsonplaceholder.typicode.com"

@pytest.fixture(scope="session")
def test_config():
    """Global test configuration"""
    return TestConfig.from_env()

import pytest_asyncio

@pytest_asyncio.fixture
async def http_client(base_url):
    """Async HTTP client for API calls"""
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        yield client

@pytest_asyncio.fixture
async def global_http_client(base_url):
    """Global async HTTP client for enterprise tests"""
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        yield client

@pytest.fixture
def sample_user_data(fake):
    """Generate sample user data for testing"""
    return {
        "name": fake.name(),
        "email": fake.email(),
        "username": fake.user_name()
    }

# Advanced fixtures
@pytest.fixture
def user_factory() -> type:
    """User factory fixture"""
    return UserFactory

@pytest.fixture
def post_factory() -> type:
    """Post factory fixture"""
    return PostFactory

@pytest.fixture
def comment_factory() -> type:
    """Comment factory fixture"""
    return CommentFactory

@pytest.fixture
def sample_user(user_factory):
    """Single sample user"""
    return user_factory.create_user()

@pytest.fixture
def sample_users(user_factory):
    """Multiple sample users"""
    return user_factory.create_multiple_users(5)

@pytest.fixture
def sample_post(post_factory):
    """Single sample post"""
    return post_factory.create_post()

# Database-like fixtures (for complex test scenarios)
@pytest.fixture
def user_with_posts(user_factory, post_factory):
    """Create a user with associated posts in the test API"""
    # Create user
    user_data = user_factory.create_user()
    
    # For JSONPlaceholder, we'll use the fallback since it's read-only
    return {
        "user": user_data,
        "posts": post_factory.create_posts_for_user(user_data["id"])
    }

# Cleanup fixtures
@pytest.fixture
def cleanup_tracker():
    """Enhanced cleanup tracker with duplicate prevention and custom resource types"""
    created_resources = {
        "users": [],
        "posts": [],
        "comments": [],
        "albums": [],
        "photos": [],
        "todos": []
    }
    
    def add_resource(resource_type: str, resource_id: int):
        """Add resource to tracker with duplicate prevention"""
        if resource_type not in created_resources:
            created_resources[resource_type] = []
        
        if resource_id not in created_resources[resource_type]:
            created_resources[resource_type].append(resource_id)
            print(f"Added {resource_type} {resource_id} to cleanup tracker")
    
    def get_resource_count(resource_type: str) -> int:
        """Get count of tracked resources by type"""
        return len(created_resources.get(resource_type, []))
    
    def get_total_resources() -> int:
        """Get total count of all tracked resources"""
        return sum(len(resources) for key, resources in created_resources.items() 
                  if isinstance(resources, list))
    
    # Add helper methods to the tracker
    created_resources["add"] = add_resource
    created_resources["count"] = get_resource_count
    created_resources["total"] = get_total_resources
    
    yield created_resources
    
    # Enhanced cleanup reporting
    total_resources = get_total_resources()
    if total_resources > 0:
        print(f"\n=== CLEANUP SUMMARY ===")
        print(f"Total resources tracked: {total_resources}")
        for resource_type, resources in created_resources.items():
            if isinstance(resources, list) and resources:
                print(f"  {resource_type}: {len(resources)} items")
        print(f"=== END CLEANUP ===\n")
    else:
        print("No resources to cleanup")

@pytest.fixture
def respx_mock():
    with respx.mock as mock:
        yield mock 