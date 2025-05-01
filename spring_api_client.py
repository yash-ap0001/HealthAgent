"""
Spring Boot API Client

This module provides integration with the Spring Boot backend APIs.
It handles authentication, health data retrieval, and insight management.
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SpringApiClient:
    """Client for interacting with the Spring Boot backend APIs."""
    
    def __init__(self, base_url=None, username=None, password=None):
        """
        Initialize the API client.
        
        Args:
            base_url (str): Base URL for the API endpoints
            username (str): Username for authentication
            password (str): Password for authentication
        """
        self.base_url = base_url or os.environ.get('SPRING_API_URL', 'http://localhost:8080/api')
        self.username = username or os.environ.get('SPRING_API_USERNAME', 'admin@example.com')
        self.password = password or os.environ.get('SPRING_API_PASSWORD', 'password123')
        self.token = None
        self.token_expiry = None
    
    def authenticate(self):
        """
        Authenticate with the API and obtain a JWT token.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        try:
            # Check if we already have a valid token
            if self.token and self.token_expiry and datetime.now() < self.token_expiry:
                logger.info("Using existing token - still valid")
                return True
            
            auth_url = f"{self.base_url}/auth/login"
            payload = {
                "email": self.username,
                "password": self.password
            }
            
            logger.info(f"Authenticating with {auth_url}")
            response = requests.post(auth_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                # Assuming token expires in 24 hours
                self.token_expiry = datetime.now() + timedelta(hours=24)
                logger.info("Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return False
    
    def get_headers(self):
        """
        Get HTTP headers for authenticated requests.
        
        Returns:
            dict: Headers with Authorization token if authenticated
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"
        
        return headers
    
    def get_health_data(self, user_id=None, data_type=None, start_date=None, end_date=None):
        """
        Get health data from the API.
        
        Args:
            user_id (int): ID of the user to get data for
            data_type (str): Type of health data (steps, sleep, heart_rate)
            start_date (str): Start date in ISO format (YYYY-MM-DD)
            end_date (str): End date in ISO format (YYYY-MM-DD)
            
        Returns:
            list: List of health data records, or None if the request failed
        """
        if not self.authenticate():
            return None
        
        try:
            url = f"{self.base_url}/health-data"
            params = {}
            
            if user_id:
                params['userId'] = user_id
            if data_type:
                params['dataType'] = data_type
            if start_date:
                params['startDate'] = start_date
            if end_date:
                params['endDate'] = end_date
            
            logger.info(f"Getting health data from {url} with params {params}")
            response = requests.get(url, headers=self.get_headers(), params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get health data: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting health data: {str(e)}")
            return None
    
    def save_health_data(self, data):
        """
        Save health data to the API.
        
        Args:
            data (dict): Health data to save
            
        Returns:
            dict: Saved health data record with ID, or None if the request failed
        """
        if not self.authenticate():
            return None
        
        try:
            url = f"{self.base_url}/health-data"
            
            logger.info(f"Saving health data to {url}")
            response = requests.post(url, headers=self.get_headers(), json=data)
            
            if response.status_code in (200, 201):
                return response.json()
            else:
                logger.error(f"Failed to save health data: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error saving health data: {str(e)}")
            return None
    
    def get_insights(self, user_id=None, category=None):
        """
        Get insights from the API.
        
        Args:
            user_id (int): ID of the user to get insights for
            category (str): Category of insights (activity, sleep, heart, general)
            
        Returns:
            list: List of insights, or None if the request failed
        """
        if not self.authenticate():
            return None
        
        try:
            url = f"{self.base_url}/insights"
            params = {}
            
            if user_id:
                params['userId'] = user_id
            if category:
                params['category'] = category
            
            logger.info(f"Getting insights from {url} with params {params}")
            response = requests.get(url, headers=self.get_headers(), params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get insights: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting insights: {str(e)}")
            return None
    
    def create_insight(self, insight_data):
        """
        Create a new insight.
        
        Args:
            insight_data (dict): Insight data to save
            
        Returns:
            dict: Created insight with ID, or None if the request failed
        """
        if not self.authenticate():
            return None
        
        try:
            url = f"{self.base_url}/insights"
            
            logger.info(f"Creating insight at {url}")
            response = requests.post(url, headers=self.get_headers(), json=insight_data)
            
            if response.status_code in (200, 201):
                return response.json()
            else:
                logger.error(f"Failed to create insight: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating insight: {str(e)}")
            return None

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize client
    client = SpringApiClient()
    
    # Test authentication
    if client.authenticate():
        print("Authentication successful!")
        
        # Test getting health data
        health_data = client.get_health_data(data_type="steps")
        print(f"Retrieved {len(health_data) if health_data else 0} health data records")
        
        # Test getting insights
        insights = client.get_insights()
        print(f"Retrieved {len(insights) if insights else 0} insights")