import httpx
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import asyncio

class User(BaseModel):
    id: int
    name: str
    email: str
    username: str

class Post(BaseModel):
    id: int
    userId: int
    title: str
    body: str

class UserService:
    """Consumer service that depends on User API"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=10.0)
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID - this is what we'll test with Pact"""
        try:
            response = self.client.get(f"/users/{user_id}")
            if response.status_code == 200:
                return User(**response.json())
            return None
        except Exception:
            return None
    
    def get_users(self, limit: int = 10) -> List[User]:
        """Get multiple users"""
        try:
            response = self.client.get(f"/users?_limit={limit}")
            if response.status_code == 200:
                return [User(**user_data) for user_data in response.json()]
            return []
        except Exception:
            return []
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[User]:
        """Create a new user"""
        try:
            response = self.client.post("/users", json=user_data)
            if response.status_code == 201:
                return User(**response.json())
            return None
        except Exception:
            return None
    
    def get_user_posts(self, user_id: int) -> List[Post]:
        """Get posts for a specific user"""
        try:
            response = self.client.get(f"/posts?userId={user_id}")
            if response.status_code == 200:
                return [Post(**post_data) for post_data in response.json()]
            return []
        except Exception:
            return []
    
    def close(self):
        """Close the HTTP client"""
        self.client.close() 