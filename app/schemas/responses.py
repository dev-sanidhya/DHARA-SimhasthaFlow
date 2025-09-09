"""
Pydantic response schemas for DHARA API
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class LocationResponse(BaseModel):
    """Location response schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    osm_id: Optional[str] = None
    name: str
    location_type: str
    address: Optional[str] = None
    capacity: Optional[int] = None
    current_crowd: int = 0
    is_active: bool
    created_at: datetime
    updated_at: datetime

class WeatherResponse(BaseModel):
    """Weather data response schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    timestamp: datetime
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: float
    pressure: float
    visibility: float
    description: str
    icon: str
    rain_1h: float = 0
    rain_3h: float = 0
    uv_index: Optional[float] = None

class CrowdResponse(BaseModel):
    """Crowd data response schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    location_id: int
    timestamp: datetime
    crowd_count: int
    density_level: int
    data_source: str
    confidence_score: float
    is_verified: bool

class RouteResponse(BaseModel):
    """Route response schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    source_location_id: int
    destination_location_id: int
    distance: float
    estimated_time: int
    difficulty_level: int
    current_congestion: int
    is_recommended: bool
    created_at: datetime
    updated_at: datetime
