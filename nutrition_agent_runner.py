"""
Nutrition Agent Runner

This script enhances the nutrition sub-agent with ML capabilities
and runs the analysis on nutrition data from the Spring Boot backend.
"""
import logging
import os
from datetime import datetime, timedelta
from flask import current_app

from app import db
from models import HealthData, Insight, User
from nutrition_subagent.api_client import NutritionApiClient
from nutrition_subagent.nutrition_analyzer import NutritionAnalyzer
from nutrition_subagent.insights_engine import NutritionInsightsEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_nutrition_agent():
    """Run the nutrition sub-agent with enhanced ML capabilities."""
    logger.info("Starting nutrition agent analysis")
    
    try:
        # Create a specialized API client that works with the Spring Boot backend
        # For development/testing, use direct DB access if no Spring Boot server is available
        class DirectDBClient:
            def __init__(self, user_id=1):
                """Initialize with user ID."""
                self.user_id = user_id
                self.authenticated = True
            
            def authenticate(self):
                """Simulate authentication by checking if user exists."""
                user = User.query.get(self.user_id)
                self.authenticated = user is not None
                return self.authenticated
            
            def get_nutrition_data(self, user_id=None, start_date=None, end_date=None):
                """Get nutrition data directly from the database."""
                user_id = user_id or self.user_id
                
                query = HealthData.query.filter_by(user_id=user_id)
                
                # Filter by data type for nutrition records
                query = query.filter(HealthData.data_type.in_(['nutrition', 'meal', 'diet']))
                
                # Apply date filters if provided
                if start_date:
                    query = query.filter(HealthData.date >= start_date)
                if end_date:
                    query = query.filter(HealthData.date <= end_date)
                
                # Convert to nutrition data format
                nutrition_data = []
                for record in query.all():
                    # Basic nutrition data record
                    nutrition_record = {
                        'id': record.id,
                        'userId': record.user_id,
                        'date': record.date.isoformat(),
                        'value': record.value,
                    }
                    
                    # Add additional fields from metadata if available
                    if record.meta_data:
                        try:
                            metadata = eval(record.meta_data)  # Convert string to dict
                            # Extract nutrition-specific fields
                            nutrition_record['mealType'] = metadata.get('mealType', 'other')
                            nutrition_record['foodName'] = metadata.get('foodName', 'Unknown food')
                            nutrition_record['calories'] = float(metadata.get('calories', record.value))
                            nutrition_record['protein'] = float(metadata.get('protein', 0))
                            nutrition_record['carbs'] = float(metadata.get('carbs', 0))
                            nutrition_record['fat'] = float(metadata.get('fat', 0))
                            nutrition_record['fiber'] = float(metadata.get('fiber', 0))
                            nutrition_record['sugar'] = float(metadata.get('sugar', 0))
                            nutrition_record['sodium'] = float(metadata.get('sodium', 0))
                            nutrition_record['unit'] = metadata.get('unit', 'g')
                        except:
                            # If metadata parsing fails, use defaults
                            nutrition_record['mealType'] = 'unknown'
                            nutrition_record['foodName'] = f"{record.data_type} record"
                            nutrition_record['calories'] = float(record.value)
                            nutrition_record['protein'] = 0.0
                            nutrition_record['carbs'] = 0.0
                            nutrition_record['fat'] = 0.0
                            nutrition_record['unit'] = 'g'
                    else:
                        # Default values if no metadata
                        nutrition_record['mealType'] = 'unknown'
                        nutrition_record['foodName'] = f"{record.data_type} record"
                        nutrition_record['calories'] = float(record.value)
                        nutrition_record['protein'] = 0.0
                        nutrition_record['carbs'] = 0.0
                        nutrition_record['fat'] = 0.0
                        nutrition_record['unit'] = 'g'
                    
                    nutrition_record['source'] = record.source or 'database'
                    nutrition_record['createdAt'] = record.created_at.isoformat() if record.created_at else None
                    nutrition_record['updatedAt'] = record.updated_at.isoformat() if record.updated_at else None
                    
                    nutrition_data.append(nutrition_record)
                
                logger.info(f"Retrieved {len(nutrition_data)} nutrition records for user {user_id}")
                return nutrition_data
            
            def create_nutrition_insight(self, insight_data):
                """Create nutrition insight directly in the database."""
                try:
                    # Convert from nutrition insight format to database model
                    new_insight = Insight(
                        user_id=insight_data.get('userId', self.user_id),
                        category=insight_data.get('category', 'nutrition'),
                        title=insight_data.get('title'),
                        description=insight_data.get('description'),
                        severity=insight_data.get('severity', 1),
                        is_actionable=insight_data.get('isActionable', True),
                        recommendation=insight_data.get('recommendation'),
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    # Add and commit to database
                    db.session.add(new_insight)
                    db.session.commit()
                    
                    # Return the created insight in API format
                    created_insight = {
                        'id': new_insight.id,
                        'userId': new_insight.user_id,
                        'category': new_insight.category,
                        'title': new_insight.title,
                        'description': new_insight.description,
                        'severity': new_insight.severity,
                        'isActionable': new_insight.is_actionable,
                        'recommendation': new_insight.recommendation,
                        'createdAt': new_insight.created_at.isoformat() if new_insight.created_at else None,
                        'updatedAt': new_insight.updated_at.isoformat() if new_insight.updated_at else None
                    }
                    
                    logger.info(f"Created new nutrition insight with ID {new_insight.id}: {new_insight.title}")
                    return created_insight
                
                except Exception as e:
                    logger.error(f"Error creating nutrition insight: {str(e)}")
                    db.session.rollback()
                    return None
        
        # Use the direct DB client (in production this would use the Spring Boot API client)
        api_client = DirectDBClient(user_id=1)
        
        # Authenticate
        if not api_client.authenticate():
            logger.error("Failed to authenticate with database")
            return {
                'success': False,
                'message': 'Authentication failed',
                'insights_generated': 0
            }
        
        # Create nutritional analyzer and insights engine
        analyzer = NutritionAnalyzer()
        insights_engine = NutritionInsightsEngine(api_client)
        
        # Generate insights
        insights = insights_engine.generate_insights(user_id=1)
        
        return {
            'success': True,
            'message': f'Successfully generated {len(insights)} nutrition insights',
            'insights_generated': len(insights),
            'insights': insights
        }
    
    except Exception as e:
        logger.error(f"Error running nutrition agent: {str(e)}")
        return {
            'success': False,
            'message': f'Error running nutrition agent: {str(e)}',
            'insights_generated': 0
        }

if __name__ == "__main__":
    # This allows running the agent directly for testing
    from app import app
    with app.app_context():
        result = run_nutrition_agent()
        print(result)