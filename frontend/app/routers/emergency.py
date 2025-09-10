"""
Emergency management API router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app.database.database import get_db
from app.models.database_models import Emergency as DBEmergency, Zone as DBZone
from app.models.schemas import (
    EmergencyRequest, EmergencyResponse, EmergencyType, EmergencyRoute,
    PriorityLevel, Coordinate
)
from app.routers.auth import get_current_user

router = APIRouter()

def find_nearest_medical_facility(emergency_lat: float, emergency_lng: float, db: Session) -> Coordinate:
    """Find the nearest medical facility to the emergency location"""
    medical_zones = db.query(DBZone).filter(DBZone.type == "medical").all()
    
    if not medical_zones:
        # Default medical facility coordinates (District Hospital from seed data)
        return Coordinate(latitude=25.3195, longitude=83.0105)
    
    # Calculate distances and find nearest
    min_distance = float('inf')
    nearest_facility = None
    
    for zone in medical_zones:
        # Simple distance calculation (in real system, use proper geodetic distance)
        distance = ((emergency_lat - zone.center_lat) ** 2 + (emergency_lng - zone.center_lng) ** 2) ** 0.5
        
        if distance < min_distance:
            min_distance = distance
            nearest_facility = zone
    
    return Coordinate(latitude=nearest_facility.center_lat, longitude=nearest_facility.center_lng)

def generate_evacuation_routes(emergency_type: EmergencyType, location: Coordinate, db: Session) -> List[EmergencyRoute]:
    """Generate evacuation routes based on emergency type and location"""
    routes = []
    
    # Define evacuation points based on emergency type
    if emergency_type == EmergencyType.STAMPEDE:
        evacuation_points = [
            Coordinate(latitude=25.3150, longitude=83.0065),  # Central Parking Area
            Coordinate(latitude=25.3180, longitude=83.0090),  # Annadaan Hall
            Coordinate(latitude=25.3200, longitude=83.0100),  # Open area near hospital
        ]
        safety_instructions = [
            "Move calmly towards the nearest evacuation point",
            "Do not run or push others",
            "Follow emergency personnel instructions",
            "Stay away from crowded areas",
            "Help elderly and disabled persons if possible"
        ]
        clearance_time = 15
        
    elif emergency_type == EmergencyType.FIRE:
        evacuation_points = [
            Coordinate(latitude=25.3140, longitude=83.0065),  # Parking area (away from structures)
            Coordinate(latitude=25.3050, longitude=83.0090),  # Ghat area (near water)
            Coordinate(latitude=25.3200, longitude=83.0110),  # Hospital area
        ]
        safety_instructions = [
            "Exit buildings immediately",
            "Stay low to avoid smoke inhalation",
            "Do not use elevators",
            "Move to open areas away from buildings",
            "Call fire department if not already notified"
        ]
        clearance_time = 20
        
    elif emergency_type == EmergencyType.MEDICAL:
        evacuation_points = [
            Coordinate(latitude=25.3195, longitude=83.0105),  # District Hospital
        ]
        safety_instructions = [
            "Clear the area for medical personnel",
            "Do not move injured person unless necessary",
            "Provide first aid if trained",
            "Call ambulance services",
            "Maintain clear access routes"
        ]
        clearance_time = 10
        
    elif emergency_type == EmergencyType.SECURITY:
        evacuation_points = [
            Coordinate(latitude=25.3115, longitude=83.0135),  # Police Control Room
            Coordinate(latitude=25.3150, longitude=83.0065),  # Central Parking
            Coordinate(latitude=25.3200, longitude=83.0100),  # Secure area near hospital
        ]
        safety_instructions = [
            "Move to secure locations",
            "Follow police instructions",
            "Avoid the incident area",
            "Report suspicious activities",
            "Stay calm and alert"
        ]
        clearance_time = 25
        
    elif emergency_type == EmergencyType.NATURAL_DISASTER:
        evacuation_points = [
            Coordinate(latitude=25.3200, longitude=83.0100),  # High ground near hospital
            Coordinate(latitude=25.3150, longitude=83.0065),  # Central Parking (elevated)
            Coordinate(latitude=25.3180, longitude=83.0090),  # Annadaan Hall (sturdy structure)
        ]
        safety_instructions = [
            "Move to higher ground if flooding",
            "Seek sturdy shelter",
            "Stay away from trees and power lines",
            "Follow official evacuation orders",
            "Take essential items only"
        ]
        clearance_time = 30
    
    else:
        # Default emergency response
        evacuation_points = [
            Coordinate(latitude=25.3150, longitude=83.0065),  # Central Parking Area
        ]
        safety_instructions = [
            "Move to safe areas",
            "Follow emergency personnel instructions",
            "Stay calm",
            "Help others if safe to do so"
        ]
        clearance_time = 20
    
    # Find nearest medical facilities
    medical_facilities = []
    medical_zones = db.query(DBZone).filter(DBZone.type == "medical").all()
    for zone in medical_zones:
        medical_facilities.append(Coordinate(latitude=zone.center_lat, longitude=zone.center_lng))
    
    if not medical_facilities:
        medical_facilities = [Coordinate(latitude=25.3195, longitude=83.0105)]  # Default hospital
    
    # Create emergency route
    route = EmergencyRoute(
        route_id=str(uuid.uuid4()),
        evacuation_points=evacuation_points,
        medical_facilities=medical_facilities,
        estimated_clearance_time_minutes=clearance_time,
        safety_instructions=safety_instructions
    )
    
    routes.append(route)
    return routes

@router.post("/emergency", response_model=EmergencyResponse)
async def report_emergency(
    emergency_request: EmergencyRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Report a new emergency and get response plan"""
    
    # Create emergency record
    emergency_id = str(uuid.uuid4())
    
    db_emergency = DBEmergency(
        id=emergency_id,
        type=emergency_request.type.value,
        location_lat=emergency_request.location.latitude,
        location_lng=emergency_request.location.longitude,
        description=emergency_request.description,
        severity=emergency_request.severity.value,
        status="active"
    )
    
    db.add(db_emergency)
    db.commit()
    
    # Generate evacuation routes
    evacuation_routes = generate_evacuation_routes(
        emergency_request.type,
        emergency_request.location,
        db
    )
    
    # Find nearest medical facility
    nearest_medical = find_nearest_medical_facility(
        emergency_request.location.latitude,
        emergency_request.location.longitude,
        db
    )
    
    # Emergency contacts
    emergency_contacts = [
        "Police: 100",
        "Fire: 101",
        "Ambulance: 108",
        "Disaster Management: 1070",
        "Control Room: +91-542-2345678"
    ]
    
    # General instructions based on emergency type
    type_instructions = {
        EmergencyType.MEDICAL: [
            "Medical emergency reported and response initiated",
            "Ambulance services have been notified",
            "Keep the patient stable and conscious",
            "Ensure clear access for medical personnel"
        ],
        EmergencyType.FIRE: [
            "Fire emergency - evacuation in progress",
            "Fire department has been alerted",
            "All personnel must evacuate immediately",
            "Do not attempt to fight large fires"
        ],
        EmergencyType.STAMPEDE: [
            "Crowd control measures activated",
            "Security personnel deployed to manage crowd",
            "All entry points to affected area closed",
            "Alternative routes have been established"
        ],
        EmergencyType.SECURITY: [
            "Security incident reported",
            "Law enforcement has been notified",
            "Area under security lockdown",
            "Cooperate with security personnel"
        ],
        EmergencyType.NATURAL_DISASTER: [
            "Natural disaster response activated",
            "Disaster management team notified",
            "Follow official evacuation orders",
            "Stay updated with official announcements"
        ]
    }
    
    instructions = type_instructions.get(emergency_request.type, [
        "Emergency response initiated",
        "Follow evacuation procedures",
        "Stay calm and follow instructions"
    ])
    
    return EmergencyResponse(
        emergency_id=emergency_id,
        type=emergency_request.type,
        status="active",
        evacuation_routes=evacuation_routes,
        nearest_medical_facility=nearest_medical,
        emergency_contacts=emergency_contacts,
        instructions=instructions
    )

