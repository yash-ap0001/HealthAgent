"""
Base processor for health data analysis.
"""
import logging
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

class BaseProcessor:
    """Base class for health data processors."""
    
    def __init__(self, api_client):
        """
        Initialize the base processor.
        
        Args:
            api_client (ApiClient): The API client for interacting with the backend.
        """
        self.api_client = api_client
        self.config = api_client.config
        self.data_type = None
    
    def process(self):
        """
        Process health data. This is the main method to be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the process method")
    
    def get_data_for_period(self, days=30):
        """
        Get health data for a specified period.
        
        Args:
            days (int): The number of days to look back.
            
        Returns:
            pandas.DataFrame: A DataFrame containing the health data.
        """
        if not self.data_type:
            raise ValueError("data_type must be set by the subclass")
            
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        data = self.api_client.get_health_data(
            data_type=self.data_type,
            start_date=start_date,
            end_date=end_date
        )
        
        if not data:
            return pd.DataFrame()
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(data)
        
        # Convert date strings to datetime objects
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            
        return df
    
    def analyze_trend(self, data, value_column='value'):
        """
        Analyze the trend in the health data.
        
        Args:
            data (pandas.DataFrame): The health data.
            value_column (str): The column name containing the values to analyze.
            
        Returns:
            dict: A dictionary containing trend analysis results.
        """
        if data.empty:
            return {
                'average': None,
                'min': None,
                'max': None,
                'trend': 'insufficient_data',
                'data_points': 0
            }
        
        # Basic statistics
        avg_value = data[value_column].mean()
        min_value = data[value_column].min()
        max_value = data[value_column].max()
        count = len(data)
        
        # Determine trend
        if count < 3:
            trend = 'insufficient_data'
        else:
            # Sort by date and calculate the trend
            sorted_data = data.sort_values('date')
            
            # Simple linear regression
            x = range(len(sorted_data))
            y = sorted_data[value_column].values
            
            if len(x) > 1:
                # Calculate slope
                n = len(x)
                sum_x = sum(x)
                sum_y = sum(y)
                sum_xy = sum(x_i * y_i for x_i, y_i in zip(x, y))
                sum_xx = sum(x_i * x_i for x_i in x)
                
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
                
                if slope > 0.05:
                    trend = 'increasing'
                elif slope < -0.05:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
        
        return {
            'average': avg_value,
            'min': min_value,
            'max': max_value,
            'trend': trend,
            'data_points': count
        }
