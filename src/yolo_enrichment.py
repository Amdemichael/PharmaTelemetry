import os
import glob
import psycopg2
from loguru import logger
from ultralytics import YOLO
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': os.getenv('POSTGRES_DB', 'pharmadb'),
    'user': os.getenv('POSTGRES_USER', 'pharmauser'),
    'password': os.getenv('POSTGRES_PASSWORD', 'pharmapass')
}

def create_image_detections_table():
    """Create raw table for storing YOLO detection results."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Create raw schema if it doesn't exist
    cur.execute("CREATE SCHEMA IF NOT EXISTS raw")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw.image_detections (
            id SERIAL PRIMARY KEY,
            message_id VARCHAR(50),
            image_path VARCHAR(500),
            detected_object_class VARCHAR(100),
            confidence_score DECIMAL(5,4),
            bbox_x1 DECIMAL(10,4),
            bbox_y1 DECIMAL(10,4),
            bbox_x2 DECIMAL(10,4),
            bbox_y2 DECIMAL(10,4),
            channel_name VARCHAR(100),
            message_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    logger.info("Raw image detections table created successfully.")

def get_message_id_from_image_path(image_path):
    """Extract message ID from image path to link with fact table."""
    # Path format: data/raw/telegram_messages/YYYY-MM-DD/channel_images/message_id.jpg
    filename = os.path.basename(image_path)
    message_id = filename.replace('.jpg', '')
    return message_id

def extract_channel_and_date_from_path(image_path):
    """Extract channel name and date from image path."""
    # Path format: data/raw/telegram_messages/YYYY-MM-DD/channel_images/message_id.jpg
    parts = image_path.split(os.sep)
    if len(parts) >= 4:
        date_str = parts[-3]  # YYYY-MM-DD
        channel_name = parts[-2].replace('_images', '')
        return channel_name, date_str
    return None, None

def process_images_with_yolo():
    """Process all scraped images with YOLO and store results in raw table."""
    # First, ensure the table exists
    create_image_detections_table()
    
    # Load pre-trained YOLO model
    model = YOLO('yolov8n.pt')  # Use nano model for speed
    
    # Find all image directories
    data_dir = 'data/raw/telegram_messages'
    image_dirs = glob.glob(f'{data_dir}/**/*_images', recursive=True)
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    total_processed = 0
    
    for img_dir in image_dirs:
        image_files = glob.glob(f'{img_dir}/*.jpg')
        
        for image_path in image_files:
            try:
                # Run YOLO detection
                results = model(image_path)
                
                # Extract metadata from path
                message_id = get_message_id_from_image_path(image_path)
                channel_name, date_str = extract_channel_and_date_from_path(image_path)
                
                # Process results
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            # Get detection info
                            class_id = int(box.cls[0])
                            class_name = model.names[class_id]
                            confidence = float(box.conf[0])
                            bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                            
                            # Insert detection result into raw table
                            cur.execute("""
                                INSERT INTO raw.image_detections 
                                (message_id, image_path, detected_object_class, confidence_score, 
                                 bbox_x1, bbox_y1, bbox_x2, bbox_y2, channel_name, message_date)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, (message_id, image_path, class_name, confidence, 
                                  bbox[0], bbox[1], bbox[2], bbox[3], channel_name, date_str))
                
                total_processed += 1
                logger.info(f"Processed {image_path} image {total_processed}/{len(image_files)}")
                
            except Exception as e:
                logger.error(f"Error processing {image_path}: {e}")
                # Rollback the transaction on error to prevent "current transaction is aborted"
                conn.rollback()
                continue
    
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"YOLO processing completed. Total images processed: {total_processed}")

if __name__ == '__main__':
    create_image_detections_table()
    process_images_with_yolo() 