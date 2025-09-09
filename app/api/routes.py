"""
API routes for DHARA crowd management system
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.core.database import get_db, Location, WeatherData, CrowdData, Event, Route
from app.schemas.responses import LocationResponse, WeatherResponse, CrowdResponse, RouteResponse
from app.services.auth import verify_token
from app.services.routing_engine import RoutingEngine

router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and get current user"""
    token = credentials.credentials
    user = await verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user

@router.get("/locations", response_model=List[LocationResponse])
async def get_locations(
    location_type: Optional[str] = Query(None, description="Filter by location type"),
    limit: int = Query(100, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get all locations with current crowd data"""
    query = select(Location).where(Location.is_active == True)
    
    if location_type:
        query = query.where(Location.location_type == location_type)
    
    query = query.limit(limit)
    result = await db.execute(query)
    locations = result.scalars().all()
    
    return [LocationResponse.from_orm(loc) for loc in locations]

@router.get("/locations/{location_id}/crowd", response_model=List[CrowdResponse])
async def get_location_crowd_history(
    location_id: int,
    hours: int = Query(24, description="Hours of history to fetch"),
    db: AsyncSession = Depends(get_db)
):
    """Get crowd history for a specific location"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(CrowdData).where(
        CrowdData.location_id == location_id,
        CrowdData.timestamp >= since
    ).order_by(CrowdData.timestamp.desc())
    
    result = await db.execute(query)
    crowd_data = result.scalars().all()
    
    return [CrowdResponse.from_orm(cd) for cd in crowd_data]

@router.get("/weather/current", response_model=WeatherResponse)
async def get_current_weather(db: AsyncSession = Depends(get_db)):
    """Get latest weather data"""
    query = select(WeatherData).order_by(WeatherData.timestamp.desc()).limit(1)
    result = await db.execute(query)
    weather = result.scalar_one_or_none()
    
    if not weather:
        raise HTTPException(status_code=404, detail="No weather data available")
    
    return WeatherResponse.from_orm(weather)

@router.get("/weather/forecast")
async def get_weather_forecast(
    hours: int = Query(24, description="Hours of forecast"),
    db: AsyncSession = Depends(get_db)
):
    """Get weather forecast (last 24 hours of data as trend)"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(WeatherData).where(
        WeatherData.timestamp >= since
    ).order_by(WeatherData.timestamp.desc())
    
    result = await db.execute(query)
    weather_data = result.scalars().all()
    
    return [WeatherResponse.from_orm(wd) for wd in weather_data]

@router.get("/routes", response_model=List[RouteResponse])
async def get_routes(
    source_id: Optional[int] = Query(None),
    destination_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get available routes between locations"""
    query = select(Route).where(Route.is_recommended == True)
    
    if source_id:
        query = query.where(Route.source_location_id == source_id)
    if destination_id:
        query = query.where(Route.destination_location_id == destination_id)
    
    result = await db.execute(query)
    routes = result.scalars().all()
    
    return [RouteResponse.from_orm(route) for route in routes]

@router.post("/routes/calculate")
async def calculate_route(
    source_lat: float,
    source_lon: float,
    dest_lat: float,
    dest_lon: float,
    avoid_crowds: bool = Query(True),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculate optimal route between two points"""
    routing_engine = RoutingEngine(db)
    
    route = await routing_engine.calculate_optimal_route(
        source_lat, source_lon, dest_lat, dest_lon, avoid_crowds
    )
    
    return route

@router.get("/crowd/heatmap")
async def get_crowd_heatmap(
    timestamp: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get crowd density heatmap data"""
    if not timestamp:
        timestamp = datetime.utcnow()
    
    # Get crowd data within last 30 minutes of specified timestamp
    time_window = timedelta(minutes=30)
    start_time = timestamp - time_window
    
    query = select(
        Location.id,
        Location.name,
        Location.geometry,
        Location.location_type,
        CrowdData.crowd_count,
        CrowdData.density_level,
        CrowdData.timestamp
    ).join(CrowdData).where(
        CrowdData.timestamp >= start_time,
        CrowdData.timestamp <= timestamp,
        Location.is_active == True
    ).order_by(CrowdData.timestamp.desc())
    
    result = await db.execute(query)
    heatmap_data = []
    
    for row in result:
        heatmap_data.append({
            "location_id": row.id,
            "name": row.name,
            "geometry": str(row.geometry),
            "location_type": row.location_type,
            "crowd_count": row.crowd_count,
            "density_level": row.density_level,
            "timestamp": row.timestamp.isoformat()
        })
    
    return {
        "timestamp": timestamp.isoformat(),
        "data": heatmap_data
    }

@router.get("/events", response_model=List[dict])
async def get_events(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    event_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get scheduled events"""
    query = select(Event)
    
    if start_date:
        query = query.where(Event.start_time >= start_date)
    if end_date:
        query = query.where(Event.end_time <= end_date)
    if event_type:
        query = query.where(Event.event_type == event_type)
    
    query = query.order_by(Event.start_time)
    result = await db.execute(query)
    events = result.scalars().all()
    
    return [
        {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "event_type": event.event_type,
            "location_id": event.location_id,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "expected_attendance": event.expected_attendance,
            "status": event.status,
            "priority_level": event.priority_level
        }
        for event in events
    ]

@router.get("/analytics/crowd-trends")
async def get_crowd_trends(
    location_id: Optional[int] = Query(None),
    days: int = Query(7, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get crowd trend analytics"""
    since = datetime.utcnow() - timedelta(days=days)
    
    query = select(
        CrowdData.location_id,
        Location.name,
        func.avg(CrowdData.crowd_count).label("avg_crowd"),
        func.max(CrowdData.crowd_count).label("max_crowd"),
        func.min(CrowdData.crowd_count).label("min_crowd"),
        func.count(CrowdData.id).label("data_points")
    ).join(Location).where(
        CrowdData.timestamp >= since
    )
    
    if location_id:
        query = query.where(CrowdData.location_id == location_id)
    
    query = query.group_by(CrowdData.location_id, Location.name)
    result = await db.execute(query)
    
    trends = []
    for row in result:
        trends.append({
            "location_id": row.location_id,
            "location_name": row.name,
            "average_crowd": float(row.avg_crowd),
            "max_crowd": row.max_crowd,
            "min_crowd": row.min_crowd,
            "data_points": row.data_points
        })
    
    return {
        "period_days": days,
        "trends": trends
    }
