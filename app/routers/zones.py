"""
Zone management API router
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.database import get_db
from app.models.database_models import Zone as DBZone, CrowdData as DBCrowdData
from app.models.schemas import ZoneResponse, Zone, ZoneStatus, ZoneType, Coordinate, CrowdLevel
from datetime import datetime

router = APIRouter()

def calculate_occupancy_percentage(occupancy: int, capacity: int) -> float:
    """Calculate occupancy percentage"""
    if capacity == 0:
        return 0.0
    return round((occupancy / capacity) * 100, 1)

def estimate_wait_time(occupancy: int, capacity: int, zone_type: str) -> Optional[int]:
    """Estimate wait time based on occupancy and zone type"""
    occupancy_percentage = (occupancy / capacity) * 100 if capacity > 0 else 0
    
    if occupancy_percentage < 40:
        return None  # No significant wait time
    
    # Base wait times by zone type (in minutes)
    base_wait_times = {
        "temple": 15,
        "ghat": 10,
        "parking": 5,
        "medical": 20,
        "security": 5,
        "food": 12,
        "accommodation": 30
    }
    
    base_time = base_wait_times.get(zone_type, 10)
    
    # Scale wait time based on occupancy
    if occupancy_percentage >= 90:
        return base_time * 3
    elif occupancy_percentage >= 70:
        return base_time * 2
    elif occupancy_percentage >= 50:
        return int(base_time * 1.5)
    else:
        return base_time

def determine_crowd_level_from_occupancy(occupancy: int, capacity: int) -> CrowdLevel:
    """Determine crowd level based on occupancy"""
    if capacity == 0:
        return CrowdLevel.LOW
    
    percentage = (occupancy / capacity) * 100
    
    if percentage >= 90:
        return CrowdLevel.CRITICAL
    elif percentage >= 70:
        return CrowdLevel.HIGH
    elif percentage >= 40:
        return CrowdLevel.MEDIUM
    else:
        return CrowdLevel.LOW

@router.get("/zones", response_model=ZoneResponse)
async def get_all_zones(
    zone_type: Optional[ZoneType] = Query(None),
    include_occupancy: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all zones with optional filtering by type"""
    
    query = db.query(DBZone)
    
    if zone_type:
        query = query.filter(DBZone.type == zone_type.value)
    
    db_zones = query.all()
    
    zones = []
    for db_zone in db_zones:
        # Get current occupancy from latest crowd data if requested
        if include_occupancy:
            latest_crowd = db.query(DBCrowdData).filter(
                DBCrowdData.zone_id == db_zone.id
            ).order_by(DBCrowdData.timestamp.desc()).first()
            
            current_occupancy = latest_crowd.occupancy if latest_crowd else db_zone.current_occupancy
        else:
            current_occupancy = db_zone.current_occupancy
        
        # Convert coordinates from JSON to Coordinate objects
        coordinates = [
            Coordinate(latitude=coord[0], longitude=coord[1])
            for coord in db_zone.coordinates
        ]
        
        zone = Zone(
            id=db_zone.id,
            name=db_zone.name,
            type=ZoneType(db_zone.type),
            coordinates=coordinates,
            center=Coordinate(latitude=db_zone.center_lat, longitude=db_zone.center_lng),
            capacity=db_zone.capacity,
            current_occupancy=current_occupancy,
            amenities=db_zone.amenities or [],
            accessibility_features=db_zone.accessibility_features or [],
            description=db_zone.description
        )
        
        zones.append(zone)
    
    return ZoneResponse(
        zones=zones,
        total_zones=len(zones)
    )

@router.get("/zones/{zone_id}", response_model=Zone)
async def get_zone_by_id(zone_id: str, db: Session = Depends(get_db)):
    """Get a specific zone by ID"""
    
    db_zone = db.query(DBZone).filter(DBZone.id == zone_id).first()
    
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    # Get latest occupancy
    latest_crowd = db.query(DBCrowdData).filter(
        DBCrowdData.zone_id == zone_id
    ).order_by(DBCrowdData.timestamp.desc()).first()
    
    current_occupancy = latest_crowd.occupancy if latest_crowd else db_zone.current_occupancy
    
    # Convert coordinates
    coordinates = [
        Coordinate(latitude=coord[0], longitude=coord[1])
        for coord in db_zone.coordinates
    ]
    
    return Zone(
        id=db_zone.id,
        name=db_zone.name,
        type=ZoneType(db_zone.type),
        coordinates=coordinates,
        center=Coordinate(latitude=db_zone.center_lat, longitude=db_zone.center_lng),
        capacity=db_zone.capacity,
        current_occupancy=current_occupancy,
        amenities=db_zone.amenities or [],
        accessibility_features=db_zone.accessibility_features or [],
        description=db_zone.description
    )

