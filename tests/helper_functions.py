# helper_functions.py
"""
Helper functions for test data, validation, and utilities within the test framework.
"""
import pytest
import asyncio
from typing import List, Callable, Any
import httpx

class APIHelper:
    """Helper class for common API operations"""
    
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
    
    async def wait_for_condition(self, 
                                condition_func: Callable, 
                                timeout: int = 30, 
                                interval: int = 1) -> bool:
        """Wait for a condition to be true"""
        for _ in range(timeout):
            if await condition_func():
                return True
            await asyncio.sleep(interval)
        return False
    
    async def retry_request(self, method: str, url: str, max_retries: int = 3, **kwargs) -> httpx.Response:
        """Retry a request with exponential backoff"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                response = await self.client.request(method, url, **kwargs)
                if response.status_code < 500:  # Don't retry client errors
                    return response
            except Exception as e:
                last_exception = e
            
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        if last_exception:
            raise last_exception
        return response

@pytest.fixture
def api_helper(http_client):
    """API helper fixture"""
    return APIHelper(http_client) 