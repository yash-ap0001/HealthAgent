"""
API Client for communicating with the Spring Boot backend for nutrition data.
"""
import json
import logging
import requests
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutritionApiClient:
    """Client for interacting with the nutrition-related Spring Boot backend APIs."""
    
    def __init__(self, base_url=None, username=None, password=None, user_id=1):
        """
        Initialize the API client.
        
        Args:
            base_url (str): Base URL for the API endpoints
            username (str): Username for authentication
            password (str): Password for authentication
            user_id (int): User ID to use for API requests
        """
        self.base_url = base_url or "http://localhost:8080/api"
        self.username = username or "demo"
        self.password = password or "password"
        self.user_id = user_id
        self.token = None
        self.authenticated = False
    
    def authenticate(self):
        """
        Authenticate with the API and obtain a JWT token.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        try:
            url = f"{self.base_url}/auth/login"
            payload = {
                "username": self.username,
                "password": self.password
            }
            
            logger.info(f"Authenticating with Spring Boot API at {url}")
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.authenticated = True
                logger.info("Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def get_headers(self):
        """
        Get HTTP headers for authenticated requests.
        
        Returns:
            dict: Headers with Authorization token if authenticated
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
        return headers
    
    def get_nutrition_data(self, user_id=None, start_date=None, end_date=None):
        """
        Get nutrition data from the API.
        
        Args:
            user_id (int): ID of the user to get data for (defaults to self.user_id)
            start_date (str): Start date in ISO format (YYYY-MM-DD)
            end_date (str): End date in ISO format (YYYY-MM-DD)
            
        Returns:
            list: List of nutrition data records, or None if the request failed
        """
        try:
            user_id = user_id or self.user_id
            
            # Set default date range if not provided (last 30 days)
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date_obj = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=30)
                start_date = start_date_obj.strftime("%Y-%m-%d")
            
            url = f"{self.base_url}/nutrition-data"
            params = {
                "userId": user_id,
                "startDate": start_date,
                "endDate": end_date
            }
            
            logger.info(f"Getting nutrition data from {url} with params {params}")
            response = requests.get(url, params=params, headers=self.get_headers())
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Retrieved {len(data)} nutrition data records")
                return data
            else:
                logger.error(f"Failed to get nutrition data. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting nutrition data: {str(e)}")
            return None
    
    def save_nutrition_data(self, data):
        """
        Save nutrition data to the API.
        
        Args:
            data (dict): Nutrition data to save
            
        Returns:
            dict: Saved nutrition data record with ID, or None if the request failed
        """
        try:
            url = f"{self.base_url}/nutrition-data"
            
            # Ensure user_id is set if not provided in the data
            if "userId" not in data:
                data["userId"] = self.user_id
                
            logger.info(f"Saving nutrition data to {url}")
            response = requests.post(url, json=data, headers=self.get_headers())
            
            if response.status_code in [200, 201]:
                saved_data = response.json()
                logger.info(f"Successfully saved nutrition data with ID {saved_data.get('id')}")
                return saved_data
            else:
                logger.error(f"Failed to save nutrition data. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error saving nutrition data: {str(e)}")
            return None
    
    def get_nutrition_insights(self, user_id=None, category="nutrition"):
        """
        Get nutrition-related insights from the API.
        
        Args:
            user_id (int): ID of the user to get insights for (defaults to self.user_id)
            category (str): Category of insights (defaults to "nutrition")
            
        Returns:
            list: List of insights, or None if the request failed
        """
        try:
            user_id = user_id or self.user_id
            
            url = f"{self.base_url}/insights"
            params = {
                "userId": user_id,
                "category": category
            }
            
            logger.info(f"Getting nutrition insights from {url} with params {params}")
            response = requests.get(url, params=params, headers=self.get_headers())
            
            if response.status_code == 200:
                insights = response.json()
                logger.info(f"Retrieved {len(insights)} nutrition insights")
                return insights
            else:
                logger.error(f"Failed to get nutrition insights. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting nutrition insights: {str(e)}")
            return None
    
    def create_nutrition_insight(self, insight_data):
        """
        Create a new nutrition-related insight.
        
        Args:
            insight_data (dict): Insight data to save
            
        Returns:
            dict: Created insight with ID, or None if the request failed
        """
        try:
            url = f"{self.base_url}/insights"
            
            # Ensure user_id and category are set if not provided in the data
            if "userId" not in insight_data:
                insight_data["userId"] = self.user_id
            if "category" not in insight_data:
                insight_data["category"] = "nutrition"
                
            logger.info(f"Creating nutrition insight at {url}")
            response = requests.post(url, json=insight_data, headers=self.get_headers())
            
            if response.status_code in [200, 201]:
                created_insight = response.json()
                logger.info(f"Successfully created nutrition insight with ID {created_insight.get('id')}")
                return created_insight
            else:
                logger.error(f"Failed to create nutrition insight. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating nutrition insight: {str(e)}")
            return None