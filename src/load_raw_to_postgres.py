import os
import json
import glob
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': os.getenv('POSTGRES_DB', 'pharmadb'),
    'user': os.getenv('POSTGRES_USER', 'pharmauser'),
    'password': os.getenv('POSTGRES_PASSWORD', 'pharmapass')
}

def create_raw_schema():
    """Create raw schema and tables for storing raw data."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Create raw schema
    cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    
    # Create raw_telegram_messages table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw.telegram_messages (
            id SERIAL PRIMARY KEY,
            channel_name VARCHAR(255),
            date_scraped DATE,
            message_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    logger.info("Raw schema and tables created successfully.")

def load_raw_data():
    """Load raw JSON files into PostgreSQL."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Find all JSON files in the data lake
    data_dir = 'data/raw/telegram_messages'
    json_files = glob.glob(f'{data_dir}/**/*.json', recursive=True)
    
    for json_file in json_files:
        # Extract channel name and date from file path
        # Path format: data/raw/telegram_messages/YYYY-MM-DD/channel_name.json
        path_parts = json_file.split(os.sep)
        date_str = path_parts[-2]  # YYYY-MM-DD
        channel_name = path_parts[-1].replace('.json', '')
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            # Insert each message
            for message in messages:
                cur.execute("""
                    INSERT INTO raw.telegram_messages (channel_name, date_scraped, message_data)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (channel_name, date_str, json.dumps(message)))
            
            logger.info(f"Loaded {len(messages)} messages from {channel_name} for {date_str}")
            
        except Exception as e:
            logger.error(f"Error loading {json_file}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    logger.info("Raw data loading completed.")

if __name__ == '__main__':
    create_raw_schema()
    load_raw_data() 