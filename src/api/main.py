from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
from typing import List, Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PharmaTelemetry API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': os.getenv('POSTGRES_DB', 'pharmadb'),
    'user': os.getenv('POSTGRES_USER', 'pharmauser'),
    'password': os.getenv('POSTGRES_PASSWORD', 'pharmapass')
}

# Pydantic models for API responses
class TopProduct(BaseModel):
    product_name: str
    mention_count: int
    channels: str  # Changed from List[str] to str since we're using STRING_AGG

class ChannelActivity(BaseModel):
    date: str
    message_count: int
    image_count: int
    avg_message_length: float

class MessageSearch(BaseModel):
    message_id: int
    channel_name: str
    message_text: str
    date: str
    has_image: bool

class ImageDetection(BaseModel):
    message_id: int
    detected_object: str
    confidence: float
    image_path: str

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.get("/")
async def root():
    return {"message": "PharmaTelemetry API - Ethiopian Medical Business Analytics"}

@app.get("/api/reports/top-products", response_model=List[TopProduct])
async def get_top_products(limit: int = Query(10, description="Number of top products to return")):
    """Get the most frequently mentioned medical products across all channels."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Simple keyword-based product detection
        cur.execute("""
            SELECT 
                'paracetamol' as product_name,
                COUNT(*) as mention_count,
                STRING_AGG(DISTINCT c.channel_name, ', ') as channels
            FROM analytics.fct_messages fm
            JOIN analytics.dim_channels c ON fm.channel_id = c.channel_id
            WHERE LOWER(fm.message_text) LIKE '%paracetamol%'
            GROUP BY product_name
            UNION ALL
            SELECT 
                'amoxicillin' as product_name,
                COUNT(*) as mention_count,
                STRING_AGG(DISTINCT c.channel_name, ', ') as channels
            FROM analytics.fct_messages fm
            JOIN analytics.dim_channels c ON fm.channel_id = c.channel_id
            WHERE LOWER(fm.message_text) LIKE '%amoxicillin%'
            GROUP BY product_name
            UNION ALL
            SELECT 
                'vitamin' as product_name,
                COUNT(*) as mention_count,
                STRING_AGG(DISTINCT c.channel_name, ', ') as channels
            FROM analytics.fct_messages fm
            JOIN analytics.dim_channels c ON fm.channel_id = c.channel_id
            WHERE LOWER(fm.message_text) LIKE '%vitamin%'
            GROUP BY product_name
            ORDER BY mention_count DESC
            LIMIT %s
        """, (limit,))
        
        results = cur.fetchall()
        return [TopProduct(**row) for row in results]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()

@app.get("/api/channels/{channel_name}/activity", response_model=List[ChannelActivity])
async def get_channel_activity(channel_name: str):
    """Get posting activity for a specific channel."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute("""
            SELECT 
                d.date_key::text as date,
                COUNT(*) as message_count,
                COUNT(CASE WHEN fm.has_image THEN 1 END) as image_count,
                AVG(fm.message_length) as avg_message_length
            FROM analytics.fct_messages fm
            JOIN analytics.dim_channels c ON fm.channel_id = c.channel_id
            JOIN analytics.dim_dates d ON fm.date_key = d.date_key
            WHERE c.channel_name = %s
            GROUP BY d.date_key
            ORDER BY d.date_key DESC
        """, (channel_name,))
        
        results = cur.fetchall()
        return [ChannelActivity(**row) for row in results]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()

@app.get("/api/search/messages", response_model=List[MessageSearch])
async def search_messages(query: str = Query(..., description="Search term")):
    """Search for messages containing a specific keyword."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute("""
            SELECT 
                fm.message_id,
                c.channel_name,
                fm.message_text,
                fm.date_key::text as date,
                fm.has_image
            FROM analytics.fct_messages fm
            JOIN analytics.dim_channels c ON fm.channel_id = c.channel_id
            WHERE LOWER(fm.message_text) LIKE %s
            ORDER BY fm.message_id DESC
            LIMIT 50
        """, (f'%{query.lower()}%',))
        
        results = cur.fetchall()
        return [MessageSearch(**row) for row in results]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()

@app.get("/api/reports/visual-content", response_model=List[ImageDetection])
async def get_visual_content(limit: int = Query(20, description="Number of detections to return")):
    """Get YOLO object detection results for visual content analysis."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute("""
            SELECT 
                fid.message_id,
                fid.detected_object_class as detected_object,
                fid.confidence_score as confidence,
                fid.image_path
            FROM analytics.fct_image_detections fid
            ORDER BY fid.confidence_score DESC
            LIMIT %s
        """, (limit,))
        
        results = cur.fetchall()
        return [ImageDetection(**row) for row in results]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001) 