"""
API Client for communicating with the Health AI backend.
"""
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ApiClient:
    """Client for interacting with the Health AI backend API."""
    
    def __init__(self, config):
        """
        Initialize the API client.
        
        Args:
            config (Config): The application configuration.
        """
        self.config = config
        self.base_url = config.api_base_url
        self.token = None
    
    def authenticate(self):
        """
        Authenticate with the API and store the JWT token.
        
        Returns:
            str: The JWT token if authentication was successful, None otherwise.
        """
        try:
            url = f"{self.base_url}/api/auth/login"
            payload = {
                "email": self.config.api_username,
                "password": self.config.api_password
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["token"]
                return self.token
            else:
                logger.error(f"Authentication failed with status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return None
    
    def _get_headers(self):
        """
        Get the HTTP headers for API requests.
        
        Returns:
            dict: The headers including the Authorization token.
        """
        if not self.token:
            self.authenticate()
            
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def get_health_data(self, data_type=None, start_date=None, end_date=None):
        """
        Get health data from the API.
        
        Args:
            data_type (str, optional): The type of health data to retrieve.
            start_date (str, optional): The start date in ISO format.
            end_date (str, optional): The end date in ISO format.
            
        Returns:
            list: A list of health data points.
        """
        try:
            url = f"{self.base_url}/api/health/data"
            params = {}
            
            if data_type:
                params["dataType"] = data_type
            if start_date:
                params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date
                
            response = requests.get(url, headers=self._get_headers(), params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # Token may have expired, try to re-authenticate
                self.authenticate()
                return self.get_health_data(data_type, start_date, end_date)
            else:
                logger.error(f"Error getting health data: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Exception getting health data: {str(e)}")
            return []
    
    def save_health_data(self, data):
        """
        Save health data to the API.
        
        Args:
            data (dict): The health data to save.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            url = f"{self.base_url}/api/health/data"
            response = requests.post(url, headers=self._get_headers(), json=data)
            
            if response.status_code in (200, 201):
                return True
            elif response.status_code == 401:
                # Token may have expired, try to re-authenticate
                self.authenticate()
                return self.save_health_data(data)
            else:
                logger.error(f"Error saving health data: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Exception saving health data: {str(e)}")
            return False
    
    def create_insight(self, insight_data):
        """
        Create a new insight in the backend.
        
        Args:
            insight_data (dict): The insight data to save.
            
        Returns:
            dict: The created insight if successful, None otherwise.
        """
        try:
            url = f"{self.base_url}/api/insights"
            response = requests.post(url, headers=self._get_headers(), json=insight_data)
            
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 401:
                # Token may have expired, try to re-authenticate
                self.authenticate()
                return self.create_insight(insight_data)
            else:
                logger.error(f"Error creating insight: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Exception creating insight: {str(e)}")
            return None
    
    def get_insights(self, category=None):
        """
        Get insights from the API.
        
        Args:
            category (str, optional): The category of insights to retrieve.
            
        Returns:
            list: A list of insights.
        """
        try:
            url = f"{self.base_url}/api/insights"
            params = {}
            
            if category:
                params["category"] = category
                
            response = requests.get(url, headers=self._get_headers(), params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # Token may have expired, try to re-authenticate
                self.authenticate()
                return self.get_insights(category)
            else:
                logger.error(f"Error getting insights: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Exception getting insights: {str(e)}")
            return []
