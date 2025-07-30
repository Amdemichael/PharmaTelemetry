import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)

cur = conn.cursor()

# Check analytics.fct_messages columns
print("📊 Analytics fct_messages columns:")
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'analytics' 
    AND table_name = 'fct_messages' 
    ORDER BY ordinal_position
""")
columns = cur.fetchall()
for col in columns:
    print(f"  - {col[0]}")

# Check analytics.fct_image_detections columns
print("\n📊 Analytics fct_image_detections columns:")
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'analytics' 
    AND table_name = 'fct_image_detections' 
    ORDER BY ordinal_position
""")
columns = cur.fetchall()
for col in columns:
    print(f"  - {col[0]}")

conn.close()
print("\n✅ Schema check completed!") 