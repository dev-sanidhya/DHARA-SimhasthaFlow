"""
Configuration settings for the application
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./simhastha_flow.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Settings
    api_v1_str: str = "/api/v1"
    project_name: str = "SimhasthaFlow API"
    
    # CORS
    allowed_origins: list = ["*"]
    
    # Mock data settings
    enable_real_time_simulation: bool = True
    simulation_interval_seconds: int = 30
    
    # External API URLs (for future integration)
    weather_api_url: Optional[str] = None
    maps_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()
