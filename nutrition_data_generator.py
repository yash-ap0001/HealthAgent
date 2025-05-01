"""
Nutrition Data Generator for Health AI System

This script generates realistic nutrition data for testing and demonstration purposes.
It populates the database with nutritional meal records for users.
"""
import os
import sys
import random
import json
from datetime import datetime, timedelta
import argparse
import logging

from app import app, db
from models import User, HealthData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define realistic food data
FOODS = {
    'breakfast': [
        {'name': 'Oatmeal with berries', 'calories': 320, 'protein': 12, 'carbs': 54, 'fat': 6, 'fiber': 8, 'sugar': 12, 'sodium': 10, 'unit': 'bowl'},
        {'name': 'Scrambled eggs with toast', 'calories': 420, 'protein': 20, 'carbs': 35, 'fat': 22, 'fiber': 2, 'sugar': 3, 'sodium': 580, 'unit': 'plate'},
        {'name': 'Greek yogurt with granola', 'calories': 350, 'protein': 22, 'carbs': 38, 'fat': 12, 'fiber': 4, 'sugar': 20, 'sodium': 90, 'unit': 'cup'},
        {'name': 'Protein smoothie', 'calories': 380, 'protein': 25, 'carbs': 45, 'fat': 10, 'fiber': 5, 'sugar': 30, 'sodium': 150, 'unit': 'glass'},
        {'name': 'Pancakes with maple syrup', 'calories': 520, 'protein': 10, 'carbs': 80, 'fat': 15, 'fiber': 2, 'sugar': 40, 'sodium': 700, 'unit': 'stack'},
    ],
    'lunch': [
        {'name': 'Chicken salad', 'calories': 450, 'protein': 35, 'carbs': 20, 'fat': 25, 'fiber': 6, 'sugar': 5, 'sodium': 620, 'unit': 'bowl'},
        {'name': 'Tuna sandwich', 'calories': 480, 'protein': 30, 'carbs': 50, 'fat': 18, 'fiber': 4, 'sugar': 6, 'sodium': 800, 'unit': 'sandwich'},
        {'name': 'Vegetable soup with bread', 'calories': 320, 'protein': 12, 'carbs': 45, 'fat': 10, 'fiber': 8, 'sugar': 8, 'sodium': 900, 'unit': 'bowl'},
        {'name': 'Pasta with tomato sauce', 'calories': 520, 'protein': 15, 'carbs': 90, 'fat': 12, 'fiber': 5, 'sugar': 10, 'sodium': 650, 'unit': 'plate'},
        {'name': 'Burrito bowl', 'calories': 650, 'protein': 30, 'carbs': 80, 'fat': 25, 'fiber': 12, 'sugar': 5, 'sodium': 1100, 'unit': 'bowl'},
    ],
    'dinner': [
        {'name': 'Grilled salmon with vegetables', 'calories': 520, 'protein': 40, 'carbs': 20, 'fat': 30, 'fiber': 8, 'sugar': 5, 'sodium': 450, 'unit': 'plate'},
        {'name': 'Steak with potatoes', 'calories': 750, 'protein': 45, 'carbs': 45, 'fat': 40, 'fiber': 3, 'sugar': 2, 'sodium': 820, 'unit': 'plate'},
        {'name': 'Vegetable stir-fry with tofu', 'calories': 380, 'protein': 20, 'carbs': 40, 'fat': 18, 'fiber': 10, 'sugar': 8, 'sodium': 750, 'unit': 'plate'},
        {'name': 'Spaghetti with meatballs', 'calories': 680, 'protein': 35, 'carbs': 80, 'fat': 28, 'fiber': 6, 'sugar': 12, 'sodium': 950, 'unit': 'plate'},
        {'name': 'Roast chicken with rice', 'calories': 620, 'protein': 40, 'carbs': 60, 'fat': 25, 'fiber': 3, 'sugar': 2, 'sodium': 780, 'unit': 'plate'},
    ],
    'snack': [
        {'name': 'Apple', 'calories': 95, 'protein': 0.5, 'carbs': 25, 'fat': 0.3, 'fiber': 4, 'sugar': 19, 'sodium': 2, 'unit': 'piece'},
        {'name': 'Protein bar', 'calories': 220, 'protein': 20, 'carbs': 25, 'fat': 8, 'fiber': 2, 'sugar': 18, 'sodium': 150, 'unit': 'bar'},
        {'name': 'Nuts', 'calories': 180, 'protein': 6, 'carbs': 6, 'fat': 16, 'fiber': 3, 'sugar': 1, 'sodium': 0, 'unit': 'handful'},
        {'name': 'Yogurt', 'calories': 150, 'protein': 12, 'carbs': 15, 'fat': 4, 'fiber': 0, 'sugar': 12, 'sodium': 80, 'unit': 'cup'},
        {'name': 'Chips', 'calories': 250, 'protein': 3, 'carbs': 25, 'fat': 15, 'fiber': 1, 'sugar': 0.5, 'sodium': 300, 'unit': 'serving'},
    ],
}

