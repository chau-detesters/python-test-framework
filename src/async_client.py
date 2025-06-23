import asyncio
import httpx
from typing import Dict, List, Any, Optional
import json
from dataclasses import dataclass

"""
Asynchrone HTTP client voor API-testen, gebaseerd op httpx.
Bevat AsyncAPIClient en response wrappers.
"""

@dataclass
class APIResponse:
    """Structured API response returned by the async client."""
    status_code: int
    data: Any
    headers: Dict[str, str]
    response_time: float

class AsyncAPIClient:
    """Example async API client that we'll test"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self._session: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self._session = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.aclose()
    
    async def get_user(self, user_id: int) -> APIResponse:
        import time
        start_time = time.time()
        
        response = await self._session.get(f"/users/{user_id}")
        end_time = time.time()
        
        return APIResponse(
            status_code=response.status_code,
            data=response.json() if response.status_code == 200 else None,
            headers=dict(response.headers),
            response_time=end_time - start_time
        )
    
    async def get_users(self, limit: int = 10) -> APIResponse:
        import time
        start_time = time.time()
        
        response = await self._session.get(f"/users?_limit={limit}")
        end_time = time.time()
        
        return APIResponse(
            status_code=response.status_code,
            data=response.json() if response.status_code == 200 else [],
            headers=dict(response.headers),
            response_time=end_time - start_time
        )
    
    async def create_user(self, user_data: Dict[str, Any]) -> APIResponse:
        import time
        start_time = time.time()
        
        response = await self._session.post("/users", json=user_data)
        end_time = time.time()
        
        return APIResponse(
            status_code=response.status_code,
            data=response.json() if response.status_code == 201 else None,
            headers=dict(response.headers),
            response_time=end_time - start_time
        )
    
    async def batch_create_users(self, users_data: List[Dict[str, Any]]) -> List[APIResponse]:
        tasks = [self.create_user(user_data) for user_data in users_data]
        return await asyncio.gather(*tasks)
    
    async def get_user_posts(self, user_id: int) -> APIResponse:
        import time
        start_time = time.time()
        
        response = await self._session.get(f"/posts?userId={user_id}")
        end_time = time.time()
        
        return APIResponse(
            status_code=response.status_code,
            data=response.json() if response.status_code == 200 else [],
            headers=dict(response.headers),
            response_time=end_time - start_time
        ) 