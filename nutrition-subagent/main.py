"""
Nutrition Sub-Agent: Analyzes nutrition data and generates insights.

This sub-agent is responsible for processing nutrition data from the Spring Boot
backend, analyzing dietary patterns, and generating personalized insights and
recommendations.
"""
import os
import sys
import logging
import argparse
import json
from datetime import datetime, timedelta

from .api_client import NutritionApiClient
from .nutrition_analyzer import NutritionAnalyzer
from .insights_engine import NutritionInsightsEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def authenticate(api_client):
    """
    Authenticate with the backend API.
    
    Args:
        api_client: The API client to authenticate
        
    Returns:
        bool: True if authentication was successful, False otherwise
    """
    logger.info("Authenticating with backend API")
    result = api_client.authenticate()
    
    if result:
        logger.info("Authentication successful")
    else:
        logger.error("Authentication failed")
    
    return result

def create_arg_parser():
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(description='Nutrition Sub-Agent')
    
    parser.add_argument(
        '--base-url', 
        type=str, 
        default=os.environ.get('API_BASE_URL', 'http://localhost:8080/api'),
        help='Base URL of the Spring Boot API'
    )
    
    parser.add_argument(
        '--username', 
        type=str, 
        default=os.environ.get('API_USERNAME', 'demo'),
        help='Username for API authentication'
    )
    
    parser.add_argument(
        '--password', 
        type=str, 
        default=os.environ.get('API_PASSWORD', 'password'),
        help='Password for API authentication'
    )
    
    parser.add_argument(
        '--user-id', 
        type=int, 
        default=os.environ.get('USER_ID', 1),
        help='User ID to analyze data for'
    )
    
    parser.add_argument(
        '--days', 
        type=int, 
        default=30,
        help='Number of days of data to analyze'
    )
    
    parser.add_argument(
        '--generate-insights', 
        action='store_true',
        help='Generate insights from nutrition data'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser

def main():
    """
    Main function to run the nutrition sub-agent.
    
    This function initializes the API client, authenticates with the backend,
    retrieves nutrition data, analyzes it, and generates insights.
    """
    # Parse command line arguments
    parser = create_arg_parser()
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"Starting Nutrition Sub-Agent with base URL: {args.base_url}")
    
    # Initialize API client
    api_client = NutritionApiClient(
        base_url=args.base_url,
        username=args.username,
        password=args.password,
        user_id=args.user_id
    )
    
    # Authenticate with backend
    if not authenticate(api_client):
        logger.error("Failed to authenticate with backend. Exiting.")
        sys.exit(1)
    
    # Get nutrition data
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    
    logger.info(f"Retrieving nutrition data for user {args.user_id} from {start_date} to {end_date}")
    nutrition_data = api_client.get_nutrition_data(
        user_id=args.user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    if not nutrition_data:
        logger.warning("No nutrition data retrieved. Exiting.")
        sys.exit(1)
    
    logger.info(f"Retrieved {len(nutrition_data)} nutrition data points")
    
    # Initialize nutrition analyzer
    analyzer = NutritionAnalyzer()
    
    # Perform comprehensive analysis
    logger.info("Performing nutrition analysis")
    analysis = analyzer.analyze_nutrition(nutrition_data, args.user_id)
    
    # Output analysis summary
    logger.info("Nutrition Analysis Summary:")
    logger.info(f"Period: {analysis.period['start']} to {analysis.period['end']}")
    logger.info(f"Daily Averages: {json.dumps(analysis.dailyAverages, default=str)}")
    logger.info(f"Calorie Trend: {analysis.calorieIntakeTrend.trend}")
    logger.info(f"Protein Trend: {analysis.proteinIntakeTrend.trend}")
    logger.info(f"Carbs Trend: {analysis.carbIntakeTrend.trend}")
    logger.info(f"Fat Trend: {analysis.fatIntakeTrend.trend}")
    logger.info(f"Nutritional Gaps: {len(analysis.nutritionalGaps)}")
    logger.info(f"Positive Patterns: {len(analysis.positivePatterns)}")
    
    # Generate insights if requested
    if args.generate_insights:
        logger.info("Generating nutrition insights")
        insights_engine = NutritionInsightsEngine(api_client)
        insights = insights_engine.generate_insights(args.user_id)
        
        logger.info(f"Generated and saved {len(insights)} insights")
        for i, insight in enumerate(insights, 1):
            logger.info(f"Insight {i}: {insight.get('title', 'Unknown')}")
    
    logger.info("Nutrition Sub-Agent completed successfully")

if __name__ == "__main__":
    main()