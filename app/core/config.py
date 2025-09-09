"""
Configuration settings for DHARA application
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/dhara_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs - REAL API KEYS REQUIRED
    OPENWEATHER_API_KEY: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # OSM Settings
    OSM_API_URL: str = "https://overpass-api.de/api/interpreter"
    OSM_NOMINATIM_URL: str = "https://nominatim.openstreetmap.org"
    
    # Weather API
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"
    
    # Ujjain coordinates (real location)
    UJJAIN_LAT: float = 23.1765
    UJJAIN_LON: float = 75.7885
    UJJAIN_BBOX: tuple = (75.7, 23.1, 75.9, 23.3)  # (min_lon, min_lat, max_lon, max_lat)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
