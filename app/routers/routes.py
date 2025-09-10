"""
Routes API router for navigation and pathfinding
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import math

from app.database.database import get_db
from app.models.database_models import Route as DBRoute, Zone as DBZone, RoadNetwork, CrowdData
from app.models.schemas import (
    RouteRequest, RouteResponse, Route, RoutePoint, Coordinate, 
    PriorityLevel, CrowdLevel
)

router = APIRouter()

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def get_crowd_level_for_route(db: Session, lat: float, lng: float) -> str:
    """Get crowd level for a specific route point"""
    # Find nearest zone
    zones = db.query(DBZone).all()
    min_distance = float('inf')
    nearest_zone = None
    
    for zone in zones:
        distance = calculate_distance(lat, lng, zone.center_lat, zone.center_lng)
        if distance < min_distance:
            min_distance = distance
            nearest_zone = zone
    
    if nearest_zone and min_distance < 0.5:  # Within 500m
        # Get latest crowd data for this zone
        crowd_data = db.query(CrowdData).filter(
            CrowdData.zone_id == nearest_zone.id
        ).order_by(CrowdData.timestamp.desc()).first()
        
        if crowd_data:
            return crowd_data.crowd_level
    
    return "low"

def calculate_safety_score(crowd_level: str, road_width: float, accessibility: bool) -> float:
    """Calculate safety score for a route"""
    base_score = 10.0
    
    # Crowd level impact
    crowd_penalties = {
        "low": 0,
        "medium": -1,
        "high": -3,
        "critical": -5
    }
    base_score += crowd_penalties.get(crowd_level, 0)
    
    # Road width impact
    if road_width < 4:
        base_score -= 2
    elif road_width > 8:
        base_score += 1
    
    # Accessibility bonus
    if accessibility:
        base_score += 0.5
    
    return max(0, min(10, base_score))

def generate_route_points(start: Coordinate, end: Coordinate, db: Session) -> List[RoutePoint]:
    """Generate route points between start and end coordinates"""
    # Simple implementation - in real system this would use OSM/Google Maps routing
    points = []
    
    # Add start point
    points.append(RoutePoint(
        coordinates=start,
        instruction="Start your journey",
        estimated_time_minutes=0
    ))
    
    # Generate intermediate waypoints (simplified)
    lat_diff = end.latitude - start.latitude
    lng_diff = end.longitude - start.longitude
    
    # Add 2-3 intermediate points
    for i in range(1, 3):
        progress = i / 3
        intermediate_lat = start.latitude + (lat_diff * progress)
        intermediate_lng = start.longitude + (lng_diff * progress)
        
        points.append(RoutePoint(
            coordinates=Coordinate(latitude=intermediate_lat, longitude=intermediate_lng),
            instruction=f"Continue straight for {int(200 * progress)}m",
            estimated_time_minutes=int(5 * progress)
        ))
    
    # Add end point
    points.append(RoutePoint(
        coordinates=end,
        instruction="You have arrived at your destination",
        estimated_time_minutes=15
    ))
    
    return points

@router.post("/routes/{priority}", response_model=RouteResponse)
async def get_routes(
    priority: PriorityLevel,
    route_request: RouteRequest,
    db: Session = Depends(get_db)
):
    """Get route options based on priority and preferences"""
    
    # Calculate basic route metrics
    distance = calculate_distance(
        route_request.start.latitude,
        route_request.start.longitude,
        route_request.end.latitude,
        route_request.end.longitude
    )
    
    # Generate route points
    route_points = generate_route_points(route_request.start, route_request.end, db)
    
    # Get crowd level for the route
    mid_lat = (route_request.start.latitude + route_request.end.latitude) / 2
    mid_lng = (route_request.start.longitude + route_request.end.longitude) / 2
    crowd_level = get_crowd_level_for_route(db, mid_lat, mid_lng)
    
    # Calculate safety score
    safety_score = calculate_safety_score(crowd_level, 8.0, route_request.accessibility_required)
    
    # Base time calculation (5 km/h walking speed)
    base_time = int((distance * 60) / 5)
    
    # Adjust time based on crowd and priority
    crowd_multipliers = {
        "low": 1.0,
        "medium": 1.2,
        "high": 1.5,
        "critical": 2.0
    }
    
    if route_request.avoid_crowded_areas and crowd_level in ["high", "critical"]:
        # Alternative route - longer but less crowded
        alternative_time = int(base_time * 1.3)
        alternative_crowd_level = "medium"
        alternative_safety_score = calculate_safety_score(alternative_crowd_level, 6.0, route_request.accessibility_required)
        
        routes = [
            # Main route
            Route(
                id=str(uuid.uuid4()),
                start=route_request.start,
                end=route_request.end,
                points=route_points,
                total_distance_km=distance,
                estimated_time_minutes=int(base_time * crowd_multipliers[crowd_level]),
                priority=priority,
                crowd_level=CrowdLevel(crowd_level),
                safety_score=safety_score,
                created_at=datetime.utcnow()
            ),
            # Alternative route
            Route(
                id=str(uuid.uuid4()),
                start=route_request.start,
                end=route_request.end,
                points=route_points,  # In real system, this would be different
                total_distance_km=distance * 1.2,
                estimated_time_minutes=alternative_time,
                priority=priority,
                crowd_level=CrowdLevel(alternative_crowd_level),
                safety_score=alternative_safety_score,
                created_at=datetime.utcnow()
            )
        ]
        
        # Recommend the safer route
        recommended_route_id = routes[1].id if alternative_safety_score > safety_score else routes[0].id
        
    else:
        # Single route
        route = Route(
            id=str(uuid.uuid4()),
            start=route_request.start,
            end=route_request.end,
            points=route_points,
            total_distance_km=distance,
            estimated_time_minutes=int(base_time * crowd_multipliers[crowd_level]),
            priority=priority,
            crowd_level=CrowdLevel(crowd_level),
            safety_score=safety_score,
            created_at=datetime.utcnow()
        )
        
        routes = [route]
        recommended_route_id = route.id
    
    # Store routes in database
    for route in routes:
        db_route = DBRoute(
            id=route.id,
            start_lat=route.start.latitude,
            start_lng=route.start.longitude,
            end_lat=route.end.latitude,
            end_lng=route.end.longitude,
            points=[{
                "coordinates": {"latitude": p.coordinates.latitude, "longitude": p.coordinates.longitude},
                "instruction": p.instruction,
                "estimated_time_minutes": p.estimated_time_minutes
            } for p in route.points],
            total_distance_km=route.total_distance_km,
            estimated_time_minutes=route.estimated_time_minutes,
            priority=route.priority.value,
            crowd_level=route.crowd_level.value,
            safety_score=route.safety_score
        )
        db.add(db_route)
    
    db.commit()
    
    return RouteResponse(
        routes=routes,
        recommended_route_id=recommended_route_id,
        alternative_count=len(routes) - 1
    )

@router.get("/routes/{route_id}", response_model=Route)
async def get_route_by_id(route_id: str, db: Session = Depends(get_db)):
    """Get a specific route by ID"""
    db_route = db.query(DBRoute).filter(DBRoute.id == route_id).first()
    
    if not db_route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Convert stored points back to RoutePoint objects
    route_points = []
    for point_data in db_route.points:
        route_points.append(RoutePoint(
            coordinates=Coordinate(
                latitude=point_data["coordinates"]["latitude"],
                longitude=point_data["coordinates"]["longitude"]
            ),
            instruction=point_data["instruction"],
            estimated_time_minutes=point_data["estimated_time_minutes"]
        ))
    
    return Route(
        id=db_route.id,
        start=Coordinate(latitude=db_route.start_lat, longitude=db_route.start_lng),
        end=Coordinate(latitude=db_route.end_lat, longitude=db_route.end_lng),
        points=route_points,
        total_distance_km=db_route.total_distance_km,
        estimated_time_minutes=db_route.estimated_time_minutes,
        priority=PriorityLevel(db_route.priority),
        crowd_level=CrowdLevel(db_route.crowd_level),
        safety_score=db_route.safety_score,
        created_at=db_route.created_at
    )

@router.get("/routes", response_model=List[Route])
async def get_recent_routes(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get recent routes"""
    db_routes = db.query(DBRoute).order_by(DBRoute.created_at.desc()).limit(limit).all()
    
    routes = []
    for db_route in db_routes:
        route_points = []
        for point_data in db_route.points:
            route_points.append(RoutePoint(
                coordinates=Coordinate(
                    latitude=point_data["coordinates"]["latitude"],
                    longitude=point_data["coordinates"]["longitude"]
                ),
                instruction=point_data["instruction"],
                estimated_time_minutes=point_data["estimated_time_minutes"]
            ))
        
        routes.append(Route(
            id=db_route.id,
            start=Coordinate(latitude=db_route.start_lat, longitude=db_route.start_lng),
            end=Coordinate(latitude=db_route.end_lat, longitude=db_route.end_lng),
            points=route_points,
            total_distance_km=db_route.total_distance_km,
            estimated_time_minutes=db_route.estimated_time_minutes,
            priority=PriorityLevel(db_route.priority),
            crowd_level=CrowdLevel(db_route.crowd_level),
            safety_score=db_route.safety_score,
            created_at=db_route.created_at
        ))
    
    return routes
