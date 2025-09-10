"""
FastAPI Backend for SimhasthaFlow/Dhara System
Main application entry point
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import logging

# Import routers
from app.routers import routes, weather, crowd, zones, emergency, auth
from app.database.database import init_db, get_db
from app.websocket.crowd_updates import setup_websocket_routes
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting SimhasthaFlow Backend...")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down SimhasthaFlow Backend...")

# Create FastAPI app
app = FastAPI(
    title="SimhasthaFlow API",
    description="Crowd management and navigation system for religious gatherings",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(routes.router, prefix="/api/v1", tags=["Routes"])
app.include_router(weather.router, prefix="/api/v1", tags=["Weather"])
app.include_router(crowd.router, prefix="/api/v1", tags=["Crowd Management"])
app.include_router(zones.router, prefix="/api/v1", tags=["Zone Management"])
app.include_router(emergency.router, prefix="/api/v1", tags=["Emergency"])

# Setup WebSocket routes
setup_websocket_routes(app)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SimhasthaFlow API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SimhasthaFlow API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
