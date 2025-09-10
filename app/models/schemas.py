"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"

class ZoneType(str, Enum):
    TEMPLE = "temple"
    GHAT = "ghat"
    PARKING = "parking"
    MEDICAL = "medical"
    SECURITY = "security"
    FOOD = "food"
    ACCOMMODATION = "accommodation"

class WeatherCondition(str, Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"

class CrowdLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Coordinate models
class Coordinate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class RoutePoint(BaseModel):
    coordinates: Coordinate
    instruction: Optional[str] = None
    estimated_time_minutes: Optional[int] = None

# Route models
class RouteRequest(BaseModel):
    start: Coordinate
    end: Coordinate
    priority: PriorityLevel = PriorityLevel.MEDIUM
    avoid_crowded_areas: bool = True
    accessibility_required: bool = False

class Route(BaseModel):
    id: str
    start: Coordinate
    end: Coordinate
    points: List[RoutePoint]
    total_distance_km: float
    estimated_time_minutes: int
    priority: PriorityLevel
    crowd_level: CrowdLevel
    safety_score: float = Field(..., ge=0, le=10)
    created_at: datetime

class RouteResponse(BaseModel):
    routes: List[Route]
    recommended_route_id: str
    alternative_count: int

# Weather models
class WeatherData(BaseModel):
    temperature_celsius: float
    humidity_percent: float
    wind_speed_kmh: float
    condition: WeatherCondition
    visibility_km: float
    uv_index: int = Field(..., ge=0, le=11)
    last_updated: datetime

class WeatherForecast(BaseModel):
    date: datetime
    weather: WeatherData
    crowd_impact_score: float = Field(..., ge=0, le=10)

class WeatherResponse(BaseModel):
    current: WeatherData
    forecast: List[WeatherForecast]
    alerts: List[str] = []

# Zone models
class Zone(BaseModel):
    id: str
    name: str
    type: ZoneType
    coordinates: List[Coordinate]  # Polygon boundary
    center: Coordinate
    capacity: int
    current_occupancy: int
    amenities: List[str] = []
    accessibility_features: List[str] = []
    description: Optional[str] = None

class ZoneStatus(BaseModel):
    zone_id: str
    zone_name: str
    current_occupancy: int
    capacity: int
    occupancy_percentage: float
    crowd_level: CrowdLevel
    estimated_wait_time_minutes: Optional[int] = None
    last_updated: datetime

class ZoneResponse(BaseModel):
    zones: List[Zone]
    total_zones: int

# Crowd models
class CrowdDensity(BaseModel):
    zone_id: str
    zone_name: str
    density_per_sqm: float
    crowd_level: CrowdLevel
    timestamp: datetime
    trend: str  # "increasing", "decreasing", "stable"

class CrowdStatusResponse(BaseModel):
    overall_crowd_level: CrowdLevel
    zones: List[CrowdDensity]
    peak_hours_today: List[str]
    recommendations: List[str]
    last_updated: datetime

# Emergency models
class EmergencyType(str, Enum):
    MEDICAL = "medical"
    FIRE = "fire"
    STAMPEDE = "stampede"
    SECURITY = "security"
    NATURAL_DISASTER = "natural_disaster"

class EmergencyRequest(BaseModel):
    type: EmergencyType
    location: Coordinate
    description: str
    severity: PriorityLevel = PriorityLevel.HIGH

class EmergencyRoute(BaseModel):
    route_id: str
    evacuation_points: List[Coordinate]
    medical_facilities: List[Coordinate]
    estimated_clearance_time_minutes: int
    safety_instructions: List[str]

class EmergencyResponse(BaseModel):
    emergency_id: str
    type: EmergencyType
    status: str
    evacuation_routes: List[EmergencyRoute]
    nearest_medical_facility: Coordinate
    emergency_contacts: List[str]
    instructions: List[str]

# Authentication models
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: str
    username: str
    is_admin: bool
    created_at: datetime

# WebSocket models
class CrowdUpdate(BaseModel):
    zone_id: str
    zone_name: str
    occupancy: int
    capacity: int
    crowd_level: CrowdLevel
    timestamp: datetime
    change_from_previous: int

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[Any, Any]
    timestamp: datetime
