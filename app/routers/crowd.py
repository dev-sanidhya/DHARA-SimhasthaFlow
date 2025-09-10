"""
Crowd management API router
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database.database import get_db
from app.models.database_models import CrowdData as DBCrowdData, Zone as DBZone
from app.models.schemas import CrowdStatusResponse, CrowdDensity, CrowdLevel

router = APIRouter()

def determine_crowd_level(occupancy: int, capacity: int) -> CrowdLevel:
    """Determine crowd level based on occupancy percentage"""
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

def get_trend(current_occupancy: int, previous_occupancy: int) -> str:
    """Determine crowd trend"""
    if current_occupancy > previous_occupancy * 1.1:
        return "increasing"
    elif current_occupancy < previous_occupancy * 0.9:
        return "decreasing"
    else:
        return "stable"

def get_peak_hours() -> List[str]:
    """Get typical peak hours for religious gatherings"""
    return [
        "05:00-07:00 (Morning prayers)",
        "11:00-13:00 (Midday rituals)",
        "17:00-20:00 (Evening aarti)",
        "22:00-24:00 (Night ceremonies)"
    ]

def generate_recommendations(zones: List[CrowdDensity]) -> List[str]:
    """Generate crowd management recommendations"""
    recommendations = []
    
    critical_zones = [z for z in zones if z.crowd_level == CrowdLevel.CRITICAL]
    high_zones = [z for z in zones if z.crowd_level == CrowdLevel.HIGH]
    
    if critical_zones:
        recommendations.append(f"URGENT: {len(critical_zones)} zone(s) at critical capacity - implement crowd control measures immediately")
        recommendations.append("Consider temporary entry restrictions to overcrowded areas")
        recommendations.append("Deploy additional security personnel to critical zones")
    
    if high_zones:
        recommendations.append(f"{len(high_zones)} zone(s) experiencing high crowds - monitor closely")
        recommendations.append("Direct visitors to alternative, less crowded areas")
    
    if len(critical_zones) + len(high_zones) > 3:
        recommendations.append("Consider activating emergency crowd dispersal protocols")
    
    recommendations.extend([
        "Maintain clear emergency evacuation routes",
        "Ensure adequate medical personnel are stationed",
        "Use public announcements to guide crowd flow",
        "Monitor weather conditions for crowd impact"
    ])
    
    return recommendations

@router.get("/crowd-status", response_model=CrowdStatusResponse)
async def get_crowd_status(db: Session = Depends(get_db)):
    """Get overall crowd status across all zones"""
    
    # Get all zones
    zones = db.query(DBZone).all()
    
    if not zones:
        raise HTTPException(status_code=404, detail="No zones found")
    
    crowd_densities = []
    total_occupancy = 0
    total_capacity = 0
    
    for zone in zones:
        # Get latest crowd data for this zone
        latest_crowd = db.query(DBCrowdData).filter(
            DBCrowdData.zone_id == zone.id
        ).order_by(DBCrowdData.timestamp.desc()).first()
        
        # Get previous crowd data for trend analysis
        previous_crowd = db.query(DBCrowdData).filter(
            DBCrowdData.zone_id == zone.id
        ).order_by(DBCrowdData.timestamp.desc()).offset(1).first()
        
        if latest_crowd:
            occupancy = latest_crowd.occupancy
            density = latest_crowd.density_per_sqm
            crowd_level = CrowdLevel(latest_crowd.crowd_level)
            timestamp = latest_crowd.timestamp
            
            # Determine trend
            if previous_crowd:
                trend = get_trend(occupancy, previous_crowd.occupancy)
            else:
                trend = "stable"
            
        else:
            # Use current zone data as fallback
            occupancy = zone.current_occupancy
            density = occupancy / max(zone.capacity * 0.1, 1)  # Estimate density
            crowd_level = determine_crowd_level(occupancy, zone.capacity)
            timestamp = datetime.utcnow()
            trend = "stable"
        
        crowd_densities.append(CrowdDensity(
            zone_id=zone.id,
            zone_name=zone.name,
            density_per_sqm=round(density, 2),
            crowd_level=crowd_level,
            timestamp=timestamp,
            trend=trend
        ))
        
        total_occupancy += occupancy
        total_capacity += zone.capacity
    
    # Determine overall crowd level
    overall_crowd_level = determine_crowd_level(total_occupancy, total_capacity)
    
    # Get peak hours
    peak_hours = get_peak_hours()
    
    # Generate recommendations
    recommendations = generate_recommendations(crowd_densities)
    
    return CrowdStatusResponse(
        overall_crowd_level=overall_crowd_level,
        zones=crowd_densities,
        peak_hours_today=peak_hours,
        recommendations=recommendations,
        last_updated=datetime.utcnow()
    )

@router.get("/crowd-status/{zone_id}", response_model=CrowdDensity)
async def get_zone_crowd_status(zone_id: str, db: Session = Depends(get_db)):
    """Get crowd status for a specific zone"""
    
    zone = db.query(DBZone).filter(DBZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    # Get latest crowd data
    latest_crowd = db.query(DBCrowdData).filter(
        DBCrowdData.zone_id == zone_id
    ).order_by(DBCrowdData.timestamp.desc()).first()
    
    # Get previous crowd data for trend
    previous_crowd = db.query(DBCrowdData).filter(
        DBCrowdData.zone_id == zone_id
    ).order_by(DBCrowdData.timestamp.desc()).offset(1).first()
    
    if latest_crowd:
        occupancy = latest_crowd.occupancy
        density = latest_crowd.density_per_sqm
        crowd_level = CrowdLevel(latest_crowd.crowd_level)
        timestamp = latest_crowd.timestamp
        
        if previous_crowd:
            trend = get_trend(occupancy, previous_crowd.occupancy)
        else:
            trend = "stable"
    else:
        # Fallback to zone data
        occupancy = zone.current_occupancy
        density = occupancy / max(zone.capacity * 0.1, 1)
        crowd_level = determine_crowd_level(occupancy, zone.capacity)
        timestamp = datetime.utcnow()
        trend = "stable"
    
    return CrowdDensity(
        zone_id=zone.id,
        zone_name=zone.name,
        density_per_sqm=round(density, 2),
        crowd_level=crowd_level,
        timestamp=timestamp,
        trend=trend
    )

@router.get("/crowd-history/{zone_id}", response_model=List[CrowdDensity])
async def get_zone_crowd_history(
    zone_id: str,
    hours: int = Query(24, ge=1, le=168),  # 1 hour to 1 week
    db: Session = Depends(get_db)
):
    """Get crowd history for a specific zone"""
    
    zone = db.query(DBZone).filter(DBZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    # Get crowd data for the specified time period
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    crowd_data = db.query(DBCrowdData).filter(
        DBCrowdData.zone_id == zone_id,
        DBCrowdData.timestamp >= start_time
    ).order_by(DBCrowdData.timestamp.desc()).all()
    
    if not crowd_data:
        return []
    
    # Convert to response format
    history = []
    for i, data in enumerate(crowd_data):
        # Calculate trend compared to previous entry
        if i < len(crowd_data) - 1:
            prev_data = crowd_data[i + 1]
            trend = get_trend(data.occupancy, prev_data.occupancy)
        else:
            trend = "stable"
        
        history.append(CrowdDensity(
            zone_id=data.zone_id,
            zone_name=zone.name,
            density_per_sqm=round(data.density_per_sqm, 2),
            crowd_level=CrowdLevel(data.crowd_level),
            timestamp=data.timestamp,
            trend=trend
        ))
    
    return history

@router.get("/crowd-analytics", response_model=dict)
async def get_crowd_analytics(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get crowd analytics and patterns"""
    
    start_time = datetime.utcnow() - timedelta(days=days)
    
    # Get all crowd data for the period
    crowd_data = db.query(DBCrowdData).filter(
        DBCrowdData.timestamp >= start_time
    ).all()
    
    if not crowd_data:
        return {
            "message": "No crowd data available for the specified period",
            "period_days": days
        }
    
    # Analyze patterns
    hourly_patterns = {}
    daily_patterns = {}
    zone_averages = {}
    
    for data in crowd_data:
        hour = data.timestamp.hour
        day = data.timestamp.strftime("%A")
        zone_id = data.zone_id
        
        # Hourly patterns
        if hour not in hourly_patterns:
            hourly_patterns[hour] = []
        hourly_patterns[hour].append(data.occupancy)
        
        # Daily patterns
        if day not in daily_patterns:
            daily_patterns[day] = []
        daily_patterns[day].append(data.occupancy)
        
        # Zone averages
        if zone_id not in zone_averages:
            zone_averages[zone_id] = []
        zone_averages[zone_id].append(data.occupancy)
    
    # Calculate averages
    hourly_avg = {hour: sum(occupancies) / len(occupancies) 
                  for hour, occupancies in hourly_patterns.items()}
    daily_avg = {day: sum(occupancies) / len(occupancies) 
                 for day, occupancies in daily_patterns.items()}
    zone_avg = {zone_id: sum(occupancies) / len(occupancies) 
                for zone_id, occupancies in zone_averages.items()}
    
    # Find peak times
    peak_hour = max(hourly_avg, key=hourly_avg.get) if hourly_avg else None
    peak_day = max(daily_avg, key=daily_avg.get) if daily_avg else None
    
    return {
        "analysis_period_days": days,
        "total_data_points": len(crowd_data),
        "hourly_patterns": hourly_avg,
        "daily_patterns": daily_avg,
        "zone_averages": zone_avg,
        "peak_hour": peak_hour,
        "peak_day": peak_day,
        "insights": [
            f"Peak crowd hour: {peak_hour}:00" if peak_hour else "No peak hour identified",
            f"Busiest day: {peak_day}" if peak_day else "No peak day identified",
            f"Average daily crowd variations: {len(set(daily_patterns.keys()))} different patterns",
            f"Most crowded zones: {len([z for z in zone_avg.values() if z > 1000])} zones with high traffic"
        ]
    }