# Define meal patterns
MEAL_PATTERNS = {
    'healthy': {
        'breakfast': [0, 2, 3],  # Index of healthy options
        'lunch': [0, 2],
        'dinner': [0, 2],
        'snack': [0, 2, 3],
        'meal_probability': {'breakfast': 0.95, 'lunch': 0.9, 'dinner': 0.95, 'snack': 0.7}
    },
    'average': {
        'breakfast': [0, 1, 2, 3],
        'lunch': [0, 1, 2, 3],
        'dinner': [0, 1, 2, 3, 4],
        'snack': [0, 1, 2, 3, 4],
        'meal_probability': {'breakfast': 0.85, 'lunch': 0.9, 'dinner': 0.9, 'snack': 0.8}
    },
    'unhealthy': {
        'breakfast': [1, 4],
        'lunch': [1, 3, 4],
        'dinner': [1, 3, 4],
        'snack': [1, 4],
        'meal_probability': {'breakfast': 0.7, 'lunch': 0.95, 'dinner': 0.98, 'snack': 0.9}
    }
}

def create_test_user():
    """Create a test user if it doesn't exist."""
    user = User.query.filter_by(username='demo').first()
    if not user:
        user = User(
            username='demo',
            email='demo@example.com',
            password_hash='pbkdf2:sha256:150000$7SLHA3gG$97b21e2ad90a5db14af790f16af8177fe6fff67f978280f284175094dcca8716'  # 'password'
        )
        db.session.add(user)
        db.session.commit()
        logger.info(f"Created test user: {user.username}")
    return user

def generate_nutrition_data(user_id, days=30, pattern='average'):
    """
    Generate realistic nutrition data for the specified number of days.
    
    Args:
        user_id (int): User ID to generate data for
        days (int): Number of days to generate data for
        pattern (str): Eating pattern ('healthy', 'average', 'unhealthy')
        
    Returns:
        list: List of generated HealthData objects
    """
    if pattern not in MEAL_PATTERNS:
        pattern = 'average'
    
    today = datetime.now().date()
    data_objects = []
    
    logger.info(f"Generating {days} days of nutrition data with {pattern} pattern")
    
    for day_offset in range(days):
        current_date = today - timedelta(days=day_offset)
        pattern_data = MEAL_PATTERNS[pattern]
        
        # Generate data for each meal type
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
            # Determine if this meal is consumed on this day
            if random.random() <= pattern_data['meal_probability'][meal_type]:
                # Choose a food option for this meal based on the pattern
                food_index = random.choice(pattern_data[meal_type])
                food = FOODS[meal_type][food_index]
                
                # Add some variation
                calories_variation = random.uniform(0.9, 1.1)  # +/- 10%
                
                # Create metadata for the meal
                metadata = {
                    'mealType': meal_type,
                    'foodName': food['name'],
                    'calories': round(food['calories'] * calories_variation, 1),
                    'protein': round(food['protein'] * calories_variation, 1),
                    'carbs': round(food['carbs'] * calories_variation, 1),
                    'fat': round(food['fat'] * calories_variation, 1),
                    'fiber': round(food['fiber'] * calories_variation, 1),
                    'sugar': round(food['sugar'] * calories_variation, 1),
                    'sodium': round(food['sodium'] * calories_variation, 1),
                    'unit': food['unit']
                }
                
                # Create the health data record
                # We'll use the 'calories' as the main value
                data = HealthData(
                    user_id=user_id,
                    data_type='nutrition',
                    date=current_date,
                    value=metadata['calories'],  # Store calories as the primary value
                    unit='kcal',
                    meta_data=str(metadata),  # Store detailed nutrition info in metadata
                    source='generated',
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                data_objects.append(data)
    
    return data_objects

def main():
    """Main function to generate test data."""
    parser = argparse.ArgumentParser(description='Generate nutrition test data')
    parser.add_argument('--days', type=int, default=30, help='Number of days to generate data for')
    parser.add_argument('--pattern', type=str, default='average', 
                        choices=['healthy', 'average', 'unhealthy'], 
                        help='Nutrition pattern to generate')
    parser.add_argument('--user-id', type=int, help='User ID to generate data for (default: create demo user)')
    parser.add_argument('--clear', action='store_true', help='Clear existing nutrition data before generating new data')
    
    args = parser.parse_args()
    
    with app.app_context():
        # Get or create user
        if args.user_id:
            user = User.query.get(args.user_id)
            if not user:
                logger.error(f"User with ID {args.user_id} not found")
                sys.exit(1)
        else:
            user = create_test_user()
        
        # Clear existing data if requested
        if args.clear:
            deleted = HealthData.query.filter_by(user_id=user.id, data_type='nutrition').delete()
            db.session.commit()
            logger.info(f"Cleared {deleted} existing nutrition records")
        
        # Generate and save the data
        data_objects = generate_nutrition_data(user.id, args.days, args.pattern)
        
        db.session.bulk_save_objects(data_objects)
        db.session.commit()
        
        logger.info(f"Generated and saved {len(data_objects)} nutrition records")

if __name__ == "__main__":
    main()