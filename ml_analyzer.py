"""
Machine Learning Health Data Analyzer

This module provides advanced ML-based analysis for health data.
It includes time series forecasting, anomaly detection, and pattern recognition.
"""

import logging
import numpy as np
import json
from datetime import datetime, timedelta
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

logger = logging.getLogger(__name__)

class HealthMLAnalyzer:
    """ML analyzer for health data metrics."""
    
    def __init__(self):
        """Initialize the ML analyzer."""
        self.scaler = StandardScaler()
    
    def _convert_to_dataframe(self, health_data, value_column='value'):
        """
        Convert health data list to pandas DataFrame.
        
        Args:
            health_data (list): List of health data dictionaries
            value_column (str): The name of the column containing the values
            
        Returns:
            pd.DataFrame: DataFrame with formatted data
        """
        if not health_data:
            return None
        
        # Extract data and convert dates
        data = []
        for item in health_data:
            try:
                date = item.get('date')
                if isinstance(date, str):
                    date = datetime.strptime(date, '%Y-%m-%d').date()
                
                # Extract metadata if available
                meta = {}
                meta_str = item.get('meta_data')
                if meta_str:
                    try:
                        if isinstance(meta_str, str):
                            meta = json.loads(meta_str)
                        elif isinstance(meta_str, dict):
                            meta = meta_str
                    except:
                        pass
                
                data.append({
                    'id': item.get('id'),
                    'date': date,
                    'value': float(item.get('value', 0)),
                    'metadata': meta,
                    'data_type': item.get('data_type'),
                    'unit': item.get('unit')
                })
            except Exception as e:
                logger.error(f"Error converting health data item: {str(e)}")
        
        # Create DataFrame and sort by date
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values(by='date')
        
        return df
    
    def detect_anomalies(self, health_data, contamination=0.05):
        """
        Detect anomalies in health data using Isolation Forest.
        
        Args:
            health_data (list): List of health data dictionaries
            contamination (float): Expected proportion of anomalies
            
        Returns:
            list: List of detected anomalies with dates and values
        """
        df = self._convert_to_dataframe(health_data)
        if df is None or len(df) < 5:
            return []
        
        try:
            # Prepare data for anomaly detection
            values = df['value'].values.reshape(-1, 1)
            
            # Apply Isolation Forest for anomaly detection
            model = IsolationForest(contamination=contamination, random_state=42)
            df['anomaly'] = model.fit_predict(values)
            
            # Extract anomalies (anomaly == -1)
            anomalies = df[df['anomaly'] == -1]
            
            # If no anomalies detected, try a more sensitive approach
            if len(anomalies) == 0:
                # Simplify to using mean ± 2*std as anomaly threshold
                mean_val = df['value'].mean()
                std_val = df['value'].std() if len(df) > 1 else 1.0
                upper_threshold = mean_val + 2 * std_val
                lower_threshold = mean_val - 2 * std_val
                anomalies = df[(df['value'] > upper_threshold) | (df['value'] < lower_threshold)]
            
            # Calculate simple z-scores
            mean_val = df['value'].mean()
            std_val = df['value'].std() if len(df) > 1 else 1.0
            if std_val == 0:  # Avoid division by zero
                std_val = 1.0
            
            # Format results
            result = []
            for _, row in anomalies.iterrows():
                try:
                    date_str = row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date'])
                    # Calculate z-score directly here
                    z = (row['value'] - mean_val) / std_val
                    result.append({
                        'date': date_str,
                        'value': float(row['value']),
                        'zscore': abs(float(z)),
                        'direction': 'high' if row['value'] > mean_val else 'low',
                        'data_type': str(row['data_type']),
                        'id': int(row['id']) if pd.notna(row['id']) else None
                    })
                except Exception as detail_error:
                    logger.warning(f"Error formatting anomaly row: {str(detail_error)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return []
    
    def forecast_values(self, health_data, days_to_forecast=7):
        """
        Forecast future values using ARIMA time series forecasting.
        
        Args:
            health_data (list): List of health data dictionaries
            days_to_forecast (int): Number of days to forecast
            
        Returns:
            dict: Dictionary with forecast values and dates
        """
        df = self._convert_to_dataframe(health_data)
        if df is None or len(df) < 10:  # Need sufficient data for forecasting
            return {
                'status': 'insufficient_data',
                'forecast': []
            }
        
        try:
            # Set date as index for time series analysis
            ts_data = df.set_index('date')['value']
            
            # Fit ARIMA model
            # p, d, q parameters can be optimized based on the data
            model = ARIMA(ts_data, order=(1, 1, 1))
            model_fit = model.fit()
            
            # Generate forecast
            forecast_dates = [max(ts_data.index) + timedelta(days=i+1) for i in range(days_to_forecast)]
            forecast = model_fit.forecast(steps=days_to_forecast)
            
            # Format results
            result = []
            for i, date in enumerate(forecast_dates):
                result.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'value': max(0, forecast.iloc[i] if i < len(forecast) else forecast.iloc[-1]),  # Ensure non-negative values and safe access
                    'data_type': df['data_type'].iloc[0]
                })
            
            return {
                'status': 'success',
                'forecast': result
            }
            
        except Exception as e:
            logger.error(f"Error forecasting values: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'forecast': []
            }
    
    def identify_patterns(self, health_data, num_clusters=3):
        """
        Identify patterns in health data using clustering.
        
        Args:
            health_data (list): List of health data dictionaries
            num_clusters (int): Number of clusters to identify
            
        Returns:
            dict: Dictionary with identified patterns
        """
        df = self._convert_to_dataframe(health_data)
        if df is None or len(df) < num_clusters * 2:
            return {
                'status': 'insufficient_data',
                'patterns': []
            }
        
        try:
            # Simple approach: create a weekday classifier based on date pattern
            # Create a new dataframe with just the needed columns
            analysis_df = pd.DataFrame({
                'value': df['value'].values
            })
            
            # Try to determine weekday from the date
            weekdays = []
            for i, row in df.iterrows():
                try:
                    if isinstance(row['date'], pd.Timestamp) or isinstance(row['date'], datetime):
                        weekday = row['date'].weekday()
                    elif isinstance(row['date'], str):
                        dt = pd.to_datetime(row['date'])
                        weekday = dt.weekday()
                    else:
                        # Fallback to assigning based on index
                        weekday = i % 7
                    weekdays.append(weekday)
                except:
                    # Fallback to assigning based on index
                    weekdays.append(i % 7)
            
            analysis_df['day_of_week'] = weekdays
            
            # Prepare features: day of week and value
            features = analysis_df[['day_of_week', 'value']].values
            
            # Scale features
            scaled_features = self.scaler.fit_transform(features)
            
            # Apply K-means clustering
            num_clusters = min(num_clusters, len(df) // 2)
            num_clusters = max(2, num_clusters)  # Ensure at least 2 clusters
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            analysis_df['cluster'] = kmeans.fit_predict(scaled_features)
            
            # Analyze clusters
            patterns = []
            for cluster_id in range(kmeans.n_clusters):
                cluster_data = analysis_df[analysis_df['cluster'] == cluster_id]
                
                # Skip empty clusters
                if len(cluster_data) == 0:
                    continue
                
                # Calculate statistics
                avg_value = cluster_data['value'].mean()
                std_value = cluster_data['value'].std() if len(cluster_data) > 1 else 0
                
                # Get most common days of week in this cluster
                day_counts = cluster_data['day_of_week'].value_counts()
                # Set a minimum threshold or use mean
                threshold = max(1, day_counts.mean() if len(day_counts) > 0 else 0)
                dominant_days = day_counts[day_counts >= threshold].index.tolist()
                
                # Convert day numbers to names
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                dominant_day_names = [day_names[int(day) % 7] for day in dominant_days]
                
                # Get data type from original dataframe
                data_type = "unknown"
                if 'data_type' in df.columns and len(df) > 0:
                    data_type = str(df['data_type'].iloc[0])
                
                patterns.append({
                    'cluster_id': int(cluster_id),
                    'count': int(len(cluster_data)),
                    'average': float(avg_value),
                    'std_dev': float(std_value),
                    'dominant_days': dominant_day_names,
                    'description': self._generate_pattern_description(
                        data_type, 
                        float(avg_value), 
                        dominant_day_names
                    )
                })
            
            return {
                'status': 'success',
                'patterns': patterns
            }
            
        except Exception as e:
            logger.error(f"Error identifying patterns: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'patterns': []
            }
    
    def _generate_pattern_description(self, data_type, avg_value, dominant_days):
        """Generate a human-readable description of the pattern."""
        if not dominant_days:
            days_text = "various days"
        elif len(dominant_days) == 1:
            days_text = dominant_days[0]
        elif len(dominant_days) == 2:
            days_text = f"{dominant_days[0]} and {dominant_days[1]}"
        else:
            days_text = f"{', '.join(dominant_days[:-1])} and {dominant_days[-1]}"
        
        if data_type == 'steps':
            if avg_value > 10000:
                level = "high"
            elif avg_value > 7500:
                level = "good"
            elif avg_value > 5000:
                level = "moderate"
            else:
                level = "low"
            
            return f"{level.capitalize()} activity level (avg. {avg_value:.0f} steps) on {days_text}"
            
        elif data_type == 'sleep':
            if avg_value > 8:
                level = "excellent"
            elif avg_value > 7:
                level = "good"
            elif avg_value > 6:
                level = "moderate"
            else:
                level = "poor"
            
            return f"{level.capitalize()} sleep duration (avg. {avg_value:.1f} hours) on {days_text}"
            
        elif data_type == 'heart_rate':
            if avg_value < 60:
                level = "very good"
            elif avg_value < 70:
                level = "good"
            elif avg_value < 80:
                level = "moderate"
            else:
                level = "elevated"
            
            return f"{level.capitalize()} resting heart rate (avg. {avg_value:.0f} bpm) on {days_text}"
            
        else:
            return f"Average {data_type} of {avg_value:.1f} on {days_text}"
    
    def analyze_correlation(self, data_series1, data_series2):
        """
        Analyze correlation between two health data series.
        
        Args:
            data_series1 (list): First list of health data dictionaries
            data_series2 (list): Second list of health data dictionaries
            
        Returns:
            dict: Dictionary with correlation analysis
        """
        df1 = self._convert_to_dataframe(data_series1)
        df2 = self._convert_to_dataframe(data_series2)
        
        if df1 is None or df2 is None or len(df1) < 5 or len(df2) < 5:
            return {
                'status': 'insufficient_data',
                'correlation': None
            }
        
        try:
            # Merge dataframes on date
            merged = pd.merge(
                df1[['date', 'value', 'data_type']], 
                df2[['date', 'value', 'data_type']], 
                on='date', 
                suffixes=('_1', '_2')
            )
            
            if len(merged) < 5:
                return {
                    'status': 'insufficient_overlap',
                    'correlation': None
                }
            
            # Calculate correlation
            correlation, p_value = stats.pearsonr(merged['value_1'], merged['value_2'])
            
            # Determine correlation strength
            if abs(correlation) > 0.7:
                strength = "strong"
            elif abs(correlation) > 0.4:
                strength = "moderate"
            elif abs(correlation) > 0.2:
                strength = "weak"
            else:
                strength = "very weak"
            
            # Determine direction
            direction = "positive" if correlation > 0 else "negative"
            
            # Generate description
            data_type1 = merged['data_type_1'].iloc[0]
            data_type2 = merged['data_type_2'].iloc[0]
            
            if p_value < 0.05:
                significance = "significant"
                if direction == "positive":
                    description = f"Higher {data_type1} values are associated with higher {data_type2} values."
                else:
                    description = f"Higher {data_type1} values are associated with lower {data_type2} values."
            else:
                significance = "not significant"
                description = f"There is no significant relationship between {data_type1} and {data_type2}."
            
            return {
                'status': 'success',
                'correlation': float(correlation),
                'p_value': float(p_value),
                'strength': strength,
                'direction': direction,
                'significance': significance,
                'description': description,
                'data_points': len(merged)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing correlation: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'correlation': None
            }

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = HealthMLAnalyzer()
    
    # Example health data
    steps_data = [
        {"id": 1, "date": "2023-01-01", "value": 8000, "data_type": "steps"},
        {"id": 2, "date": "2023-01-02", "value": 9000, "data_type": "steps"},
        {"id": 3, "date": "2023-01-03", "value": 7500, "data_type": "steps"},
        {"id": 4, "date": "2023-01-04", "value": 12000, "data_type": "steps"},  # anomaly
        {"id": 5, "date": "2023-01-05", "value": 8200, "data_type": "steps"},
    ]
    
    # Detect anomalies
    anomalies = analyzer.detect_anomalies(steps_data)
    print(f"Detected {len(anomalies)} anomalies")
    for anomaly in anomalies:
        print(f"Anomaly on {anomaly['date']}: {anomaly['value']} steps")