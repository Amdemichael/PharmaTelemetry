#!/usr/bin/env python3
"""
Test script to verify notebook imports and functionality
"""

import sys
from pathlib import Path
import asyncio
import nest_asyncio

# Add project root to path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

# Apply nest_asyncio for Jupyter compatibility
nest_asyncio.apply()

def test_imports():
    """Test all imports used in the notebook"""
    print("🔍 Testing notebook imports...")
    
    try:
        # Test basic imports
        import json
        import os
        from datetime import datetime, timedelta
        print("  ✅ Basic imports successful")
        
        # Test project module imports
        from src.scrape_telegram import scrape_telegram_channels
        print("  ✅ Telegram scraping module imported")
        
        from src.load_raw_to_postgres import load_raw_data
        print("  ✅ Data loading module imported")
        
        from src.yolo_enrichment import process_images_with_yolo
        print("  ✅ YOLO enrichment module imported")
        
        # Test database imports
        import psycopg2
        from psycopg2.extras import RealDictCursor
        print("  ✅ Database imports successful")
        
        # Test environment variables
        from dotenv import load_dotenv
        load_dotenv()
        print("  ✅ Environment variables loaded")
        
        # Test FastAPI import
        from src.api.main import app
        print("  ✅ FastAPI app imported")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        import psycopg2
        import os
        
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        print("  ✅ Database connection successful")
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False

def test_fixed_queries():
    """Test the fixed SQL queries"""
    print("\n🔍 Testing fixed SQL queries...")
    
    try:
        import psycopg2
        import os
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Test channel activity query
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
            
            results = cur.fetchall()
            print(f"  ✅ Channel activity query successful: {len(results)} channels")
            
            # Test product detection query
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
            
            results = cur.fetchall()
            print(f"  ✅ Product detection query successful: {len(results)} object types")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Query error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Notebook Functionality")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test database connection
    db_ok = test_database_connection()
    
    # Test fixed queries
    queries_ok = test_fixed_queries()
    
    print("\n📋 Test Results:")
    print(f"  {'✅' if imports_ok else '❌'} Imports")
    print(f"  {'✅' if db_ok else '❌'} Database connection")
    print(f"  {'✅' if queries_ok else '❌'} SQL queries")
    
    if imports_ok and db_ok and queries_ok:
        print("\n🎉 All tests passed! The notebook should work correctly.")
        print("\n📝 Next steps:")
        print("  1. Run the notebook: notebooks/complete_pipeline_demo.ipynb")
        print("  2. Start FastAPI: cd src/api && python -m uvicorn main:app --host 127.0.0.1 --port 8001")
        print("  3. Start Dagster: dagster dev")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 