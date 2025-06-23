# Modern Python Test Automation Framework
# Dag 1 Starter Project

"""
Hoofdmodule van het Python API testframework.
Bevat kernlogica voor testuitvoering, data loading, validatie, en utilities.
"""

# requirements.txt
"""
pytest==7.4.3
httpx==0.25.2
pytest-asyncio==0.21.1
pytest-html==4.1.1
pydantic==2.5.0
faker==20.1.0
"""

# conftest.py - Pytest configuration
import pytest
import httpx
from faker import Faker

@pytest.fixture(scope="session")
def fake():
    """Faker instance voor testdata generatie"""
    return Faker()

@pytest.fixture(scope="session") 
def base_url():
    """Base URL voor API testing"""
    return "https://jsonplaceholder.typicode.com"

@pytest.fixture
async def http_client(base_url):
    """Async HTTP client voor API calls"""
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        yield client

@pytest.fixture
def sample_user_data(fake):
    """Generate sample user data voor testing"""
    return {
        "name": fake.name(),
        "email": fake.email(),
        "username": fake.user_name()
    }

# test_api_basics.py - Basis API tests
import pytest
import httpx
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    id: int
    name: str
    username: str
    email: str

class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str

@pytest.mark.asyncio
class TestUsersAPI:
    
    async def test_get_all_users(self, http_client):
        """Test het ophalen van alle users"""
        response = await http_client.get("/users")
        
        assert response.status_code == 200
        users_data = response.json()
        assert len(users_data) > 0
        
        # Valideer eerste user met Pydantic
        first_user = User(**users_data[0])
        assert first_user.id > 0
        assert "@" in first_user.email

    async def test_get_single_user(self, http_client):
        """Test het ophalen van een specifieke user"""
        user_id = 1
        response = await http_client.get(f"/users/{user_id}")
        
        assert response.status_code == 200
        user_data = response.json()
        
        user = User(**user_data)
        assert user.id == user_id

    @pytest.mark.parametrize("user_id", [1, 2, 3, 5, 10])
    async def test_multiple_users(self, http_client, user_id):
        """Test meerdere user IDs met parametrized testing"""
        response = await http_client.get(f"/users/{user_id}")
        
        assert response.status_code == 200
        user = User(**response.json())
        assert user.id == user_id

    async def test_user_not_found(self, http_client):
        """Test 404 scenario"""
        response = await http_client.get("/users/999")
        assert response.status_code == 404

@pytest.mark.asyncio  
class TestPostsAPI:
    
    async def test_get_posts_for_user(self, http_client):
        """Test posts van een specifieke user"""
        user_id = 1
        response = await http_client.get(f"/posts?userId={user_id}")
        
        assert response.status_code == 200
        posts = response.json()
        
        # Valideer dat alle posts van de juiste user zijn
        for post_data in posts:
            post = Post(**post_data)
            assert post.userId == user_id

    async def test_create_post(self, http_client, sample_user_data):
        """Test het aanmaken van een nieuwe post"""
        new_post = {
            "title": "Test Post",
            "body": "Dit is een test post body",
            "userId": 1
        }
        
        response = await http_client.post("/posts", json=new_post)
        
        assert response.status_code == 201
        created_post = response.json()
        assert created_post["title"] == new_post["title"]
        assert created_post["userId"] == new_post["userId"]

# test_performance.py - Performance testing
import pytest
import time
import httpx

@pytest.mark.asyncio
class TestPerformance:
    
    async def test_response_time_under_threshold(self, http_client):
        """Test dat API responses binnen acceptabele tijd zijn"""
        start_time = time.time()
        response = await http_client.get("/users")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0, f"Response time {response_time}s exceeded 2s threshold"

    @pytest.mark.parametrize("endpoint", ["/users", "/posts", "/albums"])
    async def test_multiple_endpoints_performance(self, http_client, endpoint):
        """Test performance van verschillende endpoints"""
        start_time = time.time()
        response = await http_client.get(endpoint)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 3.0

# pytest.ini - Pytest configuratie
"""
[tool:pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --html=reports/report.html 
    --self-contained-html
    -v
    --tb=short
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
"""