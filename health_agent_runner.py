"""
Health Agent Runner

This script enhances the health sub-agent with ML capabilities
and runs the analysis on health data from the Spring Boot backend.
"""

import os
import logging
import json
from datetime import datetime, timedelta
from ml_analyzer import HealthMLAnalyzer
from spring_api_client import SpringApiClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_health_agent():
    """Run the health sub-agent with enhanced ML capabilities."""
    logger.info("Starting Health Agent with ML enhancements")
    
    # Initialize the API client - use the Flask app API endpoints
    client = SpringApiClient(base_url="http://localhost:5000/api")
    if not client.authenticate():
        logger.error("Failed to authenticate with API")
        return False
    
    # Initialize the ML analyzer
    analyzer = HealthMLAnalyzer()
    
    # Define date range for analysis (last 30 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Get health data from the API
    logger.info("Fetching steps data...")
    steps_data = client.get_health_data(
        data_type="steps",
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    
    logger.info("Fetching sleep data...")
    sleep_data = client.get_health_data(
        data_type="sleep",
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    
    logger.info("Fetching heart rate data...")
    heart_rate_data = client.get_health_data(
        data_type="heart_rate",
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    
    # Log data count to debug
    logger.info(f"Retrieved {len(steps_data) if steps_data else 0} steps records")
    logger.info(f"Retrieved {len(sleep_data) if sleep_data else 0} sleep records")
    logger.info(f"Retrieved {len(heart_rate_data) if heart_rate_data else 0} heart rate records")
    
    if not steps_data and not sleep_data and not heart_rate_data:
        logger.warning("No health data available for analysis")
        return False
    
    # Perform analyses
    insights = []
    
    # 1. Anomaly detection
    if steps_data:
        logger.info(f"Analyzing {len(steps_data)} steps records")
        steps_anomalies = analyzer.detect_anomalies(steps_data)
        if steps_anomalies:
            logger.info(f"Detected {len(steps_anomalies)} anomalies in steps data")
            high_anomalies = [a for a in steps_anomalies if a['direction'] == 'high']
            low_anomalies = [a for a in steps_anomalies if a['direction'] == 'low']
            
            if high_anomalies:
                dates = ", ".join([a['date'] for a in high_anomalies[:3]])
                if len(high_anomalies) > 3:
                    dates += f" and {len(high_anomalies) - 3} more"
                
                insights.append({
                    "userId": 1,  # Using test user ID
                    "category": "activity",
                    "title": "Unusually High Activity Detected",
                    "description": f"You had unusually high step counts on: {dates}.",
                    "severity": 2,
                    "isActionable": False,
                    "recommendation": "These days show much higher activity than your normal pattern. What activities did you do on these days?"
                })
            
            if low_anomalies:
                dates = ", ".join([a['date'] for a in low_anomalies[:3]])
                if len(low_anomalies) > 3:
                    dates += f" and {len(low_anomalies) - 3} more"
                
                insights.append({
                    "userId": 1,  # Using test user ID
                    "category": "activity",
                    "title": "Unusually Low Activity Detected",
                    "description": f"You had unusually low step counts on: {dates}.",
                    "severity": 3,
                    "isActionable": True,
                    "recommendation": "These days show much lower activity than your normal pattern. Consider adding more activity on similar days in the future."
                })
    
    if sleep_data:
        logger.info(f"Analyzing {len(sleep_data)} sleep records")
        sleep_anomalies = analyzer.detect_anomalies(sleep_data)
        if sleep_anomalies:
            logger.info(f"Detected {len(sleep_anomalies)} anomalies in sleep data")
            short_sleep = [a for a in sleep_anomalies if a['direction'] == 'low']
            
            if short_sleep:
                dates = ", ".join([a['date'] for a in short_sleep[:3]])
                if len(short_sleep) > 3:
                    dates += f" and {len(short_sleep) - 3} more"
                
                insights.append({
                    "userId": 1,  # Using test user ID
                    "category": "sleep",
                    "title": "Sleep Deprivation Detected",
                    "description": f"You had unusually short sleep duration on: {dates}.",
                    "severity": 4,
                    "isActionable": True,
                    "recommendation": "Consistent sleep deprivation can impact health and cognitive function. Try to identify what disrupted your sleep on these days."
                })
    
    # 2. Pattern recognition
    if steps_data:
        patterns = analyzer.identify_patterns(steps_data)
        if patterns.get('status') == 'success':
            logger.info(f"Identified {len(patterns['patterns'])} patterns in steps data")
            
            weekday_pattern = None
            weekend_pattern = None
            
            for pattern in patterns['patterns']:
                if 'Saturday' in pattern['dominant_days'] or 'Sunday' in pattern['dominant_days']:
                    weekend_pattern = pattern
                else:
                    weekday_pattern = pattern
            
            if weekday_pattern and weekend_pattern:
                diff = weekend_pattern['average'] - weekday_pattern['average']
                if abs(diff) > 2000:  # Significant difference
                    if diff > 0:
                        insights.append({
                            "userId": 1,
                            "category": "activity",
                            "title": "Higher Weekend Activity",
                            "description": f"You're more active on weekends (avg. {weekend_pattern['average']:.0f} steps) compared to weekdays (avg. {weekday_pattern['average']:.0f} steps).",
                            "severity": 2,
                            "isActionable": True,
                            "recommendation": "Consider incorporating more movement into your weekday routine to maintain consistent activity levels throughout the week."
                        })
                    else:
                        insights.append({
                            "userId": 1,
                            "category": "activity",
                            "title": "Lower Weekend Activity",
                            "description": f"You're less active on weekends (avg. {weekend_pattern['average']:.0f} steps) compared to weekdays (avg. {weekday_pattern['average']:.0f} steps).",
                            "severity": 2,
                            "isActionable": True,
                            "recommendation": "Try to maintain your weekday activity levels through the weekend by planning active outings or recreational activities."
                        })
    
    # 3. Correlation analysis
    if steps_data and sleep_data:
        correlation = analyzer.analyze_correlation(steps_data, sleep_data)
        if correlation.get('status') == 'success' and correlation.get('significance') == 'significant':
            logger.info(f"Found significant correlation between steps and sleep: {correlation['correlation']:.2f}")
            
            if correlation['direction'] == 'positive':
                insights.append({
                    "userId": 1,
                    "category": "general",
                    "title": "Activity Improves Sleep Quality",
                    "description": "Days with higher step counts are associated with longer sleep duration.",
                    "severity": 1,
                    "isActionable": True,
                    "recommendation": "Maintaining regular physical activity appears to benefit your sleep. Consider staying active to support healthy sleep patterns."
                })
            else:
                insights.append({
                    "userId": 1,
                    "category": "general",
                    "title": "Activity and Sleep Pattern",
                    "description": "Days with higher step counts are associated with shorter sleep duration.",
                    "severity": 2,
                    "isActionable": True,
                    "recommendation": "Your data suggests physical activity might be affecting your sleep duration. Consider adjusting when you exercise to see if it improves your sleep."
                })
    
    # 4. Time series forecasting
    if steps_data:
        forecast = analyzer.forecast_values(steps_data)
        if forecast.get('status') == 'success':
            logger.info(f"Generated forecast for next {len(forecast['forecast'])} days")
            
            # Calculate trend from forecast
            if len(forecast['forecast']) >= 7:
                first_values = [f['value'] for f in forecast['forecast'][:3]]
                last_values = [f['value'] for f in forecast['forecast'][-3:]]
                
                avg_first = sum(first_values) / len(first_values)
                avg_last = sum(last_values) / len(last_values)
                
                if avg_last > avg_first * 1.1:  # 10% increase
                    insights.append({
                        "userId": 1,
                        "category": "activity",
                        "title": "Positive Activity Trend Forecast",
                        "description": "Based on your recent patterns, your activity level is projected to increase over the next week.",
                        "severity": 1,
                        "isActionable": False,
                        "recommendation": "Keep up your momentum to maintain this positive trajectory."
                    })
                elif avg_last < avg_first * 0.9:  # 10% decrease
                    insights.append({
                        "userId": 1,
                        "category": "activity",
                        "title": "Declining Activity Trend Forecast",
                        "description": "Based on your recent patterns, your activity level is projected to decrease over the next week.",
                        "severity": 3,
                        "isActionable": True,
                        "recommendation": "Be mindful of this projected decline. Consider scheduling activities to maintain your step count."
                    })
    
    # Save insights to API
    if insights:
        logger.info(f"Sending {len(insights)} insights to API")
        for insight in insights:
            result = client.create_insight(insight)
            if result:
                logger.info(f"Created insight: {insight['title']}")
            else:
                logger.error(f"Failed to create insight: {insight['title']}")
    else:
        logger.info("No new insights generated")
    
    logger.info("Health Agent analysis completed")
    return True

if __name__ == "__main__":
    run_health_agent()