"""
Test script for DHARA FastAPI backend
Tests core functionality without requiring external dependencies
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        # Test core imports
        print("  📦 Testing core imports...")
        from app.core.config import settings
        print(f"    ✅ Config loaded - Ujjain coordinates: {settings.UJJAIN_LAT}, {settings.UJJAIN_LON}")
        
        # Test database models (without connecting)
        print("  📦 Testing database models...")
        from app.core.database import Base, User, Location, WeatherData
        print("    ✅ Database models imported")
        
        # Test services
        print("  📦 Testing services...")
        from app.services.websocket_manager import WebSocketManager
        print("    ✅ WebSocket manager imported")
        
        # Test API schemas
        print("  📦 Testing schemas...")
        from app.schemas.responses import LocationResponse, WeatherResponse
        print("    ✅ Response schemas imported")
        
        print("✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_configuration():
    """Test configuration settings"""
    print("🔧 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        # Test required settings
        required_settings = [
            'DATABASE_URL', 'REDIS_URL', 'SECRET_KEY', 
            'UJJAIN_LAT', 'UJJAIN_LON', 'OSM_API_URL'
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not hasattr(settings, setting):
                missing_settings.append(setting)
        
        if missing_settings:
            print(f"❌ Missing settings: {missing_settings}")
            return False
        
        # Test Ujjain coordinates
        if not (23.0 <= settings.UJJAIN_LAT <= 24.0):
            print(f"❌ Invalid Ujjain latitude: {settings.UJJAIN_LAT}")
            return False
        
        if not (75.0 <= settings.UJJAIN_LON <= 76.0):
            print(f"❌ Invalid Ujjain longitude: {settings.UJJAIN_LON}")
            return False
        
        print("✅ Configuration is valid!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_websocket_manager():
    """Test WebSocket manager functionality"""
    print("🔌 Testing WebSocket manager...")
    
    try:
        from app.services.websocket_manager import WebSocketManager
        
        manager = WebSocketManager()
        
        # Test initial state
        if len(manager.active_connections) != 0:
            print("❌ WebSocket manager should start with no connections")
            return False
        
        print("✅ WebSocket manager initialized correctly!")
        return True
        
    except Exception as e:
        print(f"❌ WebSocket manager error: {e}")
        return False

def test_database_models():
    """Test database model definitions"""
    print("🗄️  Testing database models...")
    
    try:
        from app.core.database import (
            User, Location, Road, WeatherData, 
            CrowdData, Event, Route
        )
        
        # Test model attributes
        models_to_test = {
            'User': User,
            'Location': Location,
            'Road': Road,
            'WeatherData': WeatherData,
            'CrowdData': CrowdData,
            'Event': Event,
            'Route': Route
        }
        
        for name, model in models_to_test.items():
            if not hasattr(model, '__tablename__'):
                print(f"❌ Model {name} missing __tablename__")
                return False
            
            print(f"    ✅ {name} model: {model.__tablename__}")
        
        print("✅ All database models are properly defined!")
        return True
        
    except Exception as e:
        print(f"❌ Database model error: {e}")
        return False

async def test_data_ingestion_structure():
    """Test data ingestion service structure"""
    print("📡 Testing data ingestion service...")
    
    try:
        from app.services.data_ingestion import DataIngestionService
        
        service = DataIngestionService()
        
        # Test that required methods exist
        required_methods = [
            'start_real_time_ingestion',
            'ingest_osm_data',
            'ingest_weather_data',
            'monitor_crowd_density'
        ]
        
        for method in required_methods:
            if not hasattr(service, method):
                print(f"❌ Missing method: {method}")
                return False
        
        print("✅ Data ingestion service structure is correct!")
        return True
        
    except Exception as e:
        print(f"❌ Data ingestion service error: {e}")
        return False

def test_routing_engine():
    """Test routing engine structure"""
    print("🗺️  Testing routing engine...")
    
    try:
        # This will fail without database session, but we can test structure
        from app.services.routing_engine import RoutingEngine
        
        # Test that class can be imported and has required methods
        required_methods = [
            'calculate_optimal_route',
            '_get_google_route',
            '_calculate_osm_route'
        ]
        
        for method in required_methods:
            if not hasattr(RoutingEngine, method):
                print(f"❌ Missing method: {method}")
                return False
        
        print("✅ Routing engine structure is correct!")
        return True
        
    except Exception as e:
        print(f"❌ Routing engine error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 DHARA Backend Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports()),
        ("Configuration", test_configuration()),
        ("WebSocket Manager", test_websocket_manager()),
        ("Database Models", test_database_models()),
        ("Data Ingestion", test_data_ingestion_structure()),
        ("Routing Engine", test_routing_engine())
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_coro in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend structure is ready.")
        print("\n📋 Next steps:")
        print("1. Run 'python setup.py' to configure environment")
        print("2. Install dependencies: pip install -r requirements-fastapi.txt")
        print("3. Setup PostgreSQL and Redis")
        print("4. Configure .env file with API keys")
        print("5. Start the server: python run_dev.py")
    else:
        print(f"❌ {total - passed} tests failed. Please fix the issues above.")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())
