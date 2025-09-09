"""
Routing engine for DHARA system using real road network data
Calculates optimal routes avoiding crowded areas
"""

import asyncio
from typing import List, Dict, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import math
import httpx
import logging

from app.core.config import settings
from app.core.database import Road, Location, CrowdData

logger = logging.getLogger(__name__)

class RoutingEngine:
    """Real-time routing engine with crowd avoidance"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_optimal_route(
        self, 
        source_lat: float, 
        source_lon: float, 
        dest_lat: float, 
        dest_lon: float, 
        avoid_crowds: bool = True
    ) -> Dict:
        """Calculate optimal route between two points"""
        
        # Try Google Maps API first if available
        if settings.GOOGLE_MAPS_API_KEY:
            google_route = await self._get_google_route(
                source_lat, source_lon, dest_lat, dest_lon, avoid_crowds
            )
            if google_route:
                return google_route
        
        # Fallback to OSM-based routing
        return await self._calculate_osm_route(
            source_lat, source_lon, dest_lat, dest_lon, avoid_crowds
        )
    
    async def _get_google_route(
        self, 
        source_lat: float, 
        source_lon: float, 
        dest_lat: float, 
        dest_lon: float, 
        avoid_crowds: bool
    ) -> Optional[Dict]:
        """Get route from Google Maps Directions API"""
        try:
            async with httpx.AsyncClient() as client:
                url = "https://maps.googleapis.com/maps/api/directions/json"
                params = {
                    "origin": f"{source_lat},{source_lon}",
                    "destination": f"{dest_lat},{dest_lon}",
                    "mode": "walking",  # Appropriate for crowd management
                    "alternatives": "true",
                    "key": settings.GOOGLE_MAPS_API_KEY
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data["status"] == "OK" and data["routes"]:
                    route = data["routes"][0]  # Primary route
                    
                    # Apply crowd avoidance if requested
                    if avoid_crowds:
                        route = await self._apply_crowd_avoidance(route)
                    
                    return {
                        "source": "google_maps",
                        "distance": route["legs"][0]["distance"]["value"],  # meters
                        "duration": route["legs"][0]["duration"]["value"],  # seconds
                        "polyline": route["overview_polyline"]["points"],
                        "steps": [
                            {
                                "instruction": step["html_instructions"],
                                "distance": step["distance"]["value"],
                                "duration": step["duration"]["value"]
                            }
                            for step in route["legs"][0]["steps"]
                        ],
                        "crowd_score": await self._calculate_route_crowd_score(route),
                        "recommended": True
                    }
                
        except Exception as e:
            logger.error(f"Error fetching Google route: {e}")
        
        return None
    
    async def _calculate_osm_route(
        self, 
        source_lat: float, 
        source_lon: float, 
        dest_lat: float, 
        dest_lon: float, 
        avoid_crowds: bool
    ) -> Dict:
        """Calculate route using OSM road network data"""
        
        # Find nearest roads to source and destination
        source_road = await self._find_nearest_road(source_lat, source_lon)
        dest_road = await self._find_nearest_road(dest_lat, dest_lon)
        
        if not source_road or not dest_road:
            # Direct route as fallback
            distance = self._haversine_distance(source_lat, source_lon, dest_lat, dest_lon)
            return {
                "source": "direct",
                "distance": distance,
                "duration": int(distance / 1.4 * 60),  # Walking speed ~1.4 m/s
                "polyline": f"LINESTRING({source_lon} {source_lat}, {dest_lon} {dest_lat})",
                "steps": [
                    {
                        "instruction": f"Walk directly to destination",
                        "distance": distance,
                        "duration": int(distance / 1.4 * 60)
                    }
                ],
                "crowd_score": 0,
                "recommended": True
            }
        
        # Use A* algorithm on road network
        path = await self._astar_routing(source_road, dest_road, avoid_crowds)
        
        return {
            "source": "osm",
            "distance": path["distance"],
            "duration": path["duration"],
            "polyline": path["geometry"],
            "steps": path["steps"],
            "crowd_score": path["crowd_score"],
            "recommended": path["crowd_score"] < 3  # Recommend if low crowd
        }
    
    async def _find_nearest_road(self, lat: float, lon: float) -> Optional[Road]:
        """Find nearest road to given coordinates using PostGIS"""
        query = select(Road).order_by(
            func.ST_Distance(
                Road.geometry,
                func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
            )
        ).limit(1)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _astar_routing(
        self, 
        source_road: Road, 
        dest_road: Road, 
        avoid_crowds: bool
    ) -> Dict:
        """A* pathfinding algorithm on road network"""
        
        # Simplified A* implementation
        # In production, use a proper graph library like NetworkX
        
        # For now, return a direct route with crowd consideration
        distance = 500  # Placeholder
        crowd_score = 0
        
        if avoid_crowds:
            # Check for crowded locations along the route
            crowd_score = await self._get_route_crowd_impact(source_road, dest_road)
        
        return {
            "distance": distance,
            "duration": int(distance / 1.4 * 60),  # Walking speed
            "geometry": f"LINESTRING({source_road.geometry}, {dest_road.geometry})",
            "steps": [
                {
                    "instruction": f"Follow {source_road.name or 'road'} towards destination",
                    "distance": distance,
                    "duration": int(distance / 1.4 * 60)
                }
            ],
            "crowd_score": crowd_score
        }
    
    async def _get_route_crowd_impact(self, source_road: Road, dest_road: Road) -> int:
        """Calculate crowd impact score for a route (0-5 scale)"""
        
        # Get nearby crowded locations
        query = select(Location, CrowdData).join(CrowdData).where(
            CrowdData.density_level >= 3,  # High density
            func.ST_DWithin(
                Location.geometry,
                func.ST_MakeLine(source_road.geometry, dest_road.geometry),
                100  # Within 100 meters of route
            )
        )
        
        result = await self.db.execute(query)
        crowded_locations = result.fetchall()
        
        if len(crowded_locations) == 0:
            return 1  # Low crowd impact
        elif len(crowded_locations) <= 2:
            return 3  # Medium crowd impact
        else:
            return 5  # High crowd impact
    
    async def _apply_crowd_avoidance(self, google_route: Dict) -> Dict:
        """Apply crowd avoidance to Google Maps route"""
        # Analyze route for crowded areas and suggest modifications
        crowd_score = await self._calculate_route_crowd_score(google_route)
        google_route["crowd_score"] = crowd_score
        return google_route
    
    async def _calculate_route_crowd_score(self, route: Dict) -> int:
        """Calculate crowd score for a Google Maps route"""
        # Decode polyline and check for crowded locations
        # This is a simplified implementation
        return 2  # Medium crowd score as placeholder
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate haversine distance between two points"""
        R = 6371000  # Earth radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
