"""
Seed data for the database with realistic mock data for SimhasthaFlow system
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import asyncio
import logging
import random
from passlib.context import CryptContext

from app.database.database import get_db_session
from app.models.database_models import User, Zone, Route, CrowdData, WeatherData, Emergency, RoadNetwork

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def seed_database():
    """Seed the database with initial mock data"""
    db = get_db_session()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            logger.info("Database already seeded")
            return
        
        logger.info("Seeding database with initial data...")
        
        # Seed users
        seed_users(db)
        
        # Seed zones (temples, ghats, facilities)
        seed_zones(db)
        
        # Seed road network
        seed_road_network(db)
        
        # Seed weather data
        seed_weather_data(db)
        
        # Seed crowd data
        seed_crowd_data(db)
        
        # Seed emergency data
        seed_emergency_data(db)
        
        db.commit()
        logger.info("Database seeding completed successfully")
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def seed_users(db: Session):
    """Seed user data"""
    users = [
        User(
            username="admin",
            hashed_password=hash_password("admin123"),
            is_admin=True
        ),
        User(
            username="operator",
            hashed_password=hash_password("operator123"),
            is_admin=False
        )
    ]
    
    for user in users:
        db.add(user)
    
    logger.info("Seeded user data")

def seed_zones(db: Session):
    """Seed zone data with temples, ghats, and facilities for Ujjain Mahakumbh"""
    zones = [
        # Main Temples in Ujjain
        Zone(
            name="Shri Mahakaleshwar Jyotirlinga Temple",
            type="temple",
            coordinates=[
                [23.1825, 75.7685],
                [23.1830, 75.7685],
                [23.1830, 75.7690],
                [23.1825, 75.7690],
                [23.1825, 75.7685]
            ],
            center_lat=23.1827,
            center_lng=75.7687,
            capacity=10000,
            current_occupancy=7500,
            amenities=["prasadam", "water", "restrooms", "security", "medical"],
            accessibility_features=["wheelchair_access", "guide_rails", "audio_guidance"],
            description="One of the 12 Jyotirlingas, main attraction during Mahakumbh"
        ),
        Zone(
            name="Harsiddhi Temple",
            type="temple",
            coordinates=[
                [23.1820, 75.7650],
                [23.1825, 75.7650],
                [23.1825, 75.7655],
                [23.1820, 75.7655],
                [23.1820, 75.7650]
            ],
            center_lat=23.1822,
            center_lng=75.7652,
            capacity=3000,
            current_occupancy=1800,
            amenities=["prasadam", "water", "restrooms"],
            accessibility_features=["wheelchair_access"],
            description="Sacred Shakti Peeth temple"
        ),
        Zone(
            name="Chintaman Ganesh Temple",
            type="temple",
            coordinates=[
                [23.1815, 75.7700],
                [23.1820, 75.7700],
                [23.1820, 75.7705],
                [23.1815, 75.7705],
                [23.1815, 75.7700]
            ],
            center_lat=23.1817,
            center_lng=75.7702,
            capacity=2000,
            current_occupancy=1200,
            amenities=["prasadam", "water", "restrooms"],
            accessibility_features=["wheelchair_access"],
            description="Ancient Ganesh temple, part of traditional pilgrimage route"
        ),
        
        # Ghats on Shipra River
        Zone(
            name="Ram Ghat",
            type="ghat",
            coordinates=[
                [23.1800, 75.7620],
                [23.1800, 75.7680],
                [23.1780, 75.7680],
                [23.1780, 75.7620],
                [23.1800, 75.7620]
            ],
            center_lat=23.1790,
            center_lng=75.7650,
            capacity=15000,
            current_occupancy=12000,
            amenities=["boats", "prasadam", "water", "restrooms", "vendors", "medical"],
            accessibility_features=["ramps", "guide_rails", "announcements"],
            description="Main bathing ghat during Mahakumbh, primary Shahi Snan location"
        ),
        Zone(
            name="Triveni Ghat",
            type="ghat",
            coordinates=[
                [23.1770, 75.7610],
                [23.1770, 75.7670],
                [23.1750, 75.7670],
                [23.1750, 75.7610],
                [23.1770, 75.7610]
            ],
            center_lat=23.1760,
            center_lng=75.7640,
            capacity=8000,
            current_occupancy=4500,
            amenities=["boats", "prasadam", "water", "restrooms", "vendors"],
            accessibility_features=["ramps", "guide_rails"],
            description="Sacred confluence ghat for ritual bathing"
        ),
        Zone(
            name="Mangalnath Ghat",
            type="ghat",
            coordinates=[
                [23.1740, 75.7600],
                [23.1740, 75.7660],
                [23.1720, 75.7660],
                [23.1720, 75.7600],
                [23.1740, 75.7600]
            ],
            center_lat=23.1730,
            center_lng=75.7630,
            capacity=6000,
            current_occupancy=3200,
            amenities=["boats", "water", "restrooms"],
            accessibility_features=["ramps"],
            description="Ancient ghat near Mangalnath Temple"
        ),
        
        # Facilities for Mahakumbh
        Zone(
            name="Mahakumbh Main Parking",
            type="parking",
            coordinates=[
                [23.1900, 75.7550],
                [23.1900, 75.7650],
                [23.1850, 75.7650],
                [23.1850, 75.7550],
                [23.1900, 75.7550]
            ],
            center_lat=23.1875,
            center_lng=75.7600,
            capacity=2000,
            current_occupancy=1650,
            amenities=["security", "restrooms", "water", "bus_terminal"],
            accessibility_features=["wheelchair_access", "reserved_spaces"],
            description="Main vehicle parking facility for Mahakumbh pilgrims"
        ),
        Zone(
            name="District Hospital Ujjain",
            type="medical",
            coordinates=[
                [23.1950, 75.7750],
                [23.1950, 75.7780],
                [23.1920, 75.7780],
                [23.1920, 75.7750],
                [23.1950, 75.7750]
            ],
            center_lat=23.1935,
            center_lng=75.7765,
            capacity=300,
            current_occupancy=85,
            amenities=["emergency_care", "ambulance", "pharmacy", "restrooms", "icu"],
            accessibility_features=["wheelchair_access", "emergency_access"],
            description="Primary medical facility for Mahakumbh emergency care"
        ),
        Zone(
            name="Mahakumbh Police Control Center",
            type="security",
            coordinates=[
                [23.1850, 75.7700],
                [23.1850, 75.7730],
                [23.1830, 75.7730],
                [23.1830, 75.7700],
                [23.1850, 75.7700]
            ],
            center_lat=23.1840,
            center_lng=75.7715,
            capacity=100,
            current_occupancy=75,
            amenities=["security", "communication", "first_aid", "cctv_monitoring"],
            accessibility_features=["wheelchair_access"],
            description="Main security coordination center for Mahakumbh"
        ),
        Zone(
            name="Mahakumbh Bhandara (Community Kitchen)",
            type="food",
            coordinates=[
                [23.1820, 75.7550],
                [23.1820, 75.7580],
                [23.1800, 75.7580],
                [23.1800, 75.7550],
                [23.1820, 75.7550]
            ],
            center_lat=23.1810,
            center_lng=75.7565,
            capacity=3000,
            current_occupancy=1800,
            amenities=["free_food", "water", "restrooms", "seating", "prasadam"],
            accessibility_features=["wheelchair_access", "priority_service"],
            description="Large community kitchen serving free meals to pilgrims"
        ),
        Zone(
            name="Sadhu Camp Area",
            type="accommodation",
            coordinates=[
                [23.1750, 75.7500],
                [23.1750, 75.7550],
                [23.1700, 75.7550],
                [23.1700, 75.7500],
                [23.1750, 75.7500]
            ],
            center_lat=23.1725,
            center_lng=75.7525,
            capacity=5000,
            current_occupancy=3500,
            amenities=["water", "restrooms", "security", "medical_post"],
            accessibility_features=["basic_access"],
            description="Designated camping area for sadhus and religious orders"
        )
    ]
    
    for zone in zones:
        db.add(zone)
    
    logger.info("Seeded zone data")

def seed_road_network(db: Session):
    """Seed road network data for Ujjain"""
    roads = [
        RoadNetwork(
            name="Mahakaleshwar Temple Approach Road",
            road_type="main",
            start_lat=23.1750,
            start_lng=75.7650,
            end_lat=23.1830,
            end_lng=75.7690,
            length_km=1.2,
            width_meters=15.0,
            is_accessible=True,
            max_crowd_capacity=3000
        ),
        RoadNetwork(
            name="Ram Ghat Access Road",
            road_type="secondary",
            start_lat=23.1780,
            start_lng=75.7600,
            end_lat=23.1800,
            end_lng=75.7680,
            length_km=0.8,
            width_meters=10.0,
            is_accessible=True,
            max_crowd_capacity=1500
        ),
        RoadNetwork(
            name="Shipra River Road",
            road_type="main",
            start_lat=23.1720,
            start_lng=75.7580,
            end_lat=23.1800,
            end_lng=75.7680,
            length_km=2.0,
            width_meters=12.0,
            is_accessible=True,
            max_crowd_capacity=2500
        ),
        RoadNetwork(
            name="Mahakumbh Parking Road",
            road_type="service",
            start_lat=23.1850,
            start_lng=75.7550,
            end_lat=23.1900,
            end_lng=75.7650,
            length_km=1.5,
            width_meters=8.0,
            is_accessible=True,
            max_crowd_capacity=800
        ),
        RoadNetwork(
            name="Pedestrian Walkway North",
            road_type="pedestrian",
            start_lat=25.3110,
            start_lng=83.0100,
            end_lat=25.3120,
            end_lng=83.0110,
            length_km=0.2,
            width_meters=4.0,
            is_accessible=True,
            max_crowd_capacity=500
        ),
        RoadNetwork(
            name="Emergency Access Route",
            road_type="main",
            start_lat=25.3150,
            start_lng=83.0060,
            end_lat=25.3200,
            end_lng=83.0110,
            length_km=0.8,
            width_meters=10.0,
            is_accessible=True,
            max_crowd_capacity=1500
        )
    ]
    
    for road in roads:
        db.add(road)
    
    logger.info("Seeded road network data")

def seed_weather_data(db: Session):
    """Seed weather data"""
    now = datetime.utcnow()
    
    weather_records = [
        WeatherData(
            temperature_celsius=28.5,
            humidity_percent=65.0,
            wind_speed_kmh=12.0,
            condition="clear",
            visibility_km=10.0,
            uv_index=6,
            timestamp=now
        ),
        WeatherData(
            temperature_celsius=26.2,
            humidity_percent=70.0,
            wind_speed_kmh=8.0,
            condition="cloudy",
            visibility_km=8.0,
            uv_index=4,
            timestamp=now - timedelta(hours=1)
        ),
        WeatherData(
            temperature_celsius=24.8,
            humidity_percent=80.0,
            wind_speed_kmh=15.0,
            condition="rainy",
            visibility_km=5.0,
            uv_index=2,
            timestamp=now - timedelta(hours=2)
        )
    ]
    
    for weather in weather_records:
        db.add(weather)
    
    logger.info("Seeded weather data")

def seed_crowd_data(db: Session):
    """Seed crowd data"""
    # Get zones for crowd data
    zones = db.query(Zone).all()
    now = datetime.utcnow()
    
    for zone in zones:
        # Create historical crowd data
        for i in range(24):  # Last 24 hours
            timestamp = now - timedelta(hours=i)
            
            # Simulate crowd patterns
            if zone.type == "temple":
                base_occupancy = zone.current_occupancy
                if 6 <= timestamp.hour <= 10 or 17 <= timestamp.hour <= 21:
                    # Peak hours
                    occupancy = min(int(base_occupancy * 1.2), zone.capacity)
                else:
                    occupancy = max(int(base_occupancy * 0.6), 100)
            elif zone.type == "ghat":
                base_occupancy = zone.current_occupancy
                if 5 <= timestamp.hour <= 8 or 18 <= timestamp.hour <= 20:
                    # Peak hours for rituals
                    occupancy = min(int(base_occupancy * 1.5), zone.capacity)
                else:
                    occupancy = max(int(base_occupancy * 0.4), 200)
            else:
                # Other facilities
                occupancy = max(int(zone.current_occupancy * (0.5 + (i % 12) / 24)), 10)
            
            density = occupancy / (zone.capacity * 0.1)  # Assuming 10% of capacity is area
            
            if density > 8:
                crowd_level = "critical"
            elif density > 5:
                crowd_level = "high"
            elif density > 2:
                crowd_level = "medium"
            else:
                crowd_level = "low"
            
            crowd_data = CrowdData(
                zone_id=zone.id,
                occupancy=occupancy,
                density_per_sqm=density,
                crowd_level=crowd_level,
                timestamp=timestamp
            )
            db.add(crowd_data)
    
    logger.info("Seeded crowd data")

def seed_emergency_data(db: Session):
    """Seed emergency data for Ujjain Mahakumbh with 50+ realistic incidents"""
    
    # Base locations around Ujjain Mahakumbh areas
    base_locations = [
        {"name": "Mahakaleshwar Temple Complex", "lat": 23.1827, "lng": 75.7687},
        {"name": "Ram Ghat", "lat": 23.1790, "lng": 75.7650},
        {"name": "Triveni Ghat", "lat": 23.1760, "lng": 75.7640},
        {"name": "Mangalnath Ghat", "lat": 23.1730, "lng": 75.7630},
        {"name": "Harsiddhi Temple", "lat": 23.1822, "lng": 75.7652},
        {"name": "Chintaman Ganesh Temple", "lat": 23.1817, "lng": 75.7702},
        {"name": "Mahakumbh Main Parking", "lat": 23.1875, "lng": 75.7600},
        {"name": "Community Kitchen Area", "lat": 23.1810, "lng": 75.7565},
        {"name": "Sadhu Camp Area", "lat": 23.1725, "lng": 75.7525},
        {"name": "Medical Center", "lat": 23.1935, "lng": 75.7765},
        {"name": "Police Control Center", "lat": 23.1840, "lng": 75.7715},
        {"name": "Shipra River Bank", "lat": 23.1775, "lng": 75.7620},
        {"name": "Mahakumbh Entry Gate", "lat": 23.1850, "lng": 75.7550},
        {"name": "Pilgrims Accommodation", "lat": 23.1700, "lng": 75.7500},
        {"name": "VIP Area", "lat": 23.1880, "lng": 75.7720}
    ]
    
    # Emergency types and templates
    emergency_templates = {
        "medical": [
            "Elderly pilgrim collapsed during darshan queue",
            "Heat exhaustion case among devotees",
            "Heart attack reported during Aarti ceremony",
            "Diabetic emergency in crowded area",
            "Asthma attack due to incense smoke",
            "Dehydration case during long wait",
            "Blood pressure emergency in temple",
            "Panic attack in dense crowd",
            "Allergic reaction to prasadam",
            "Fainting due to prolonged standing",
            "Chest pain reported by elderly devotee",
            "Seizure case during religious ceremony",
            "Breathing difficulty in crowded ghat",
            "Pregnancy complication emergency",
            "Child fever case in hot weather"
        ],
        "stampede": [
            "Crowd surge during morning Aarti",
            "Heavy congestion at temple entrance",
            "Rush during Shahi Snan timing",
            "Bottleneck at ghat stairs",
            "Crowd panic during announcement",
            "Dense gathering at prasadam distribution",
            "Overcrowding at darshan queue",
            "Rush towards celebrity saint arrival",
            "Crowd movement issue at exit gates",
            "Congestion during meal distribution"
        ],
        "security": [
            "Unauthorized vehicle in restricted area",
            "Suspicious package reported",
            "Lost child case reported",
            "Pickpocketing incident reported",
            "Unauthorized drone activity",
            "Dispute between pilgrim groups",
            "Vandalism at temple property",
            "Theft reported in accommodation area",
            "Trespassing in VIP area",
            "Unattended luggage found",
            "Mobile phone theft reported",
            "Argument over queue jumping",
            "Fake sadhu identification issue",
            "Document forgery suspected"
        ],
        "fire": [
            "Small fire in community kitchen",
            "Electrical short circuit in lighting",
            "Cooking gas leak reported",
            "Incense holder fire incident",
            "Tent fire in accommodation area",
            "Generator overheating issue",
            "Electrical panel malfunction",
            "Campfire spread incident",
            "Kitchen chimney fire",
            "Transformer sparking reported"
        ],
        "natural_disaster": [
            "Heavy rainfall flooding low areas",
            "Strong winds damaging temporary structures",
            "Dust storm affecting visibility",
            "River water level rising concern",
            "Tree branch falling due to wind",
            "Lightning strike near metal structures",
            "Hailstorm damage to tents",
            "Flash flood warning issued"
        ]
    }
    
    severities = ["low", "medium", "high", "critical"]
    statuses = ["active", "resolved", "monitoring"]
    
    emergencies = []
    
    # Generate 55 emergency incidents
    for i in range(55):
        # Select random location with slight variation
        base_loc = random.choice(base_locations)
        lat_variation = random.uniform(-0.002, 0.002)  # Small area variation
        lng_variation = random.uniform(-0.002, 0.002)
        
        # Select emergency type and description
        emergency_type = random.choice(list(emergency_templates.keys()))
        description_template = random.choice(emergency_templates[emergency_type])
        
        # Add location context to description
        full_description = f"{description_template} near {base_loc['name']}"
        
        # Assign severity based on type
        if emergency_type == "stampede":
            severity = random.choice(["high", "critical"])
        elif emergency_type == "fire":
            severity = random.choice(["medium", "high", "critical"])
        elif emergency_type == "medical":
            severity = random.choice(["low", "medium", "high"])
        else:
            severity = random.choice(severities)
        
        # Assign status - more recent incidents are more likely to be active
        if i < 10:  # Recent incidents
            status = random.choice(["active", "monitoring", "resolved"])
        else:  # Older incidents
            status = random.choice(["resolved", "resolved", "monitoring"])
        
        # Generate realistic timestamps
        hours_ago = random.randint(1, 72)  # Within last 3 days
        created_time = datetime.utcnow() - timedelta(hours=hours_ago)
        
        resolved_time = None
        if status == "resolved":
            resolution_delay = random.randint(15, 180)  # 15 mins to 3 hours
            resolved_time = created_time + timedelta(minutes=resolution_delay)
        
        emergency = Emergency(
            type=emergency_type,
            location_lat=base_loc["lat"] + lat_variation,
            location_lng=base_loc["lng"] + lng_variation,
            description=full_description,
            severity=severity,
            status=status,
            created_at=created_time,
            resolved_at=resolved_time
        )
        
        emergencies.append(emergency)
    
    for emergency in emergencies:
        db.add(emergency)
    
    logger.info(f"Seeded emergency data with {len(emergencies)} incidents")
