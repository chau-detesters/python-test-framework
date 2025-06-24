# environment_configs.py - Configuration per environment
"""
Contains configurations for different test environments (development, staging, production, etc).
"""
import os
from enum import Enum
from dataclasses import dataclass

class Environment(Enum):
    """Enum for different test environments."""
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"

@dataclass
class EnvironmentConfig:
    """Configuration for a specific test environment."""
    base_url: str
    timeout: int

    @property
    def is_production(self):
        """Returns True if the environment is production."""
        return self.base_url == "https://api.example.com"

ENVIRONMENT_CONFIGS = {
    Environment.DEV: EnvironmentConfig(base_url="https://jsonplaceholder.typicode.com", timeout=10),
    Environment.STAGING: EnvironmentConfig(base_url="https://jsonplaceholder.typicode.com", timeout=15),
    Environment.PROD: EnvironmentConfig(base_url="https://api.example.com", timeout=20),
}

def get_environment_config(env_name: str) -> EnvironmentConfig:
    """Get the configuration for a given environment name."""
    env = Environment(env_name)
    return ENVIRONMENT_CONFIGS[env] 