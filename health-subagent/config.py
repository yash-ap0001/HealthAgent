"""
Configuration module for the Health Sub-Agent.
"""
import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Config:
    """Configuration class for the Health Sub-Agent."""
    
    def __init__(self):
        # API Configuration
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.api_username = os.getenv("API_USERNAME")
        self.api_password = os.getenv("API_PASSWORD")
        
        # Processing Configuration
        self.processing_interval = int(os.getenv("PROCESSING_INTERVAL", "3600"))  # Default: 1 hour
        
        # Data Analysis Configuration
        self.lookback_days = int(os.getenv("LOOKBACK_DAYS", "30"))
        self.step_goal = int(os.getenv("STEP_GOAL", "10000"))
        self.sleep_goal_hours = float(os.getenv("SLEEP_GOAL_HOURS", "8.0"))
        self.heart_rate_rest_threshold = int(os.getenv("HEART_RATE_REST_THRESHOLD", "70"))
        
        # Insight Configuration
        self.min_data_points = int(os.getenv("MIN_DATA_POINTS", "5"))
        self.activity_threshold = float(os.getenv("ACTIVITY_THRESHOLD", "0.8"))  # 80% of goal
        self.sleep_threshold = float(os.getenv("SLEEP_THRESHOLD", "0.9"))  # 90% of goal
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that all required configuration values are present."""
        if not self.api_username or not self.api_password:
            raise ValueError("API_USERNAME and API_PASSWORD must be set in the environment or .env file")