@router.get("/emergency/{emergency_id}", response_model=EmergencyResponse)
async def get_emergency_status(emergency_id: str, db: Session = Depends(get_db)):
    """Get status of a specific emergency"""
    
    db_emergency = db.query(DBEmergency).filter(DBEmergency.id == emergency_id).first()
    
    if not db_emergency:
        raise HTTPException(status_code=404, detail="Emergency not found")
    
    # Recreate the response (in real system, this would be stored)
    emergency_location = Coordinate(
        latitude=db_emergency.location_lat,
        longitude=db_emergency.location_lng
    )
    
    evacuation_routes = generate_evacuation_routes(
        EmergencyType(db_emergency.type),
        emergency_location,
        db
    )
    
    nearest_medical = find_nearest_medical_facility(
        db_emergency.location_lat,
        db_emergency.location_lng,
        db
    )
    
    emergency_contacts = [
        "Police: 100",
        "Fire: 101",
        "Ambulance: 108",
        "Disaster Management: 1070",
        "Control Room: +91-542-2345678"
    ]
    
    # Status-based instructions
    if db_emergency.status == "resolved":
        instructions = [
            "Emergency has been resolved",
            "Normal operations have resumed",
            "Thank you for your cooperation"
        ]
    elif db_emergency.status == "active":
        instructions = [
            "Emergency response in progress",
            "Follow all safety instructions",
            "Stay updated with official announcements"
        ]
    else:
        instructions = [
            "Emergency status under review",
            "Continue following safety protocols"
        ]
    
    return EmergencyResponse(
        emergency_id=db_emergency.id,
        type=EmergencyType(db_emergency.type),
        status=db_emergency.status,
        evacuation_routes=evacuation_routes,
        nearest_medical_facility=nearest_medical,
        emergency_contacts=emergency_contacts,
        instructions=instructions
    )

@router.get("/emergency", response_model=List[dict])
async def get_active_emergencies(db: Session = Depends(get_db)):
    """Get all active emergencies"""
    
    active_emergencies = db.query(DBEmergency).filter(
        DBEmergency.status == "active"
    ).order_by(DBEmergency.created_at.desc()).all()
    
    emergencies = []
    for emergency in active_emergencies:
        emergencies.append({
            "id": emergency.id,
            "type": emergency.type,
            "location": {
                "latitude": emergency.location_lat,
                "longitude": emergency.location_lng
            },
            "description": emergency.description,
            "severity": emergency.severity,
            "status": emergency.status,
            "created_at": emergency.created_at,
            "resolved_at": emergency.resolved_at
        })
    
    return emergencies

@router.put("/emergency/{emergency_id}/resolve")
async def resolve_emergency(
    emergency_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark an emergency as resolved (requires authentication)"""
    
    db_emergency = db.query(DBEmergency).filter(DBEmergency.id == emergency_id).first()
    
    if not db_emergency:
        raise HTTPException(status_code=404, detail="Emergency not found")
    
    if db_emergency.status == "resolved":
        raise HTTPException(status_code=400, detail="Emergency already resolved")
    
    # Update emergency status
    db_emergency.status = "resolved"
    db_emergency.resolved_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Emergency marked as resolved",
        "emergency_id": emergency_id,
        "resolved_at": db_emergency.resolved_at,
        "resolved_by": current_user.username
    }
