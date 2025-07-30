from dagster import job, op, In, Out, Nothing, repository
import subprocess
import sys
import os
from loguru import logger

@op
def scrape_telegram_data(context) -> str:
    """Scrape data from Telegram channels."""
    context.log.info("Starting Telegram data scraping...")
    
    try:
        # Run the scraping script
        result = subprocess.run([
            sys.executable, "src/scrape_telegram.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            context.log.info("Telegram scraping completed successfully")
            return "scraping_completed"
        else:
            context.log.error(f"Scraping failed: {result.stderr}")
            raise Exception("Telegram scraping failed")
    
    except Exception as e:
        context.log.error(f"Error in scraping: {e}")
        raise

@op
def load_raw_to_postgres(context, scraping_result: str) -> str:
    """Load raw data from data lake to PostgreSQL."""
    context.log.info("Loading raw data to PostgreSQL...")
    
    try:
        # Run the loading script
        result = subprocess.run([
            sys.executable, "src/load_raw_to_postgres.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            context.log.info("Data loading completed successfully")
            return "loading_completed"
        else:
            context.log.error(f"Loading failed: {result.stderr}")
            raise Exception("Data loading failed")
    
    except Exception as e:
        context.log.error(f"Error in loading: {e}")
        raise

@op
def run_dbt_transformations(context, loading_result: str) -> str:
    """Run dbt transformations to create staging and mart models."""
    context.log.info("Running dbt transformations...")
    
    try:
        # Change to dbt project directory
        dbt_dir = "pharma_dbt"
        
        # Run dbt commands
        commands = [
            ["dbt", "debug"],
            ["dbt", "run"],
            ["dbt", "test"],
            ["dbt", "docs", "generate"]
        ]
        
        for cmd in commands:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=os.path.join(os.getcwd(), dbt_dir)
            )
            
            if result.returncode != 0:
                context.log.error(f"dbt command failed: {cmd}, Error: {result.stderr}")
                raise Exception(f"dbt command failed: {cmd}")
            else:
                context.log.info(f"dbt command completed: {cmd}")
        
        context.log.info("dbt transformations completed successfully")
        return "dbt_completed"
    
    except Exception as e:
        context.log.error(f"Error in dbt transformations: {e}")
        raise

@op
def run_yolo_enrichment(context, dbt_result: str) -> str:
    """Run YOLO object detection on images and enrich data."""
    context.log.info("Running YOLO enrichment...")
    
    try:
        # Run the YOLO enrichment script
        result = subprocess.run([
            sys.executable, "src/yolo_enrichment.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            context.log.info("YOLO enrichment completed successfully")
            return "yolo_completed"
        else:
            context.log.error(f"YOLO enrichment failed: {result.stderr}")
            raise Exception("YOLO enrichment failed")
    
    except Exception as e:
        context.log.error(f"Error in YOLO enrichment: {e}")
        raise

@op
def start_fastapi_server(context, yolo_result: str) -> str:
    """Start the FastAPI server for the analytical API."""
    context.log.info("Starting FastAPI server...")
    
    try:
        # Start the FastAPI server in background
        process = subprocess.Popen([
            sys.executable, "src/api/main.py"
        ], cwd=os.getcwd())
        
        context.log.info(f"FastAPI server started with PID: {process.pid}")
        return f"api_server_started_pid_{process.pid}"
    
    except Exception as e:
        context.log.error(f"Error starting FastAPI server: {e}")
        raise

@job
def pharma_telemetry_pipeline():
    """Complete data pipeline for PharmaTelemetry."""
    scraping_result = scrape_telegram_data()
    loading_result = load_raw_to_postgres(scraping_result)
    dbt_result = run_dbt_transformations(loading_result)
    yolo_result = run_yolo_enrichment(dbt_result)
    api_result = start_fastapi_server(yolo_result)
    
    # Don't return anything - just execute the pipeline
    return None

# Standalone test ops (no dependencies)
@op
def test_scraping_op(context) -> str:
    """Standalone scraping test op."""
    context.log.info("Testing scraping functionality...")
    return scrape_telegram_data(context)

@op
def test_loading_op(context) -> str:
    """Standalone loading test op."""
    context.log.info("Testing loading functionality...")
    # Create a dummy result for testing
    dummy_result = "test_scraping_completed"
    return load_raw_to_postgres(context, dummy_result)

@op
def test_dbt_op(context) -> str:
    """Standalone dbt test op."""
    context.log.info("Testing dbt functionality...")
    # Create a dummy result for testing
    dummy_result = "test_loading_completed"
    return run_dbt_transformations(context, dummy_result)

@op
def test_yolo_op(context) -> str:
    """Standalone YOLO test op."""
    context.log.info("Testing YOLO functionality...")
    # Create a dummy result for testing
    dummy_result = "test_dbt_completed"
    return run_yolo_enrichment(context, dummy_result)

# For testing individual ops
@job
def test_scraping():
    """Test job for scraping only."""
    test_scraping_op()

@job
def test_loading():
    """Test job for loading only."""
    test_loading_op()

@job
def test_dbt():
    """Test job for dbt only."""
    test_dbt_op()

@job
def test_yolo():
    """Test job for YOLO only."""
    test_yolo_op() 

@repository
def pharma_repo():
    return [
        pharma_telemetry_pipeline,
        test_dbt,
        test_loading,
        test_scraping,
        test_yolo,
    ]

# Add jobs property to repository for easier access
pharma_repo.jobs = [
    pharma_telemetry_pipeline,
    test_dbt,
    test_loading,
    test_scraping,
    test_yolo,
] 