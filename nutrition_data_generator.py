"""
Nutrition Data Generator for Health AI System

This script generates realistic nutrition data for testing and demonstration purposes.
It populates the database with nutritional meal records for users.
"""
import random
import logging
from datetime import datetime, timedelta

from app import db
from models import HealthData, User
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_user():
    """Create a test user if it doesn't exist."""
    username = "testuser"
    user = User.query.filter_by(username=username).first()
    
    if not user:
        logger.info(f"Creating test user: {username}")
        user = User(
            username=username,
            email="testuser@example.com",
            password_hash=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()
        logger.info(f"Created test user with ID: {user.id}")
    else:
        logger.info(f"Test user already exists with ID: {user.id}")
    
    return user.id

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
    logger.info(f"Generating {days} days of nutrition data for user {user_id} with pattern '{pattern}'")
    
    # Define common foods by meal type with nutrition info
    foods = {
        'breakfast': [
            {'name': 'Oatmeal with berries', 'calories': 350, 'protein': 10, 'carbs': 60, 'fat': 7, 'fiber': 8, 'sugar': 10},
            {'name': 'Scrambled eggs with toast', 'calories': 420, 'protein': 20, 'carbs': 30, 'fat': 22, 'fiber': 2, 'sugar': 3},
            {'name': 'Yogurt with granola', 'calories': 300, 'protein': 15, 'carbs': 45, 'fat': 8, 'fiber': 4, 'sugar': 20},
            {'name': 'Smoothie bowl', 'calories': 380, 'protein': 8, 'carbs': 70, 'fat': 6, 'fiber': 6, 'sugar': 25},
            {'name': 'Avocado toast', 'calories': 350, 'protein': 10, 'carbs': 35, 'fat': 18, 'fiber': 7, 'sugar': 2},
            {'name': 'Cereal with milk', 'calories': 280, 'protein': 8, 'carbs': 50, 'fat': 5, 'fiber': 3, 'sugar': 15},
            {'name': 'Protein pancakes', 'calories': 450, 'protein': 25, 'carbs': 55, 'fat': 12, 'fiber': 5, 'sugar': 12},
            {'name': 'Skipped breakfast', 'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0, 'sugar': 0}
        ],
        'lunch': [
            {'name': 'Grilled chicken salad', 'calories': 420, 'protein': 35, 'carbs': 20, 'fat': 22, 'fiber': 5, 'sugar': 4},
            {'name': 'Turkey sandwich', 'calories': 450, 'protein': 25, 'carbs': 50, 'fat': 15, 'fiber': 4, 'sugar': 6},
            {'name': 'Vegetable soup with bread', 'calories': 380, 'protein': 12, 'carbs': 60, 'fat': 8, 'fiber': 8, 'sugar': 10},
            {'name': 'Quinoa bowl', 'calories': 520, 'protein': 15, 'carbs': 80, 'fat': 15, 'fiber': 10, 'sugar': 8},
            {'name': 'Tuna wrap', 'calories': 410, 'protein': 30, 'carbs': 40, 'fat': 14, 'fiber': 6, 'sugar': 5},
            {'name': 'Caesar salad', 'calories': 450, 'protein': 20, 'carbs': 15, 'fat': 35, 'fiber': 3, 'sugar': 2},
            {'name': 'Rice bowl with vegetables', 'calories': 480, 'protein': 12, 'carbs': 85, 'fat': 10, 'fiber': 7, 'sugar': 6},
            {'name': 'Fast food burger', 'calories': 700, 'protein': 25, 'carbs': 60, 'fat': 40, 'fiber': 2, 'sugar': 12},
            {'name': 'Skipped lunch', 'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0, 'sugar': 0}
        ],
        'dinner': [
            {'name': 'Grilled salmon with vegetables', 'calories': 520, 'protein': 40, 'carbs': 25, 'fat': 28, 'fiber': 6, 'sugar': 5},
            {'name': 'Pasta with tomato sauce', 'calories': 580, 'protein': 15, 'carbs': 90, 'fat': 15, 'fiber': 6, 'sugar': 8},
            {'name': 'Stir-fry with rice', 'calories': 650, 'protein': 25, 'carbs': 85, 'fat': 20, 'fiber': 7, 'sugar': 6},
            {'name': 'Baked chicken with potatoes', 'calories': 620, 'protein': 45, 'carbs': 50, 'fat': 25, 'fiber': 4, 'sugar': 3},
            {'name': 'Vegetable curry', 'calories': 580, 'protein': 18, 'carbs': 70, 'fat': 22, 'fiber': 12, 'sugar': 10},
            {'name': 'Burrito bowl', 'calories': 750, 'protein': 30, 'carbs': 90, 'fat': 30, 'fiber': 15, 'sugar': 5},
            {'name': 'Pizza', 'calories': 800, 'protein': 35, 'carbs': 90, 'fat': 35, 'fiber': 4, 'sugar': 8},
            {'name': 'Takeout Chinese food', 'calories': 850, 'protein': 30, 'carbs': 100, 'fat': 35, 'fiber': 5, 'sugar': 20},
            {'name': 'Skipped dinner', 'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0, 'sugar': 0}
        ],
        'snack': [
            {'name': 'Apple with peanut butter', 'calories': 220, 'protein': 7, 'carbs': 30, 'fat': 10, 'fiber': 5, 'sugar': 20},
            {'name': 'Greek yogurt', 'calories': 150, 'protein': 15, 'carbs': 10, 'fat': 4, 'fiber': 0, 'sugar': 6},
            {'name': 'Protein bar', 'calories': 230, 'protein': 20, 'carbs': 25, 'fat': 8, 'fiber': 3, 'sugar': 15},
            {'name': 'Mixed nuts', 'calories': 270, 'protein': 10, 'carbs': 12, 'fat': 22, 'fiber': 4, 'sugar': 2},
            {'name': 'Fruit smoothie', 'calories': 200, 'protein': 5, 'carbs': 45, 'fat': 0, 'fiber': 3, 'sugar': 35},
            {'name': 'Dark chocolate', 'calories': 180, 'protein': 2, 'carbs': 20, 'fat': 12, 'fiber': 3, 'sugar': 18},
            {'name': 'Chips', 'calories': 250, 'protein': 3, 'carbs': 30, 'fat': 13, 'fiber': 1, 'sugar': 1},
            {'name': 'Ice cream', 'calories': 300, 'protein': 5, 'carbs': 40, 'fat': 15, 'fiber': 0, 'sugar': 35},
            {'name': 'No snack', 'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0, 'sugar': 0}
        ]
    }
    
    # Modify food selection probabilities based on eating pattern
    if pattern == 'healthy':
        # Higher probability of healthy foods, lower probability of unhealthy foods
        breakfast_weights = [25, 20, 20, 15, 15, 5, 0, 0]  # Skipped breakfast is rare
        lunch_weights = [25, 20, 20, 15, 10, 5, 5, 0, 0]    # Fast food is never chosen, skipping is rare
        dinner_weights = [25, 15, 20, 20, 15, 5, 0, 0, 0]   # Pizza and takeout are never chosen, skipping is rare
        snack_weights = [20, 25, 20, 20, 10, 5, 0, 0, 0]    # Chips and ice cream are never chosen
    elif pattern == 'unhealthy':
        # Higher probability of unhealthy foods, lower probability of healthy foods
        breakfast_weights = [5, 10, 5, 5, 5, 25, 20, 25]    # Higher chance of cereal, skipping, or protein pancakes
        lunch_weights = [5, 10, 5, 5, 10, 15, 15, 25, 10]   # Higher chance of fast food
        dinner_weights = [5, 10, 10, 10, 5, 10, 25, 20, 5]  # Higher chance of pizza and takeout
        snack_weights = [5, 5, 10, 5, 5, 15, 30, 25, 0]     # Higher chance of chips and ice cream
    else:  # 'average'
        # Balanced probabilities
        breakfast_weights = [15, 15, 15, 10, 10, 15, 10, 10]
        lunch_weights = [15, 15, 10, 10, 15, 10, 10, 10, 5]
        dinner_weights = [15, 15, 15, 15, 10, 10, 10, 5, 5]
        snack_weights = [15, 15, 15, 15, 10, 10, 10, 10, 0]
    
    meal_weights = {
        'breakfast': breakfast_weights,
        'lunch': lunch_weights,
        'dinner': dinner_weights,
        'snack': snack_weights
    }
    
    # Set probability of having each meal type based on pattern
    if pattern == 'healthy':
        meal_probs = {'breakfast': 0.95, 'lunch': 0.95, 'dinner': 0.95, 'snack': 0.7}
    elif pattern == 'unhealthy':
        meal_probs = {'breakfast': 0.7, 'lunch': 0.8, 'dinner': 0.9, 'snack': 0.9}
    else:  # 'average'
        meal_probs = {'breakfast': 0.85, 'lunch': 0.9, 'dinner': 0.95, 'snack': 0.8}
    
    # Generate data for each day
    health_data_records = []
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        
        # Each day may have all 4 meal types (breakfast, lunch, dinner, snack)
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
            # Determine if user had this meal today
            if random.random() < meal_probs[meal_type]:
                # Select a food for this meal based on pattern weights
                food_idx = random.choices(
                    range(len(foods[meal_type])), 
                    weights=meal_weights[meal_type][:len(foods[meal_type])], 
                    k=1
                )[0]
                food = foods[meal_type][food_idx]
                
                # Skip if "No meal" was selected
                if food['calories'] == 0:
                    continue
                
                # Add some randomness to the nutritional values
                variation = random.uniform(0.8, 1.2)  # 20% variation
                calories = round(food['calories'] * variation)
                
                # Create metadata dictionary with nutritional info
                meta_data = {
                    'mealType': meal_type,
                    'foodName': food['name'],
                    'calories': calories,
                    'protein': round(food['protein'] * variation, 1),
                    'carbs': round(food['carbs'] * variation, 1),
                    'fat': round(food['fat'] * variation, 1),
                    'fiber': round(food['fiber'] * variation, 1),
                    'sugar': round(food['sugar'] * variation, 1),
                    'sodium': round(random.uniform(100, 500) * variation, 1),
                    'unit': 'serving'
                }
                
                # Create the HealthData record
                health_data = HealthData(
                    user_id=user_id,
                    data_type='nutrition',
                    date=current_date,
                    value=calories,  # Use calories as the main value
                    unit='kcal',
                    meta_data=str(meta_data),
                    source='data_generator',
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                health_data_records.append(health_data)
    
    # Save all records to the database
    if health_data_records:
        db.session.add_all(health_data_records)
        db.session.commit()
        logger.info(f"Generated {len(health_data_records)} nutrition records for user {user_id}")
    
    return health_data_records

def main():
    """Main function to generate test data."""
    user_id = create_test_user()
    
    # Generate nutrition data for different eating patterns
    # Use 'healthy', 'average', or 'unhealthy'
    pattern = 'average'
    generate_nutrition_data(user_id, days=30, pattern=pattern)
    
    logger.info("Nutrition data generation complete")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        main()