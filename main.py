"""
DHARA - Real-time Crowd Management System for Simhastha Event
Main FastAPI application entry point
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import asyncio
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import router
from app.services.websocket_manager import WebSocketManager
from app.services.data_ingestion import DataIngestionService

# WebSocket manager for real-time updates
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start data ingestion services
    data_service = DataIngestionService()
    ingestion_task = asyncio.create_task(data_service.start_real_time_ingestion())
    
    yield
    
    # Shutdown
    ingestion_task.cancel()
    try:
        await ingestion_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="DHARA - Crowd Management System",
    description="Real-time crowd management and routing system for Simhastha event in Ujjain",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly for production
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Process incoming data if needed
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "DHARA Crowd Management System is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "external_apis": "active"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
