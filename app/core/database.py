"""
Database configuration and models for DHARA system
Uses PostgreSQL with PostGIS for spatial queries
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from geoalchemy2 import Geography, Geometry
from datetime import datetime
import asyncio

from app.core.config import settings

# Convert synchronous DATABASE_URL to async
if settings.DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = settings.DATABASE_URL

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Dependency for getting database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Location(Base):
    """Spatial locations within Ujjain - real OSM data"""
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(String(50), unique=True, index=True)  # Real OSM ID
    name = Column(String(200), nullable=False)
    location_type = Column(String(50))  # temple, ghat, parking, hospital, etc.
    geometry = Column(Geometry('POINT', srid=4326))  # PostGIS geometry
    address = Column(Text)
    capacity = Column(Integer)  # Maximum crowd capacity
    current_crowd = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Road(Base):
    """Road network from OSM data"""
    __tablename__ = "roads"
    
    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(String(50), unique=True, index=True)  # Real OSM way ID
    name = Column(String(200))
    road_type = Column(String(50))  # highway, primary, secondary, etc.
    geometry = Column(Geometry('LINESTRING', srid=4326))  # PostGIS linestring
    max_speed = Column(Integer)
    width = Column(Float)
    surface = Column(String(50))
    is_oneway = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    current_traffic_level = Column(Integer, default=0)  # 0-5 scale
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WeatherData(Base):
    """Real weather data from OpenWeatherMap"""
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    temperature = Column(Float)  # Celsius
    humidity = Column(Float)  # Percentage
    wind_speed = Column(Float)  # m/s
    wind_direction = Column(Float)  # degrees
    pressure = Column(Float)  # hPa
    visibility = Column(Float)  # km
    description = Column(String(100))
    icon = Column(String(10))
    rain_1h = Column(Float, default=0)  # mm
    rain_3h = Column(Float, default=0)  # mm
    uv_index = Column(Float)
    location = Column(Geometry('POINT', srid=4326))

class CrowdData(Base):
    """Real-time crowd density data"""
    __tablename__ = "crowd_data"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    crowd_count = Column(Integer, nullable=False)
    density_level = Column(Integer)  # 1-5 scale
    data_source = Column(String(50))  # camera, mobile, manual, estimated
    confidence_score = Column(Float, default=1.0)  # 0-1
    is_verified = Column(Boolean, default=False)
    
    location = relationship("Location", back_populates="crowd_readings")

class Event(Base):
    """Official Simhastha events - real schedule data"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    event_type = Column(String(50))  # ritual, ceremony, procession
    location_id = Column(Integer, ForeignKey("locations.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    expected_attendance = Column(Integer)
    actual_attendance = Column(Integer)
    status = Column(String(20), default="scheduled")  # scheduled, ongoing, completed, cancelled
    priority_level = Column(Integer, default=1)  # 1-5
    
    location = relationship("Location")

class Route(Base):
    """Dynamic routing suggestions"""
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    source_location_id = Column(Integer, ForeignKey("locations.id"))
    destination_location_id = Column(Integer, ForeignKey("locations.id"))
    route_geometry = Column(Geometry('LINESTRING', srid=4326))
    distance = Column(Float)  # meters
    estimated_time = Column(Integer)  # minutes
    difficulty_level = Column(Integer, default=1)  # 1-5
    current_congestion = Column(Integer, default=0)  # 0-5
    is_recommended = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    source = relationship("Location", foreign_keys=[source_location_id])
    destination = relationship("Location", foreign_keys=[destination_location_id])

# Add back reference for crowd readings
Location.crowd_readings = relationship("CrowdData", back_populates="location")
