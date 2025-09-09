#!/usr/bin/env python3
"""
DHARA Setup Script
Sets up the development environment and database for the FastAPI backend
"""

import asyncio
import os
import sys
from pathlib import Path
import subprocess
import shutil

async def check_requirements():
    """Check if required software is installed"""
    print("🔍 Checking system requirements...")
    
    requirements = {
        "python": ["python", "--version"],
        "postgresql": ["psql", "--version"],
        "redis": ["redis-cli", "--version"]
    }
    
    missing = []
    for name, cmd in requirements.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {name}: {result.stdout.strip()}")
            else:
                missing.append(name)
        except FileNotFoundError:
            missing.append(name)
    
    if missing:
        print(f"❌ Missing requirements: {', '.join(missing)}")
        print("\nPlease install:")
        if "postgresql" in missing:
            print("- PostgreSQL with PostGIS extension")
        if "redis" in missing:
            print("- Redis server")
        return False
    
    return True

def create_env_file():
    """Create .env file from .env.example"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        return
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from .env.example")
        print("🔧 Please edit .env file with your actual configuration:")
        print("   - Database credentials")
        print("   - API keys (OpenWeatherMap, Google Maps)")
        print("   - Redis configuration")
    else:
        print("❌ .env.example not found")

def install_python_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    requirements_file = Path("requirements-fastapi.txt")
    if requirements_file.exists():
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            print("✅ Python dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Python dependencies")
            return False
    else:
        print("❌ requirements-fastapi.txt not found")
        return False
    
    return True

async def setup_database():
    """Setup PostgreSQL database"""
    print("🗄️  Setting up PostgreSQL database...")
    
    # Read database config from .env
    db_name = "dhara_db"
    db_user = "username"  # Default from .env.example
    
    # Create database (assuming PostgreSQL is running)
    commands = [
        f"createdb {db_name}",
        f"psql -d {db_name} -c 'CREATE EXTENSION IF NOT EXISTS postgis;'"
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"✅ Executed: {cmd}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Command failed (may already exist): {cmd}")
    
    print("✅ Database setup completed")

def create_docker_compose():
    """Create docker-compose.yml for local development"""
    docker_compose_content = """version: '3.8'

services:
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: dhara_db
      POSTGRES_USER: username
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U username -d dhara_db"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose_content)
    
    print("✅ Created docker-compose.yml for local development")

def create_run_script():
    """Create run script for development"""
    run_script_content = """#!/usr/bin/env python3
\"\"\"
DHARA Development Server
Starts the FastAPI development server
\"\"\"

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("❌ .env file not found. Please run setup.py first.")
        sys.exit(1)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    )
"""
    
    with open("run_dev.py", "w") as f:
        f.write(run_script_content)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod("run_dev.py", 0o755)
    
    print("✅ Created run_dev.py development server script")

async def main():
    """Main setup function"""
    print("🚀 DHARA Backend Setup")
    print("=" * 50)
    
    # Check system requirements
    if not await check_requirements():
        print("\n❌ Setup failed. Please install missing requirements.")
        return
    
    # Create environment file
    create_env_file()
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("\n❌ Setup failed. Could not install Python dependencies.")
        return
    
    # Setup database
    await setup_database()
    
    # Create Docker Compose for easy development
    create_docker_compose()
    
    # Create run script
    create_run_script()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your actual API keys and database credentials")
    print("2. Start services: docker-compose up -d (if using Docker)")
    print("3. Run migrations: python -c 'from app.core.database import create_tables; create_tables()'")
    print("4. Start development server: python run_dev.py")
    print("\n🔗 API will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main())
