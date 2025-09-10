"""
Database models using SQLAlchemy
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Zone(Base):
    __tablename__ = "zones"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # temple, ghat, parking, etc.
    coordinates = Column(JSON)  # Store polygon coordinates
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False)
    current_occupancy = Column(Integer, default=0)
    amenities = Column(JSON)  # List of amenities
    accessibility_features = Column(JSON)  # Accessibility features
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Route(Base):
    __tablename__ = "routes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    start_lat = Column(Float, nullable=False)
    start_lng = Column(Float, nullable=False)
    end_lat = Column(Float, nullable=False)
    end_lng = Column(Float, nullable=False)
    points = Column(JSON)  # Route points with coordinates and instructions
    total_distance_km = Column(Float, nullable=False)
    estimated_time_minutes = Column(Integer, nullable=False)
    priority = Column(String, nullable=False)
    crowd_level = Column(String, nullable=False)
    safety_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CrowdData(Base):
    __tablename__ = "crowd_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    zone_id = Column(String, ForeignKey("zones.id"), nullable=False)
    occupancy = Column(Integer, nullable=False)
    density_per_sqm = Column(Float, nullable=False)
    crowd_level = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    zone = relationship("Zone", backref="crowd_history")

class WeatherData(Base):
    __tablename__ = "weather_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    temperature_celsius = Column(Float, nullable=False)
    humidity_percent = Column(Float, nullable=False)
    wind_speed_kmh = Column(Float, nullable=False)
    condition = Column(String, nullable=False)
    visibility_km = Column(Float, nullable=False)
    uv_index = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Emergency(Base):
    __tablename__ = "emergencies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String, nullable=False)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String, nullable=False)
    status = Column(String, default="active")  # active, resolved, closed
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

class RoadNetwork(Base):
    __tablename__ = "road_network"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    road_type = Column(String, nullable=False)  # main, secondary, pedestrian
    start_lat = Column(Float, nullable=False)
    start_lng = Column(Float, nullable=False)
    end_lat = Column(Float, nullable=False)
    end_lng = Column(Float, nullable=False)
    length_km = Column(Float, nullable=False)
    width_meters = Column(Float)
    is_accessible = Column(Boolean, default=True)
    max_crowd_capacity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
