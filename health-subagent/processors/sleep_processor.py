"""
Processor for sleep data analysis.
"""
import logging
from datetime import datetime, timedelta
import pandas as pd
from processors.base_processor import BaseProcessor

logger = logging.getLogger(__name__)

class SleepProcessor(BaseProcessor):
    """Processor for sleep data."""
    
    def __init__(self, api_client):
        """
        Initialize the sleep processor.
        
        Args:
            api_client (ApiClient): The API client for interacting with the backend.
        """
        super().__init__(api_client)
        self.data_type = "sleep"
    
    def process(self):
        """
        Process sleep data to generate analytics and insights.
        """
        logger.info("Processing sleep data...")
        
        # Get sleep data for the configured lookback period
        days = self.config.lookback_days
        sleep_data = self.get_data_for_period(days)
        
        if sleep_data.empty:
            logger.info(f"No sleep data found for the last {days} days.")
            return
        
        # Analyze sleep trend
        trend_analysis = self.analyze_trend(sleep_data)
        logger.info(f"Sleep trend analysis: {trend_analysis}")
        
        # Check if the user is meeting their sleep goal
        sleep_goal = self.config.sleep_goal_hours
        daily_sleep = self.calculate_daily_sleep(sleep_data)
        
        # Log information about sleep goal achievement
        days_met_goal = len(daily_sleep[daily_sleep['value'] >= sleep_goal])
        total_days = len(daily_sleep)
        goal_achievement_rate = days_met_goal / total_days if total_days > 0 else 0
        
        logger.info(f"Sleep goal achievement: {days_met_goal}/{total_days} days ({goal_achievement_rate:.2%})")
        
        # Analyze sleep consistency
        sleep_consistency = self.analyze_sleep_consistency(daily_sleep)
        logger.info(f"Sleep consistency: {sleep_consistency}")
        
        # Identify days with unusual sleep patterns
        unusual_days = self.identify_unusual_sleep(daily_sleep)
        if unusual_days:
            logger.info(f"Found {len(unusual_days)} days with unusual sleep patterns")
        
        return {
            'trend_analysis': trend_analysis,
            'goal_achievement_rate': goal_achievement_rate,
            'sleep_consistency': sleep_consistency,
            'unusual_days': unusual_days
        }
    
    def calculate_daily_sleep(self, sleep_data):
        """
        Calculate daily sleep duration.
        
        Args:
            sleep_data (pandas.DataFrame): The sleep data.
            
        Returns:
            pandas.DataFrame: A DataFrame with daily sleep duration.
        """
        if sleep_data.empty:
            return pd.DataFrame()
        
        # Group by date and take the sum (in case there are multiple entries)
        daily_sleep = sleep_data.groupby(sleep_data['date'].dt.date)['value'].sum().reset_index()
        return daily_sleep
    
    def analyze_sleep_consistency(self, daily_sleep):
        """
        Analyze the consistency of sleep duration.
        
        Args:
            daily_sleep (pandas.DataFrame): The daily sleep duration.
            
        Returns:
            dict: A dictionary containing sleep consistency metrics.
        """
        if len(daily_sleep) < 3:
            return {'consistency': 'insufficient_data', 'std_dev': None}
        
        # Calculate standard deviation of sleep duration
        std_dev = daily_sleep['value'].std()
        
        # Categorize consistency
        if std_dev < 0.5:  # Less than 30 minutes variation
            consistency = 'very_consistent'
        elif std_dev < 1.0:  # Less than 1 hour variation
            consistency = 'consistent'
        elif std_dev < 1.5:  # Less than 1.5 hours variation
            consistency = 'moderately_consistent'
        else:
            consistency = 'inconsistent'
        
        return {
            'consistency': consistency,
            'std_dev': std_dev
        }
    
    def identify_unusual_sleep(self, daily_sleep, z_score_threshold=2.0):
        """
        Identify days with unusually long or short sleep duration.
        
        Args:
            daily_sleep (pandas.DataFrame): The daily sleep duration.
            z_score_threshold (float): The z-score threshold for identifying outliers.
            
        Returns:
            list: A list of dates with unusual sleep patterns.
        """
        if len(daily_sleep) < 3:
            return []
        
        # Calculate mean and standard deviation
        mean_sleep = daily_sleep['value'].mean()
        std_sleep = daily_sleep['value'].std()
        
        # Calculate z-scores
        daily_sleep['z_score'] = (daily_sleep['value'] - mean_sleep) / std_sleep if std_sleep > 0 else 0
        
        # Identify outliers
        outliers = daily_sleep[abs(daily_sleep['z_score']) > z_score_threshold]
        
        unusual_days = []
        for _, row in outliers.iterrows():
            date_str = row['date'].strftime("%Y-%m-%d") if hasattr(row['date'], 'strftime') else str(row['date'])
            direction = "long" if row['z_score'] > 0 else "short"
            unusual_days.append({
                'date': date_str,
                'sleep_hours': row['value'],
                'direction': direction,
                'z_score': row['z_score']
            })
        
        return unusual_days
