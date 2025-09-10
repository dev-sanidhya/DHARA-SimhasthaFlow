"""
Display emergency incidents from the database
"""
import sqlite3
import pandas as pd
from datetime import datetime

def show_emergency_data():
    """Display all emergency incidents from the database"""
    
    # Connect to the database
    conn = sqlite3.connect('simhastha_flow.db')
    
    # Query emergency data
    query = """
    SELECT 
        type,
        description,
        severity,
        status,
        location_lat,
        location_lng,
        created_at,
        resolved_at
    FROM emergencies 
    ORDER BY created_at DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"\n🚨 EMERGENCY INCIDENTS DATABASE - UJJAIN MAHAKUMBH")
    print(f"=" * 80)
    print(f"Total Emergency Incidents: {len(df)}")
    print(f"=" * 80)
    
    # Summary by type
    print("\n📊 SUMMARY BY TYPE:")
    type_counts = df['type'].value_counts()
    for emergency_type, count in type_counts.items():
        print(f"  {emergency_type.upper()}: {count} incidents")
    
    # Summary by severity
    print("\n⚠️  SUMMARY BY SEVERITY:")
    severity_counts = df['severity'].value_counts()
    for severity, count in severity_counts.items():
        print(f"  {severity.upper()}: {count} incidents")
    
    # Summary by status
    print("\n📋 SUMMARY BY STATUS:")
    status_counts = df['status'].value_counts()
    for status, count in status_counts.items():
        print(f"  {status.upper()}: {count} incidents")
    
    print(f"\n📝 RECENT INCIDENTS (Last 10):")
    print("-" * 80)
    
    # Show recent incidents
    for i, row in df.head(10).iterrows():
        print(f"\n{i+1}. TYPE: {row['type'].upper()}")
        print(f"   SEVERITY: {row['severity'].upper()} | STATUS: {row['status'].upper()}")
        print(f"   LOCATION: ({row['location_lat']:.4f}, {row['location_lng']:.4f})")
        print(f"   TIME: {row['created_at']}")
        print(f"   DESCRIPTION: {row['description']}")
        if row['resolved_at']:
            print(f"   RESOLVED: {row['resolved_at']}")
    
    # Active incidents
    active_incidents = df[df['status'] == 'active']
    if len(active_incidents) > 0:
        print(f"\n🔥 ACTIVE INCIDENTS ({len(active_incidents)}):")
        print("-" * 50)
        for i, row in active_incidents.iterrows():
            print(f"• {row['type'].upper()} - {row['severity'].upper()}")
            print(f"  {row['description']}")
            print()
    
    # Critical incidents
    critical_incidents = df[df['severity'] == 'critical']
    if len(critical_incidents) > 0:
        print(f"\n🚨 CRITICAL INCIDENTS ({len(critical_incidents)}):")
        print("-" * 50)
        for i, row in critical_incidents.iterrows():
            print(f"• {row['type'].upper()} - {row['status'].upper()}")
            print(f"  {row['description']}")
            print(f"  Time: {row['created_at']}")
            print()

if __name__ == "__main__":
    try:
        show_emergency_data()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the database exists and the server has been started at least once.")
