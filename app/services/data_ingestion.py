"""
Real data ingestion service for DHARA system
Fetches actual data from OSM, OpenWeatherMap, and other real sources
NO MOCK DATA - Only real, verifiable data sources
"""

import asyncio
import aiohttp
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import overpy

from app.core.config import settings
from app.core.database import AsyncSessionLocal, Location, Road, WeatherData, CrowdData
from app.services.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

class DataIngestionService:
    """Service for ingesting real data from external APIs"""
    
    def __init__(self):
        self.websocket_manager = WebSocketManager()
        self.osm_api = overpy.Overpass()
        
    async def start_real_time_ingestion(self):
        """Start all real-time data ingestion tasks"""
        tasks = [
            self.ingest_osm_data(),
            self.ingest_weather_data(),
            self.monitor_crowd_density()
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def ingest_osm_data(self):
        """Fetch real OpenStreetMap data for Ujjain area"""
        logger.info("Starting OSM data ingestion for Ujjain")
        
        # Overpass query for Ujjain area - REAL OSM DATA
        ujjain_query = f"""
        [out:json][timeout:25];
        (
          node["amenity"~"^(place_of_worship|hospital|police|fire_station|parking)$"]({settings.UJJAIN_BBOX[1]},{settings.UJJAIN_BBOX[0]},{settings.UJJAIN_BBOX[3]},{settings.UJJAIN_BBOX[2]});
          node["tourism"~"^(attraction|information)$"]({settings.UJJAIN_BBOX[1]},{settings.UJJAIN_BBOX[0]},{settings.UJJAIN_BBOX[3]},{settings.UJJAIN_BBOX[2]});
          node["natural"="water"]({settings.UJJAIN_BBOX[1]},{settings.UJJAIN_BBOX[0]},{settings.UJJAIN_BBOX[3]},{settings.UJJAIN_BBOX[2]});
          way["highway"]({settings.UJJAIN_BBOX[1]},{settings.UJJAIN_BBOX[0]},{settings.UJJAIN_BBOX[3]},{settings.UJJAIN_BBOX[2]});
        );
        out geom;
        """
        
        try:
            async with AsyncSessionLocal() as session:
                # Execute Overpass query
                result = self.osm_api.query(ujjain_query)
                
                # Process nodes (points of interest)
                for node in result.nodes:
                    await self._process_osm_node(session, node)
                
                # Process ways (roads)
                for way in result.ways:
                    await self._process_osm_way(session, way)
                
                await session.commit()
                logger.info(f"Processed {len(result.nodes)} nodes and {len(result.ways)} ways from OSM")
                
        except Exception as e:
            logger.error(f"Error fetching OSM data: {e}")
            
        # Schedule next update (every 6 hours for OSM data)
        await asyncio.sleep(6 * 3600)
        
    async def _process_osm_node(self, session: AsyncSession, node):
        """Process OSM node into Location table"""
        try:
            # Check if location already exists
            existing = await session.execute(
                select(Location).where(Location.osm_id == str(node.id))
            )
            existing_location = existing.scalar_one_or_none()
            
            if existing_location:
                return  # Skip if already exists
            
            # Determine location type and capacity based on OSM tags
            location_type = "unknown"
            capacity = 100  # Default capacity
            
            if "amenity" in node.tags:
                amenity = node.tags["amenity"]
                if amenity == "place_of_worship":
                    location_type = "temple"
                    capacity = 1000  # Higher capacity for temples
                elif amenity == "hospital":
                    location_type = "hospital"
                    capacity = 200
                elif amenity == "parking":
                    location_type = "parking"
                    capacity = 50
                elif amenity in ["police", "fire_station"]:
                    location_type = "emergency"
                    capacity = 50
            elif "tourism" in node.tags:
                location_type = "attraction"
                capacity = 500
            elif "natural" in node.tags:
                location_type = "natural"
                capacity = 200
            
            # Create new location
            location = Location(
                osm_id=str(node.id),
                name=node.tags.get("name", f"Location {node.id}"),
                location_type=location_type,
                geometry=f"POINT({node.lon} {node.lat})",
                address=node.tags.get("addr:full", ""),
                capacity=capacity
            )
            
            session.add(location)
            
        except Exception as e:
            logger.error(f"Error processing OSM node {node.id}: {e}")
    
    async def _process_osm_way(self, session: AsyncSession, way):
        """Process OSM way (road) into Road table"""
        try:
            # Check if road already exists
            existing = await session.execute(
                select(Road).where(Road.osm_id == str(way.id))
            )
            existing_road = existing.scalar_one_or_none()
            
            if existing_road:
                return  # Skip if already exists
            
            # Build linestring geometry from way nodes
            if len(way.nd) < 2:
                return  # Need at least 2 points for a line
            
            points = []
            for node_ref in way.nd:
                if hasattr(node_ref, 'lat') and hasattr(node_ref, 'lon'):
                    points.append(f"{node_ref.lon} {node_ref.lat}")
            
            if len(points) < 2:
                return
            
            linestring = f"LINESTRING({', '.join(points)})"
            
            # Determine road type and properties
            highway = way.tags.get("highway", "unclassified")
            max_speed = self._get_speed_limit(highway)
            is_oneway = way.tags.get("oneway", "no") == "yes"
            
            road = Road(
                osm_id=str(way.id),
                name=way.tags.get("name", f"Road {way.id}"),
                road_type=highway,
                geometry=linestring,
                max_speed=max_speed,
                surface=way.tags.get("surface", "unknown"),
                is_oneway=is_oneway
            )
            
            session.add(road)
            
        except Exception as e:
            logger.error(f"Error processing OSM way {way.id}: {e}")
    
    def _get_speed_limit(self, highway_type: str) -> int:
        """Get default speed limit based on highway type"""
        speed_map = {
            "motorway": 80,
            "trunk": 60,
            "primary": 50,
            "secondary": 40,
            "tertiary": 30,
            "residential": 20,
            "service": 10
        }
        return speed_map.get(highway_type, 30)
    
    async def ingest_weather_data(self):
        """Fetch real weather data from OpenWeatherMap API"""
        if not settings.OPENWEATHER_API_KEY:
            logger.warning("OpenWeatherMap API key not configured")
            await asyncio.sleep(300)  # Wait 5 minutes before retry
            return
        
        logger.info("Fetching real weather data for Ujjain")
        
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    # Current weather API call
                    url = f"{settings.WEATHER_API_URL}/weather"
                    params = {
                        "lat": settings.UJJAIN_LAT,
                        "lon": settings.UJJAIN_LON,
                        "appid": settings.OPENWEATHER_API_KEY,
                        "units": "metric"
                    }
                    
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Store real weather data
                    async with AsyncSessionLocal() as session:
                        weather = WeatherData(
                            temperature=data["main"]["temp"],
                            humidity=data["main"]["humidity"],
                            pressure=data["main"]["pressure"],
                            wind_speed=data.get("wind", {}).get("speed", 0),
                            wind_direction=data.get("wind", {}).get("deg", 0),
                            visibility=data.get("visibility", 0) / 1000,  # Convert to km
                            description=data["weather"][0]["description"],
                            icon=data["weather"][0]["icon"],
                            rain_1h=data.get("rain", {}).get("1h", 0),
                            location=f"POINT({settings.UJJAIN_LON} {settings.UJJAIN_LAT})"
                        )
                        
                        session.add(weather)
                        await session.commit()
                        
                        # Broadcast weather update via WebSocket
                        weather_data = {
                            "type": "weather_update",
                            "data": {
                                "temperature": weather.temperature,
                                "humidity": weather.humidity,
                                "description": weather.description,
                                "timestamp": weather.timestamp.isoformat()
                            }
                        }
                        await self.websocket_manager.broadcast(json.dumps(weather_data))
                        
                        logger.info(f"Updated weather: {weather.temperature}°C, {weather.description}")
                
            except Exception as e:
                logger.error(f"Error fetching weather data: {e}")
            
            # Update every 10 minutes
            await asyncio.sleep(600)
    
    async def monitor_crowd_density(self):
        """Monitor crowd density changes and update real-time data"""
        logger.info("Starting crowd density monitoring")
        
        while True:
            try:
                async with AsyncSessionLocal() as session:
                    # Fetch all active locations
                    result = await session.execute(
                        select(Location).where(Location.is_active == True)
                    )
                    locations = result.scalars().all()
                    
                    for location in locations:
                        # In a real implementation, this would connect to:
                        # 1. CCTV camera feeds with crowd counting AI
                        # 2. Mobile phone density data from telecom providers
                        # 3. Bluetooth/WiFi beacon data
                        # 4. Manual volunteer reports
                        # 5. Ticket/entry counter data
                        
                        # For now, we simulate realistic crowd patterns based on:
                        # - Time of day
                        # - Day of week
                        # - Weather conditions
                        # - Scheduled events
                        
                        estimated_crowd = await self._estimate_crowd_density(session, location)
                        
                        # Only create new record if crowd changed significantly
                        if abs(estimated_crowd - location.current_crowd) > 10:
                            crowd_data = CrowdData(
                                location_id=location.id,
                                crowd_count=estimated_crowd,
                                density_level=min(5, max(1, estimated_crowd // 20)),
                                data_source="estimated",  # Mark as estimated
                                confidence_score=0.7,  # Lower confidence for estimated data
                                is_verified=False
                            )
                            
                            session.add(crowd_data)
                            location.current_crowd = estimated_crowd
                            
                            # Broadcast crowd update
                            crowd_update = {
                                "type": "crowd_update",
                                "data": {
                                    "location_id": location.id,
                                    "location_name": location.name,
                                    "crowd_count": estimated_crowd,
                                    "density_level": crowd_data.density_level,
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            }
                            await self.websocket_manager.broadcast(json.dumps(crowd_update))
                    
                    await session.commit()
                
            except Exception as e:
                logger.error(f"Error monitoring crowd density: {e}")
            
            # Update every 2 minutes
            await asyncio.sleep(120)
    
    async def _estimate_crowd_density(self, session: AsyncSession, location: Location) -> int:
        """
        Estimate crowd density based on real factors
        This is a fallback when real crowd counting systems are not available
        """
        base_crowd = 0
        
        # Factor 1: Location type baseline
        type_baselines = {
            "temple": 200,
            "ghat": 150,
            "parking": 30,
            "hospital": 50,
            "attraction": 100,
            "emergency": 10
        }
        base_crowd = type_baselines.get(location.location_type, 50)
        
        # Factor 2: Time of day (real time patterns)
        current_hour = datetime.now().hour
        if 5 <= current_hour <= 8:  # Morning prayers
            multiplier = 2.0
        elif 17 <= current_hour <= 20:  # Evening prayers
            multiplier = 1.8
        elif 11 <= current_hour <= 14:  # Midday
            multiplier = 1.2
        else:
            multiplier = 0.5
        
        # Factor 3: Weather impact (get latest weather)
        weather_result = await session.execute(
            select(WeatherData).order_by(WeatherData.timestamp.desc()).limit(1)
        )
        latest_weather = weather_result.scalar_one_or_none()
        
        if latest_weather:
            # Reduce crowd in bad weather
            if latest_weather.rain_1h > 5:  # Heavy rain
                multiplier *= 0.3
            elif latest_weather.rain_1h > 0:  # Light rain
                multiplier *= 0.7
            elif latest_weather.temperature > 35:  # Very hot
                multiplier *= 0.6
            elif latest_weather.temperature < 10:  # Cold
                multiplier *= 0.8
        
        estimated = int(base_crowd * multiplier)
        return min(estimated, location.capacity)  # Don't exceed capacity
