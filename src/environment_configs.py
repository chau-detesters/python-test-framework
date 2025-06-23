# environment_configs.py - Configuration per environment
"""
Bevat configuraties voor verschillende testomgevingen (development, staging, production, etc).
"""
import os
from enum import Enum
from dataclasses import dataclass

class Environment(Enum):
    """Enum voor verschillende testomgevingen."""
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"

@dataclass
class EnvironmentConfig:
    """Configuratie voor een specifieke testomgeving."""
    base_url: str
    timeout: int

    @property
    def is_production(self):
        """Geeft True als de omgeving productie is."""
        return self.base_url == "https://api.example.com"

ENVIRONMENT_CONFIGS = {
    Environment.DEV: EnvironmentConfig(base_url="https://jsonplaceholder.typicode.com", timeout=10),
    Environment.STAGING: EnvironmentConfig(base_url="https://jsonplaceholder.typicode.com", timeout=15),
    Environment.PROD: EnvironmentConfig(base_url="https://api.example.com", timeout=20),
}

def get_environment_config(env_name: str) -> EnvironmentConfig:
    """Haal de configuratie op voor een gegeven omgevingsnaam."""
    env = Environment(env_name)
    return ENVIRONMENT_CONFIGS[env] 