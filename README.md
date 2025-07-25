# PharmaTelemetry

End-to-end data pipeline for extracting, transforming, and analyzing Telegram data about Ethiopian medical businesses.

## Features
- Telegram data scraping (messages, images)
- Data lake storage (JSON)
- PostgreSQL data warehouse
- dbt for transformation
- YOLOv8 for image enrichment
- FastAPI for analytics API
- Orchestrated with Dagster

## Project Structure
```
PharmaTelemetry/
  data/
    raw/
      telegram_messages/
  src/
    scrape_telegram.py
  requirements.txt
  Dockerfile
  docker-compose.yml
  .env (not committed)
  .gitignore
  README.md
```

## Setup
1. **Clone the repo**
2. **Create a `.env` file** with your secrets:
   ```
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   TELEGRAM_SESSION=pharmatelemetry
   POSTGRES_USER=pharmauser
   POSTGRES_PASSWORD=pharmapass
   POSTGRES_DB=pharmadb
   ```
3. **Build and run with Docker Compose:**
   ```sh
   docker-compose up --build
   ```

## Notes
- Raw data is stored in `data/raw/telegram_messages/YYYY-MM-DD/channel_name.json`.
- PostgreSQL is exposed on port 5432.
- Add more channels in `src/scrape_telegram.py` as needed.

## License
MIT