"""
WebSocket implementation for real-time crowd updates
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
import asyncio
import json
import logging
from datetime import datetime
import random

from app.database.database import get_db_session
from app.models.database_models import Zone as DBZone, CrowdData as DBCrowdData
from app.models.schemas import CrowdUpdate, WebSocketMessage, CrowdLevel

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.simulation_task = None
        self.is_simulation_running = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connection established. Total connections: {len(self.active_connections)}")
        
        # Start simulation if this is the first connection
        if len(self.active_connections) == 1 and not self.is_simulation_running:
            self.simulation_task = asyncio.create_task(self.run_crowd_simulation())

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket connection closed. Total connections: {len(self.active_connections)}")
        
        # Stop simulation if no connections remain
        if len(self.active_connections) == 0 and self.simulation_task:
            self.simulation_task.cancel()
            self.is_simulation_running = False

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: dict):
        if self.active_connections:
            message_str = json.dumps(message, default=str)
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    logger.error(f"Error broadcasting to connection: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.disconnect(conn)

    async def run_crowd_simulation(self):
        """Run real-time crowd simulation"""
        self.is_simulation_running = True
        logger.info("Starting crowd simulation")
        
        try:
            while self.is_simulation_running and self.active_connections:
                # Generate crowd updates
                updates = await self.generate_crowd_updates()
                
                if updates:
                    # Broadcast updates to all connected clients
                    message = WebSocketMessage(
                        type="crowd_update",
                        data={"updates": [update.dict() for update in updates]},
                        timestamp=datetime.utcnow()
                    )
                    
                    await self.broadcast(message.dict())
                
                # Wait before next update (30 seconds)
                await asyncio.sleep(30)
                
        except asyncio.CancelledError:
            logger.info("Crowd simulation cancelled")
        except Exception as e:
            logger.error(f"Error in crowd simulation: {e}")
        finally:
            self.is_simulation_running = False

    async def generate_crowd_updates(self) -> List[CrowdUpdate]:
        """Generate realistic crowd updates"""
        updates = []
        db = get_db_session()
        
        try:
            # Get all zones
            zones = db.query(DBZone).all()
            
            for zone in zones:
                # Get previous occupancy
                previous_crowd = db.query(DBCrowdData).filter(
                    DBCrowdData.zone_id == zone.id
                ).order_by(DBCrowdData.timestamp.desc()).first()
                
                previous_occupancy = previous_crowd.occupancy if previous_crowd else zone.current_occupancy
                
                # Simulate crowd changes based on time and zone type
                new_occupancy = self.simulate_crowd_change(zone, previous_occupancy)
                
                # Determine crowd level
                occupancy_percentage = (new_occupancy / zone.capacity) * 100 if zone.capacity > 0 else 0
                
                if occupancy_percentage >= 90:
                    crowd_level = CrowdLevel.CRITICAL
                elif occupancy_percentage >= 70:
                    crowd_level = CrowdLevel.HIGH
                elif occupancy_percentage >= 40:
                    crowd_level = CrowdLevel.MEDIUM
                else:
                    crowd_level = CrowdLevel.LOW
                
                # Calculate change from previous
                change_from_previous = new_occupancy - previous_occupancy
                
                # Create crowd data record
                crowd_data = DBCrowdData(
                    zone_id=zone.id,
                    occupancy=new_occupancy,
                    density_per_sqm=new_occupancy / max(zone.capacity * 0.1, 1),
                    crowd_level=crowd_level.value,
                    timestamp=datetime.utcnow()
                )
                db.add(crowd_data)
                
                # Update zone current occupancy
                zone.current_occupancy = new_occupancy
                
                # Create update object
                update = CrowdUpdate(
                    zone_id=zone.id,
                    zone_name=zone.name,
                    occupancy=new_occupancy,
                    capacity=zone.capacity,
                    crowd_level=crowd_level,
                    timestamp=datetime.utcnow(),
                    change_from_previous=change_from_previous
                )
                
                updates.append(update)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error generating crowd updates: {e}")
            db.rollback()
        finally:
            db.close()
        
        return updates

    def simulate_crowd_change(self, zone: DBZone, current_occupancy: int) -> int:
        """Simulate realistic crowd changes based on time and zone type"""
        now = datetime.utcnow()
        hour = now.hour
        
        # Base change factor
        change_factor = 0
        
        # Time-based patterns
        if zone.type == "temple":
            # Peak hours: 5-9 AM, 5-8 PM
            if 5 <= hour <= 9 or 17 <= hour <= 20:
                change_factor = random.uniform(0.02, 0.08)  # Increase
            elif 21 <= hour <= 23 or 0 <= hour <= 4:
                change_factor = random.uniform(-0.05, -0.02)  # Decrease
            else:
                change_factor = random.uniform(-0.02, 0.02)  # Stable
                
        elif zone.type == "ghat":
            # Peak hours: 5-8 AM, 6-8 PM
            if 5 <= hour <= 8 or 18 <= hour <= 20:
                change_factor = random.uniform(0.03, 0.10)  # Increase
            elif 22 <= hour <= 23 or 0 <= hour <= 4:
                change_factor = random.uniform(-0.08, -0.03)  # Decrease
            else:
                change_factor = random.uniform(-0.03, 0.03)  # Stable
                
        elif zone.type == "parking":
            # Peak during temple/ghat peak hours
            if 6 <= hour <= 10 or 16 <= hour <= 21:
                change_factor = random.uniform(0.01, 0.05)  # Increase
            else:
                change_factor = random.uniform(-0.03, 0.01)  # Decrease
                
        elif zone.type == "food":
            # Peak during meal times
            if 7 <= hour <= 9 or 12 <= hour <= 14 or 19 <= hour <= 21:
                change_factor = random.uniform(0.02, 0.06)  # Increase
            else:
                change_factor = random.uniform(-0.04, 0.02)  # Variable
                
        else:
            # Other zones - general pattern
            change_factor = random.uniform(-0.03, 0.03)
        
        # Calculate new occupancy
        change = int(current_occupancy * change_factor)
        new_occupancy = current_occupancy + change
        
        # Add some randomness
        random_change = random.randint(-20, 20)
        new_occupancy += random_change
        
        # Ensure occupancy stays within bounds
        new_occupancy = max(0, min(new_occupancy, zone.capacity))
        
        return new_occupancy

# Global connection manager instance
manager = ConnectionManager()

def setup_websocket_routes(app):
    """Setup WebSocket routes"""
    
    @app.websocket("/ws/crowd-updates")
    async def websocket_crowd_updates(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                # Keep connection alive and listen for client messages
                data = await websocket.receive_text()
                
                # Handle client messages (ping, requests, etc.)
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await manager.send_personal_message(
                            {"type": "pong", "timestamp": datetime.utcnow()},
                            websocket
                        )
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received: {data}")
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            manager.disconnect(websocket)

    @app.websocket("/ws/emergency-alerts")
    async def websocket_emergency_alerts(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                # This would handle emergency alerts in real implementation
                await asyncio.sleep(60)  # Keep connection alive
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"Emergency WebSocket error: {e}")

    logger.info("WebSocket routes configured")
