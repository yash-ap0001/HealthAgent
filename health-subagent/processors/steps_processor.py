"""
Processor for steps data analysis.
"""
import logging
from datetime import datetime, timedelta
import pandas as pd
from processors.base_processor import BaseProcessor

logger = logging.getLogger(__name__)

class StepsProcessor(BaseProcessor):
    """Processor for steps data."""
    
    def __init__(self, api_client):
        """
        Initialize the steps processor.
        
        Args:
            api_client (ApiClient): The API client for interacting with the backend.
        """
        super().__init__(api_client)
        self.data_type = "steps"
    
    def process(self):
        """
        Process steps data to generate analytics and insights.
        """
        logger.info("Processing steps data...")
        
        # Get steps data for the configured lookback period
        days = self.config.lookback_days
        steps_data = self.get_data_for_period(days)
        
        if steps_data.empty:
            logger.info(f"No steps data found for the last {days} days.")
            return
        
        # Analyze steps trend
        trend_analysis = self.analyze_trend(steps_data)
        logger.info(f"Steps trend analysis: {trend_analysis}")
        
        # Check if the user is meeting their step goal
        step_goal = self.config.step_goal
        daily_averages = self.calculate_daily_averages(steps_data)
        
        # Log information about step goal achievement
        days_met_goal = len(daily_averages[daily_averages['value'] >= step_goal])
        total_days = len(daily_averages)
        goal_achievement_rate = days_met_goal / total_days if total_days > 0 else 0
        
        logger.info(f"Step goal achievement: {days_met_goal}/{total_days} days ({goal_achievement_rate:.2%})")
        
        # Identify days with unusual step counts
        unusual_days = self.identify_unusual_days(daily_averages)
        if unusual_days:
            logger.info(f"Found {len(unusual_days)} days with unusual step counts")
        
        return {
            'trend_analysis': trend_analysis,
            'goal_achievement_rate': goal_achievement_rate,
            'unusual_days': unusual_days
        }
    
    def calculate_daily_averages(self, steps_data):
        """
        Calculate daily averages for steps data.
        
        Args:
            steps_data (pandas.DataFrame): The steps data.
            
        Returns:
            pandas.DataFrame: A DataFrame with daily step averages.
        """
        if steps_data.empty:
            return pd.DataFrame()
        
        # Group by date and calculate sum (in case there are multiple entries per day)
        daily_steps = steps_data.groupby(steps_data['date'].dt.date)['value'].sum().reset_index()
        return daily_steps
    
    def identify_unusual_days(self, daily_steps, z_score_threshold=2.0):
        """
        Identify days with unusually high or low step counts.
        
        Args:
            daily_steps (pandas.DataFrame): The daily step counts.
            z_score_threshold (float): The z-score threshold for identifying outliers.
            
        Returns:
            list: A list of dates with unusual step counts.
        """
        if len(daily_steps) < 3:
            return []
        
        # Calculate mean and standard deviation
        mean_steps = daily_steps['value'].mean()
        std_steps = daily_steps['value'].std()
        
        # Calculate z-scores
        daily_steps['z_score'] = (daily_steps['value'] - mean_steps) / std_steps if std_steps > 0 else 0
        
        # Identify outliers
        outliers = daily_steps[abs(daily_steps['z_score']) > z_score_threshold]
        
        unusual_days = []
        for _, row in outliers.iterrows():
            date_str = row['date'].strftime("%Y-%m-%d") if hasattr(row['date'], 'strftime') else str(row['date'])
            direction = "high" if row['z_score'] > 0 else "low"
            unusual_days.append({
                'date': date_str,
                'steps': row['value'],
                'direction': direction,
                'z_score': row['z_score']
            })
        
        return unusual_days