@router.get("/zones/{zone_id}/status", response_model=ZoneStatus)
async def get_zone_status(zone_id: str, db: Session = Depends(get_db)):
    """Get detailed status of a specific zone"""
    
    db_zone = db.query(DBZone).filter(DBZone.id == zone_id).first()
    
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    # Get latest crowd data
    latest_crowd = db.query(DBCrowdData).filter(
        DBCrowdData.zone_id == zone_id
    ).order_by(DBCrowdData.timestamp.desc()).first()
    
    if latest_crowd:
        current_occupancy = latest_crowd.occupancy
        last_updated = latest_crowd.timestamp
    else:
        current_occupancy = db_zone.current_occupancy
        last_updated = datetime.utcnow()
    
    # Calculate metrics
    occupancy_percentage = calculate_occupancy_percentage(current_occupancy, db_zone.capacity)
    crowd_level = determine_crowd_level_from_occupancy(current_occupancy, db_zone.capacity)
    wait_time = estimate_wait_time(current_occupancy, db_zone.capacity, db_zone.type)
    
    return ZoneStatus(
        zone_id=db_zone.id,
        zone_name=db_zone.name,
        current_occupancy=current_occupancy,
        capacity=db_zone.capacity,
        occupancy_percentage=occupancy_percentage,
        crowd_level=crowd_level,
        estimated_wait_time_minutes=wait_time,
        last_updated=last_updated
    )

@router.get("/zones/status/all", response_model=List[ZoneStatus])
async def get_all_zones_status(db: Session = Depends(get_db)):
    """Get status of all zones"""
    
    db_zones = db.query(DBZone).all()
    
    if not db_zones:
        return []
    
    zone_statuses = []
    
    for db_zone in db_zones:
        # Get latest crowd data
        latest_crowd = db.query(DBCrowdData).filter(
            DBCrowdData.zone_id == db_zone.id
        ).order_by(DBCrowdData.timestamp.desc()).first()
        
        if latest_crowd:
            current_occupancy = latest_crowd.occupancy
            last_updated = latest_crowd.timestamp
        else:
            current_occupancy = db_zone.current_occupancy
            last_updated = datetime.utcnow()
        
        # Calculate metrics
        occupancy_percentage = calculate_occupancy_percentage(current_occupancy, db_zone.capacity)
        crowd_level = determine_crowd_level_from_occupancy(current_occupancy, db_zone.capacity)
        wait_time = estimate_wait_time(current_occupancy, db_zone.capacity, db_zone.type)
        
        zone_status = ZoneStatus(
            zone_id=db_zone.id,
            zone_name=db_zone.name,
            current_occupancy=current_occupancy,
            capacity=db_zone.capacity,
            occupancy_percentage=occupancy_percentage,
            crowd_level=crowd_level,
            estimated_wait_time_minutes=wait_time,
            last_updated=last_updated
        )
        
        zone_statuses.append(zone_status)
    
    return zone_statuses

@router.get("/zones/type/{zone_type}", response_model=List[Zone])
async def get_zones_by_type(zone_type: ZoneType, db: Session = Depends(get_db)):
    """Get all zones of a specific type"""
    
    db_zones = db.query(DBZone).filter(DBZone.type == zone_type.value).all()
    
    zones = []
    for db_zone in db_zones:
        # Get latest occupancy
        latest_crowd = db.query(DBCrowdData).filter(
            DBCrowdData.zone_id == db_zone.id
        ).order_by(DBCrowdData.timestamp.desc()).first()
        
        current_occupancy = latest_crowd.occupancy if latest_crowd else db_zone.current_occupancy
        
        # Convert coordinates
        coordinates = [
            Coordinate(latitude=coord[0], longitude=coord[1])
            for coord in db_zone.coordinates
        ]
        
        zone = Zone(
            id=db_zone.id,
            name=db_zone.name,
            type=ZoneType(db_zone.type),
            coordinates=coordinates,
            center=Coordinate(latitude=db_zone.center_lat, longitude=db_zone.center_lng),
            capacity=db_zone.capacity,
            current_occupancy=current_occupancy,
            amenities=db_zone.amenities or [],
            accessibility_features=db_zone.accessibility_features or [],
            description=db_zone.description
        )
        
        zones.append(zone)
    
    return zones

@router.get("/zones/search", response_model=List[Zone])
async def search_zones(
    query: str = Query(..., min_length=2),
    zone_type: Optional[ZoneType] = Query(None),
    has_amenity: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Search zones by name, type, or amenities"""
    
    db_query = db.query(DBZone)
    
    # Filter by name (case-insensitive)
    db_query = db_query.filter(DBZone.name.ilike(f"%{query}%"))
    
    # Filter by type if specified
    if zone_type:
        db_query = db_query.filter(DBZone.type == zone_type.value)
    
    db_zones = db_query.all()
    
    # Filter by amenity if specified (done in Python since SQLite JSON handling is limited)
    if has_amenity:
        db_zones = [zone for zone in db_zones 
                   if zone.amenities and has_amenity.lower() in [a.lower() for a in zone.amenities]]
    
    zones = []
    for db_zone in db_zones:
        # Get latest occupancy
        latest_crowd = db.query(DBCrowdData).filter(
            DBCrowdData.zone_id == db_zone.id
        ).order_by(DBCrowdData.timestamp.desc()).first()
        
        current_occupancy = latest_crowd.occupancy if latest_crowd else db_zone.current_occupancy
        
        # Convert coordinates
        coordinates = [
            Coordinate(latitude=coord[0], longitude=coord[1])
            for coord in db_zone.coordinates
        ]
        
        zone = Zone(
            id=db_zone.id,
            name=db_zone.name,
            type=ZoneType(db_zone.type),
            coordinates=coordinates,
            center=Coordinate(latitude=db_zone.center_lat, longitude=db_zone.center_lng),
            capacity=db_zone.capacity,
            current_occupancy=current_occupancy,
            amenities=db_zone.amenities or [],
            accessibility_features=db_zone.accessibility_features or [],
            description=db_zone.description
        )
        
        zones.append(zone)
    
    return zones
