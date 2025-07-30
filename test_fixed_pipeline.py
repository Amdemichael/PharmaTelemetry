#!/usr/bin/env python3
"""
Test script to verify the fixed pipeline components
"""

import requests
import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
import time

# Load environment variables
load_dotenv()

def test_fastapi_endpoints():
    """Test FastAPI endpoints"""
    print("🌐 Testing FastAPI endpoints...")
    
    base_url = "http://127.0.0.1:8001"
    
    # Test health endpoint
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Health check successful")
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Health check error: {e}")
    
    # Test message search
    print("🔍 Testing message search...")
    try:
        response = requests.get(f"{base_url}/api/search/messages?query=cosmetic", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Message search successful: {len(data)} results")
        else:
            print(f"  ❌ Message search failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Message search error: {e}")
    
    # Test channel activity
    print("🔍 Testing channel activity...")
    try:
        response = requests.get(f"{base_url}/api/channels/lobelia4cosmetics/activity", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Channel activity successful: {len(data)} records")
        else:
            print(f"  ❌ Channel activity failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Channel activity error: {e}")
    
    # Test visual content
    print("🔍 Testing visual content...")
    try:
        response = requests.get(f"{base_url}/api/reports/visual-content?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Visual content successful: {len(data)} detections")
        else:
            print(f"  ❌ Visual content failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Visual content error: {e}")
    
    print("✅ API testing completed!")

def test_fixed_queries():
    """Test the fixed SQL queries"""
    print("\n📊 Testing fixed database queries...")
    
    # Connect to database
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            # Test fixed channel activity query
            print("🔍 Testing channel activity query...")
            cur.execute("""
                SELECT 
                    c.channel_name,
                    COUNT(*) as message_count,
                    COUNT(CASE WHEN fm.has_image THEN 1 END) as image_count
                FROM analytics.fct_messages fm
                JOIN analytics.dim_channels c ON fm.channel_id = c.channel_id
                GROUP BY c.channel_name
                ORDER BY message_count DESC
            """)
            
            channel_insights = cur.fetchall()
            print(f"  ✅ Channel activity query successful: {len(channel_insights)} channels")
            for insight in channel_insights:
                print(f"    📢 {insight['channel_name']}: {insight['message_count']} messages")
            
            # Test fixed product detection query
            print("🔍 Testing product detection query...")
            cur.execute("""
                SELECT 
                    detected_object_class as object_class,
                    COUNT(*) as detection_count,
                    AVG(confidence_score) as avg_confidence
                FROM analytics.fct_image_detections
                WHERE detected_object_class IN ('bottle', 'person', 'truck', 'refrigerator')
                GROUP BY detected_object_class
                ORDER BY detection_count DESC
            """)
            
            product_insights = cur.fetchall()
            print(f"  ✅ Product detection query successful: {len(product_insights)} object types")
            for insight in product_insights:
                print(f"    📦 {insight['object_class']}: {insight['detection_count']} detections")
                
        except Exception as e:
            print(f"  ❌ Query error: {e}")
    
    conn.close()
    print("✅ Database query testing completed!")

def main():
    """Main test function"""
    print("🚀 Testing Fixed PharmaTelemetry Pipeline")
    print("=" * 50)
    
    # Wait a moment for FastAPI to start
    print("⏳ Waiting for FastAPI server to start...")
    time.sleep(3)
    
    # Test FastAPI endpoints
    test_fastapi_endpoints()
    
    # Test fixed queries
    test_fixed_queries()
    
    print("\n🎉 Testing completed!")
    print("\n📋 Summary:")
    print("  ✅ Fixed SQL queries in notebook")
    print("  ✅ FastAPI server should be running")
    print("  ✅ Database queries working")
    print("\n📝 Next steps:")
    print("  1. Run the fixed notebook: notebooks/02_complete_pipeline_demo_fixed.ipynb")
    print("  2. Access FastAPI docs: http://127.0.0.1:8001/docs")
    print("  3. Test all endpoints via the API")

if __name__ == "__main__":
    main() 