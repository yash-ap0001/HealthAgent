"""
Processor for heart rate data analysis.
"""
import logging
from datetime import datetime, timedelta
import pandas as pd
from processors.base_processor import BaseProcessor

logger = logging.getLogger(__name__)

class HeartRateProcessor(BaseProcessor):
    """Processor for heart rate data."""
    
    def __init__(self, api_client):
        """
        Initialize the heart rate processor.
        
        Args:
            api_client (ApiClient): The API client for interacting with the backend.
        """
        super().__init__(api_client)
        self.data_type = "heart_rate"
    
    def process(self):
        """
        Process heart rate data to generate analytics and insights.
        """
        logger.info("Processing heart rate data...")
        
        # Get heart rate data for the configured lookback period
        days = self.config.lookback_days
        hr_data = self.get_data_for_period(days)
        
        if hr_data.empty:
            logger.info(f"No heart rate data found for the last {days} days.")
            return
        
        # Analyze heart rate trend
        trend_analysis = self.analyze_trend(hr_data)
        logger.info(f"Heart rate trend analysis: {trend_analysis}")
        
        # Analyze resting heart rate
        resting_hr = self.analyze_resting_heart_rate(hr_data)
        logger.info(f"Resting heart rate analysis: {resting_hr}")
        
        # Identify heart rate zones
        hr_zones = self.analyze_heart_rate_zones(hr_data)
        logger.info(f"Heart rate zones: {hr_zones}")
        
        # Identify unusual heart rate patterns
        unusual_patterns = self.identify_unusual_patterns(hr_data)
        if unusual_patterns:
            logger.info(f"Found {len(unusual_patterns)} unusual heart rate patterns")
        
        return {
            'trend_analysis': trend_analysis,
            'resting_heart_rate': resting_hr,
            'heart_rate_zones': hr_zones,
            'unusual_patterns': unusual_patterns
        }
    
    def analyze_resting_heart_rate(self, hr_data):
        """
        Analyze resting heart rate.
        
        Args:
            hr_data (pandas.DataFrame): The heart rate data.
            
        Returns:
            dict: A dictionary containing resting heart rate metrics.
        """
        if hr_data.empty or len(hr_data) < 5:
            return {'average': None, 'trend': 'insufficient_data'}
        
        # Calculate daily minimum heart rates (approximation of resting HR)
        daily_min_hr = hr_data.groupby(hr_data['date'].dt.date)['value'].min().reset_index()
        
        # Calculate average resting heart rate
        avg_resting_hr = daily_min_hr['value'].mean()
        
        # Analyze trend in resting heart rate
        resting_hr_trend = self.analyze_trend(daily_min_hr)
        
        # Check if resting heart rate is elevated
        threshold = self.config.heart_rate_rest_threshold
        is_elevated = avg_resting_hr > threshold
        
        return {
            'average': avg_resting_hr,
            'trend': resting_hr_trend['trend'],
            'is_elevated': is_elevated,
            'threshold': threshold
        }
    
    def analyze_heart_rate_zones(self, hr_data):
        """
        Analyze time spent in different heart rate zones.
        
        Args:
            hr_data (pandas.DataFrame): The heart rate data.
            
        Returns:
            dict: A dictionary containing heart rate zone metrics.
        """
        if hr_data.empty:
            return {}
        
        # Define heart rate zones (approximate)
        # Assuming zones based on percentage of max HR (220 - age)
        # Since we don't know age, we'll use generic zones
        zones = {
            'rest': {'min': 0, 'max': 60},
            'light': {'min': 61, 'max': 100},
            'moderate': {'min': 101, 'max': 130},
            'vigorous': {'min': 131, 'max': 150},
            'max': {'min': 151, 'max': 220}
        }
        
        zone_counts = {zone: 0 for zone in zones}
        total_readings = len(hr_data)
        
        # Count readings in each zone
        for _, row in hr_data.iterrows():
            hr = row['value']
            for zone, limits in zones.items():
                if limits['min'] <= hr <= limits['max']:
                    zone_counts[zone] += 1
                    break
        
        # Calculate percentages
        zone_percentages = {
            zone: (count / total_readings) * 100 if total_readings > 0 else 0 
            for zone, count in zone_counts.items()
        }
        
        return {
            'counts': zone_counts,
            'percentages': zone_percentages,
            'total_readings': total_readings
        }
    
    def identify_unusual_patterns(self, hr_data, z_score_threshold=3.0):
        """
        Identify unusual heart rate patterns.
        
        Args:
            hr_data (pandas.DataFrame): The heart rate data.
            z_score_threshold (float): The z-score threshold for identifying outliers.
            
        Returns:
            list: A list of unusual heart rate patterns.
        """
        if len(hr_data) < 10:
            return []
        
        # Calculate mean and standard deviation
        mean_hr = hr_data['value'].mean()
        std_hr = hr_data['value'].std()
        
        # Calculate z-scores
        hr_data['z_score'] = (hr_data['value'] - mean_hr) / std_hr if std_hr > 0 else 0
        
        # Identify outliers
        outliers = hr_data[abs(hr_data['z_score']) > z_score_threshold]
        
        unusual_patterns = []
        for _, row in outliers.iterrows():
            date_str = row['date'].strftime("%Y-%m-%d") if hasattr(row['date'], 'strftime') else str(row['date'])
            direction = "high" if row['z_score'] > 0 else "low"
            unusual_patterns.append({
                'date': date_str,
                'heart_rate': row['value'],
                'direction': direction,
                'z_score': row['z_score']
            })
        
        return unusual_patterns
