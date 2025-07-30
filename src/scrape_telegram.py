import os
import json
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import MessageMediaPhoto
from loguru import logger
import time
import asyncio

# Custom JSON encoder to handle datetime objects and bytes
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, bytes):
            # Clean bytes by removing null bytes and other problematic characters
            cleaned = obj.decode('utf-8', errors='ignore').replace('\x00', '').replace('\u0000', '')
            return cleaned
        return super().default(obj)

# Load environment variables
load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_NAME = os.getenv('TELEGRAM_SESSION', 'pharmatelemetry')

RAW_DATA_DIR = 'data/raw/telegram_messages'
SCRAPE_LOG_PATH = 'data/raw/scrape_log.json'

# Utility to load and update scrape log
def load_scrape_log():
    if os.path.exists(SCRAPE_LOG_PATH):
        with open(SCRAPE_LOG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def update_scrape_log(channel, date_str, status, error=None):
    log = load_scrape_log()
    if channel not in log:
        log[channel] = {}
    log[channel][date_str] = {'status': status, 'error': error, 'timestamp': datetime.now().isoformat()}
    with open(SCRAPE_LOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)

def clean_message_data(msg_dict):
    """Clean message data to remove problematic characters"""
    def clean_value(value):
        if isinstance(value, str):
            # Remove null bytes and other problematic characters
            return value.replace('\x00', '').replace('\u0000', '').replace('\u0001', '').replace('\u0002', '')
        elif isinstance(value, dict):
            return {k: clean_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [clean_value(v) for v in value]
        else:
            return value
    return clean_value(msg_dict)

async def scrape_channel(client, channel_url, date_str=None, limit=100, max_retries=3):
    channel_name = channel_url.split('/')[-1]
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    out_dir = os.path.join(RAW_DATA_DIR, date_str)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'{channel_name}.json')
    images_dir = os.path.join(out_dir, f'{channel_name}_images')
    os.makedirs(images_dir, exist_ok=True)

    # Incremental scraping: skip if already scraped
    if os.path.exists(out_path):
        logger.info(f"Skipping {channel_name} for {date_str}: already scraped.")
        update_scrape_log(channel_name, date_str, status='skipped')
        # Load existing data
        try:
            with open(out_path, 'r', encoding='utf-8') as f:
                messages_data = json.load(f)
            return {
                'messages': messages_data,
                'images': [f for f in os.listdir(images_dir) if f.endswith('.jpg')]
            }
        except Exception as e:
            logger.error(f"Error loading existing data for {channel_name}: {e}")
            return None

    messages_data = []
    downloaded_images = []
    attempt = 0
    while attempt < max_retries:
        try:
            async for message in client.iter_messages(channel_url, limit=limit):
                msg_dict = message.to_dict()
                # Clean the message data
                msg_dict = clean_message_data(msg_dict)
                # Download images if present
                if message.media and isinstance(message.media, MessageMediaPhoto):
                    image_path = os.path.join(images_dir, f'{message.id}.jpg')
                    try:
                        await client.download_media(message, file=image_path)
                        msg_dict['downloaded_image'] = image_path
                        downloaded_images.append(f'{message.id}.jpg')
                    except Exception as e:
                        logger.error(f"Failed to download image for message {message.id}: {e}")
                messages_data.append(msg_dict)
            # Save messages as JSON
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(messages_data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
            logger.info(f"Saved {len(messages_data)} messages from {channel_name} to {out_path}")
            update_scrape_log(channel_name, date_str, status='success')
            return {
                'messages': messages_data,
                'images': downloaded_images
            }
        except Exception as e:
            attempt += 1
            wait_time = 2 ** attempt
            logger.error(f"Error scraping {channel_url} (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Max retries reached for {channel_url}. Giving up.")
                update_scrape_log(channel_name, date_str, status='error', error=str(e))
                return None

async def scrape_telegram_channels(channels, date_str=None, limit=100):
    results = {}
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        try:
            await client.start()
        except SessionPasswordNeededError:
            logger.error("2FA is enabled. Please disable it or handle password input.")
            return results
        
        for channel_url in channels:
            logger.info(f"Scraping channel: {channel_url}")
            channel_name = channel_url.split('/')[-1]
            result = await scrape_channel(client, channel_url, date_str=date_str, limit=limit)
            if result:
                results[channel_name] = result
    
    return results

# CLI entrypoint
if __name__ == '__main__':
    import asyncio
    CHANNELS = [
        'https://t.me/lobelia4cosmetics',
        'https://t.me/tikvahpharma',
        # Add more channels as needed
    ]
    asyncio.run(scrape_telegram_channels(CHANNELS)) 