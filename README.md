# PharmaTelemetry - End-to-End Data Pipeline

A complete data engineering pipeline for analyzing Ethiopian pharmaceutical businesses through Telegram channel data.

## 🚀 Status: Production Ready

All components are fully functional and tested:
- ✅ **Data Scraping**: Telegram channels → JSON files
- ✅ **Data Storage**: PostgreSQL database with raw schema  
- ✅ **Data Transformation**: dbt models (staging → marts)
- ✅ **Data Enrichment**: YOLO object detection on images
- ✅ **Analytical API**: FastAPI endpoints for insights
- ✅ **Pipeline Orchestration**: Dagster UI for monitoring

## 📊 Current Data Volume

- **Messages**: 60 total (30 per channel)
- **Images**: 47 processed with YOLO
- **Detections**: 31 objects detected (bottles, persons, trucks, etc.)
- **Channels**: 2 (lobelia4cosmetics, tikvahpharma)
- **Tests**: All 18 dbt tests passing

## 🏗️ Architecture

```
Telegram Channels → Data Lake (JSON) → PostgreSQL (raw) → dbt (analytics) → FastAPI → Dagster
```

## 🛠️ Quick Start

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd PharmaTelemetry

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
POSTGRES_USER=pharmauser
POSTGRES_PASSWORD=pharmapass
POSTGRES_DB=pharmadb
```

### 3. Start Services

```bash
# Start PostgreSQL
docker-compose up -d

# Load data and run pipeline
python src/load_raw_to_postgres.py
cd pharma_dbt && dbt run && dbt test
python src/yolo_enrichment.py
```

### 4. Test Components

```bash
# Test FastAPI
python test_fastapi.py

# Test Dagster
dagster dev
```

## 📁 Project Structure

```
PharmaTelemetry/
├── src/                          # Source code
│   ├── api/                      # FastAPI application
│   ├── scrape_telegram.py        # Telegram scraping
│   ├── load_raw_to_postgres.py   # Data loading
│   ├── yolo_enrichment.py        # Object detection
│   └── dagster_pipeline.py       # Pipeline orchestration
├── pharma_dbt/                   # dbt project
│   ├── models/                   # Data models
│   │   ├── staging/             # Staging models
│   │   └── marts/              # Dimension & fact tables
│   └── tests/                   # Data tests
├── data/                         # Data lake
│   └── raw/                     # Raw JSON files
├── notebooks/                    # Jupyter notebooks
├── tests/                        # Unit tests
├── .github/                      # CI/CD workflows
├── docker-compose.yml           # Docker services
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## 🔧 Technical Stack

### Core Technologies
- **Python 3.11** - Main programming language
- **PostgreSQL 15** - Database (Docker)
- **dbt** - Data transformation
- **YOLOv8** - Object detection
- **FastAPI** - API framework
- **Dagster** - Pipeline orchestration

### Key Libraries
- `telethon` - Telegram API client
- `ultralytics` - YOLO object detection
- `psycopg2-binary` - PostgreSQL adapter
- `dbt-postgres` - dbt PostgreSQL adapter
- `fastapi` + `uvicorn` - API framework
- `dagster` + `dagster-webserver` - Orchestration

## 📈 Data Models

### Raw Layer
- `raw.telegram_messages` - Raw Telegram data
- `raw.image_detections` - YOLO detection results

### Staging Layer
- `stg_telegram_messages` - Cleaned message data
- `stg_image_detections` - Processed detection data

### Analytics Layer
- `dim_channels` - Channel dimension table
- `dim_dates` - Date dimension table
- `fct_messages` - Message fact table
- `fct_image_detections` - Image detection fact table

## 🔍 API Endpoints

### Health & Status
- `GET /api/health` - Service health check

### Analytics
- `GET /api/reports/top-products` - Product analysis
- `GET /api/channels/{channel_name}/activity` - Channel activity
- `GET /api/search/messages?query={term}` - Message search
- `GET /api/reports/visual-content` - Visual content analysis

## 🎯 Business Insights

### Available Analytics
- **Product Tracking**: Monitor pharmaceutical product mentions
- **Channel Activity**: Analyze engagement patterns
- **Visual Content**: Detect medical products in images
- **Search Capabilities**: Find specific messages and content

### Data Quality
- **Completeness**: All messages and images captured
- **Accuracy**: YOLO detections validated
- **Consistency**: dbt tests ensure data integrity
- **Timeliness**: Real-time processing capability

## 🚀 Deployment

### Development
```bash
# Run complete pipeline
python src/load_raw_to_postgres.py
cd pharma_dbt && dbt run
python src/yolo_enrichment.py
python test_fastapi.py
```

### Production
```bash
# Use Docker Compose
docker-compose up -d

# Run with Dagster
dagster dev
```

## 🧪 Testing

### Data Tests
```bash
cd pharma_dbt
dbt test  # All 18 tests passing
```

### API Tests
```bash
python test_fastapi.py
```

### Pipeline Tests
```bash
dagster dev  # Access UI at http://localhost:3000
```

## 📊 Monitoring

### Dagster UI
- **URL**: http://localhost:3000
- **Features**: Pipeline monitoring, job scheduling, error tracking

### FastAPI Docs
- **URL**: http://localhost:8001/docs
- **Features**: Interactive API documentation, endpoint testing

## 🔒 Security

- Environment variables for sensitive data
- Database credentials in Docker Compose
- API rate limiting and validation
- Input sanitization and validation

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🤝 Support

For questions or issues:
1. Check the documentation
2. Review the test results
3. Open an issue on GitHub

---

**PharmaTelemetry** - Transforming Telegram data into pharmaceutical business insights.