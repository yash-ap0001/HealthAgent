#!/usr/bin/env python3
"""
Health Sub-Agent: Analyzes health data and generates insights.
"""
import logging
import time
from datetime import datetime, timedelta

from config import Config
from api_client import ApiClient
from processors.steps_processor import StepsProcessor
from processors.sleep_processor import SleepProcessor
from processors.heart_rate_processor import HeartRateProcessor
from insights_engine import InsightsEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def authenticate(api_client):
    """Authenticate with the backend API."""
    token = api_client.authenticate()
    if not token:
        logger.error("Authentication failed. Exiting.")
        return False
    logger.info("Authentication successful.")
    return True

def main():
    """Main function to run the health sub-agent."""
    logger.info("Starting Health Sub-Agent...")
    config = Config()
    api_client = ApiClient(config)
    
    # Authenticate with the backend
    if not authenticate(api_client):
        return
    
    # Initialize processors
    steps_processor = StepsProcessor(api_client)
    sleep_processor = SleepProcessor(api_client)
    heart_rate_processor = HeartRateProcessor(api_client)
    
    # Initialize insights engine
    insights_engine = InsightsEngine(api_client)
    
    while True:
        try:
            # Process health data
            logger.info("Processing steps data...")
            steps_processor.process()
            
            logger.info("Processing sleep data...")
            sleep_processor.process()
            
            logger.info("Processing heart rate data...")
            heart_rate_processor.process()
            
            # Generate insights
            logger.info("Generating insights...")
            insights_engine.generate_insights()
            
            # Wait for next cycle
            logger.info(f"Data processing cycle complete. Waiting for {config.processing_interval} seconds.")
            time.sleep(config.processing_interval)
            
        except Exception as e:
            logger.error(f"Error in processing cycle: {str(e)}")
            time.sleep(60)  # Wait a minute before trying again

if __name__ == "__main__":
    main()
