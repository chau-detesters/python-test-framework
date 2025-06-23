# config.py - Centralized configuration management
"""
Globale configuratie voor het testframework (paden, settings, etc).
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class TestConfig:
    """Test configuration class for the framework."""
    base_url: str
    timeout: int
    retries: int
    parallel_workers: int
    environment: str
    debug_mode: bool
    
    @classmethod
    def from_env(cls):
        """Maak een TestConfig aan op basis van environment variables."""
        return cls(
            base_url=os.getenv("TEST_BASE_URL", "https://jsonplaceholder.typicode.com"),
            timeout=int(os.getenv("TEST_TIMEOUT", "10")),
            retries=int(os.getenv("TEST_RETRIES", "3")),
            parallel_workers=int(os.getenv("TEST_WORKERS", "4")),
            environment=os.getenv("TEST_ENV", "staging"),
            debug_mode=os.getenv("DEBUG", "false").lower() == "true"
        ) 