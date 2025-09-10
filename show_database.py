"""
Script to display database contents for SimhasthaFlow system
"""

import sqlite3
import json
from datetime import datetime

def show_database_contents():
    """Display the contents of the SimhasthaFlow database"""
    db_path = "simhastha_flow.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("🏛️  SIMHASTHAFLOW DATABASE CONTENTS (UJJAIN MAHAKUMBH)")
        print("=" * 80)
        
        # Show users table
        print("\n👥 USERS:")
        print("-" * 40)
        cursor.execute("SELECT id, username, is_admin, created_at FROM users")
        users = cursor.fetchall()
        for user in users:
            admin_status = "Admin" if user[2] else "User"
            print(f"ID: {user[0][:8]}... | Username: {user[1]} | Role: {admin_status}")
        
        # Show zones table (Ujjain temples and facilities)
        print(f"\n🏛️  ZONES (Total: {len(cursor.execute('SELECT id FROM zones').fetchall())}):")
        print("-" * 60)
        cursor.execute("SELECT name, type, center_lat, center_lng, capacity, current_occupancy, description FROM zones")
        zones = cursor.fetchall()
        for zone in zones:
            occupancy_pct = (zone[5] / zone[4] * 100) if zone[4] > 0 else 0
            print(f"📍 {zone[0]}")
            print(f"   Type: {zone[1].title()} | Coords: ({zone[2]:.4f}, {zone[3]:.4f})")
            print(f"   Capacity: {zone[4]} | Current: {zone[5]} ({occupancy_pct:.1f}%)")
            print(f"   Description: {zone[6]}")
            print()
        
        # Show road network
        print("\n🛣️  ROAD NETWORK:")
        print("-" * 50)
        cursor.execute("SELECT name, road_type, length_km, width_meters, max_crowd_capacity FROM road_networks")
        roads = cursor.fetchall()
        for road in roads:
            print(f"🛣️  {road[0]} ({road[1]})")
            print(f"   Length: {road[2]}km | Width: {road[3]}m | Max Capacity: {road[4]} people")
        
        # Show recent crowd data
        print("\n👥 RECENT CROWD DATA:")
        print("-" * 50)
        cursor.execute("""
            SELECT z.name, cd.occupancy, cd.density_per_sqm, cd.crowd_level, cd.timestamp 
            FROM crowd_data cd 
            JOIN zones z ON cd.zone_id = z.id 
            ORDER BY cd.timestamp DESC 
            LIMIT 10
        """)
        crowd_data = cursor.fetchall()
        for crowd in crowd_data:
            timestamp = crowd[4][:19] if crowd[4] else "Unknown"
            print(f"📊 {crowd[0]}: {crowd[1]} people | Density: {crowd[2]:.1f}/sqm | Level: {crowd[3].upper()} | {timestamp}")
        
        # Show weather data
        print("\n🌤️  WEATHER DATA:")
        print("-" * 40)
        cursor.execute("SELECT temperature_celsius, humidity_percent, condition, timestamp FROM weather_data ORDER BY timestamp DESC LIMIT 5")
        weather_data = cursor.fetchall()
        for weather in weather_data:
            timestamp = weather[3][:19] if weather[3] else "Unknown"
            print(f"🌡️  {weather[0]}°C | Humidity: {weather[1]}% | {weather[2].title()} | {timestamp}")
        
        # Show emergency incidents
        print("\n🚨 EMERGENCY INCIDENTS:")
        print("-" * 50)
        cursor.execute("SELECT type, description, severity, status, location_lat, location_lng, created_at FROM emergencies ORDER BY created_at DESC")
        emergencies = cursor.fetchall()
        for emergency in emergencies:
            timestamp = emergency[6][:19] if emergency[6] else "Unknown"
            status_icon = "✅" if emergency[3] == "resolved" else "🔴"
            print(f"{status_icon} {emergency[0].upper()} ({emergency[2]}) - {emergency[3].upper()}")
            print(f"   Location: ({emergency[4]:.4f}, {emergency[5]:.4f})")
            print(f"   Description: {emergency[1]}")
            print(f"   Time: {timestamp}")
            print()
        
        # Database statistics
        print("\n📈 DATABASE STATISTICS:")
        print("-" * 30)
        
        # Count records in each table
        tables = ['users', 'zones', 'crowd_data', 'weather_data', 'emergencies', 'road_networks']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table.replace('_', ' ').title()}: {count} records")
            except:
                print(f"{table}: Table not found")
        
        # Show crowd levels distribution
        cursor.execute("SELECT crowd_level, COUNT(*) FROM crowd_data GROUP BY crowd_level")
        crowd_levels = cursor.fetchall()
        print(f"\nCrowd Level Distribution:")
        for level in crowd_levels:
            print(f"  {level[0].title()}: {level[1]} records")
        
        print("\n" + "=" * 80)
        print("✅ Database successfully loaded with Ujjain Mahakumbh data!")
        print("🌐 API Documentation: http://localhost:8000/docs")
        print("🔑 Default Login: admin / admin123")
        print("=" * 80)
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    show_database_contents()
