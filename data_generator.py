"""
Data Generator for Health AI System

This script generates realistic health data for testing and demonstration purposes.
It populates the database with user data, health metrics, and insights.
"""

import os
import random
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app import db
from models import User, HealthData, Insight

def create_test_user():
    """Create a test user if it doesn't exist."""
    # Check if the test user already exists
    test_user = User.query.filter_by(email='test@example.com').first()
    
    if not test_user:
        # Create a new test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123')
        )
        db.session.add(test_user)
        db.session.commit()
        print(f"Created test user with ID: {test_user.id}")
    else:
        print(f"Test user already exists with ID: {test_user.id}")
    
    return test_user

def generate_steps_data(user_id, days=30):
    """Generate realistic step count data for the specified number of days."""
    # Define a baseline daily step count
    baseline_steps = 8000
    
    # Calculate today's date and the starting date
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Create a trend (increasing, decreasing, or stable)
    trend_type = random.choice(['increasing', 'decreasing', 'stable'])
    if trend_type == 'increasing':
        slope = random.uniform(50, 150)  # steps per day
    elif trend_type == 'decreasing':
        slope = random.uniform(-150, -50)  # steps per day
    else:
        slope = 0
    
    # Generate step data with weekday/weekend patterns
    steps_data = []
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # Apply trend
        trend_adjustment = i * slope
        
        # Weekend effect (less steps on weekends)
        is_weekend = current_date.weekday() >= 5  # 5=Saturday, 6=Sunday
        weekend_factor = 0.7 if is_weekend else 1.0
        
        # Random daily variation
        daily_variation = random.normalvariate(0, 1500)
        
        # Calculate final step count
        steps = max(0, int((baseline_steps + trend_adjustment) * weekend_factor + daily_variation))
        
        # Create health data record
        health_data = HealthData(
            user_id=user_id,
            data_type='steps',
            date=current_date,
            value=steps,
            unit='steps',
            meta_data=json.dumps({'source': 'fitness_watch', 'active_minutes': int(steps / 20)}),
            source='fitness_watch'
        )
        steps_data.append(health_data)
    
    return steps_data

def generate_sleep_data(user_id, days=30):
    """Generate realistic sleep duration data for the specified number of days."""
    # Define a baseline daily sleep duration in hours
    baseline_sleep = 7.5
    
    # Calculate today's date and the starting date
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Create a trend
    trend_type = random.choice(['increasing', 'decreasing', 'stable'])
    if trend_type == 'increasing':
        slope = random.uniform(0.02, 0.05)  # hours per day
    elif trend_type == 'decreasing':
        slope = random.uniform(-0.05, -0.02)  # hours per day
    else:
        slope = 0
    
    # Generate sleep data with weekday/weekend patterns
    sleep_data = []
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # Apply trend
        trend_adjustment = i * slope
        
        # Weekend effect (more sleep on weekends)
        is_weekend = current_date.weekday() >= 5  # 5=Saturday, 6=Sunday
        weekend_factor = 1.2 if is_weekend else 1.0
        
        # Random daily variation
        daily_variation = random.normalvariate(0, 0.7)
        
        # Calculate final sleep duration
        sleep_duration = max(3, min(12, (baseline_sleep + trend_adjustment) * weekend_factor + daily_variation))
        
        # Create sleep records with deep, light, and REM sleep phases
        deep_sleep_pct = random.uniform(0.15, 0.25)
        rem_sleep_pct = random.uniform(0.2, 0.3)
        light_sleep_pct = 1 - deep_sleep_pct - rem_sleep_pct
        
        meta_data = {
            'deep_sleep': round(sleep_duration * deep_sleep_pct, 1),
            'light_sleep': round(sleep_duration * light_sleep_pct, 1),
            'rem_sleep': round(sleep_duration * rem_sleep_pct, 1),
            'sleep_quality': random.randint(60, 95),
            'times_awake': random.randint(0, 3)
        }
        
        # Create health data record
        health_data = HealthData(
            user_id=user_id,
            data_type='sleep',
            date=current_date,
            value=round(sleep_duration, 1),
            unit='hours',
            meta_data=json.dumps(meta_data),
            source='sleep_tracker'
        )
        sleep_data.append(health_data)
    
    return sleep_data

def generate_heart_rate_data(user_id, days=30):
    """Generate realistic heart rate data for the specified number of days."""
    # Define a baseline daily resting heart rate
    baseline_hr = 65
    
    # Calculate today's date and the starting date
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Create a trend
    trend_type = random.choice(['increasing', 'decreasing', 'stable'])
    if trend_type == 'increasing':
        slope = random.uniform(0.1, 0.3)  # bpm per day
    elif trend_type == 'decreasing':
        slope = random.uniform(-0.3, -0.1)  # bpm per day
    else:
        slope = 0
    
    # Generate heart rate data
    hr_data = []
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # Apply trend
        trend_adjustment = i * slope
        
        # Stress factor (some days have higher HR due to stress)
        stress_factor = random.choice([1.0, 1.0, 1.0, 1.0, 1.08])  # 20% chance of a "stressed" day
        
        # Random daily variation
        daily_variation = random.normalvariate(0, 3)
        
        # Calculate final resting heart rate
        resting_hr = max(45, min(100, (baseline_hr + trend_adjustment) * stress_factor + daily_variation))
        
        # Generate zone data
        meta_data = {
            'min_hr': int(resting_hr * 0.9),
            'max_hr': int(resting_hr * 1.7),
            'avg_hr': int(resting_hr * 1.2),
            'zones': {
                'rest': random.randint(600, 900),       # minutes in rest zone
                'moderate': random.randint(30, 120),    # minutes in moderate zone
                'intense': random.randint(0, 60)        # minutes in intense zone
            }
        }
        
        # Create health data record
        health_data = HealthData(
            user_id=user_id,
            data_type='heart_rate',
            date=current_date,
            value=round(resting_hr),
            unit='bpm',
            meta_data=json.dumps(meta_data),
            source='fitness_watch'
        )
        hr_data.append(health_data)
    
    return hr_data

def generate_insights(user_id, steps_data, sleep_data, hr_data):
    """Generate insights based on the health data."""
    insights = []
    
    # Step trend insights
    steps_values = [data.value for data in steps_data]
    avg_steps = sum(steps_values) / len(steps_values)
    step_goal = 10000
    
    if avg_steps >= step_goal * 0.9:
        insights.append(Insight(
            user_id=user_id,
            category='activity',
            title='Excellent Activity Level',
            description=f'Great job! You\'re consistently reaching your step goal of {step_goal} steps per day with an average of {avg_steps:.0f} steps.',
            severity=1,
            is_actionable=False,
            recommendation='Keep up the good work and maintain this excellent activity level.'
        ))
    elif avg_steps >= step_goal * 0.7:
        insights.append(Insight(
            user_id=user_id,
            category='activity',
            title='Good Activity Level',
            description=f'You\'re doing well with an average of {avg_steps:.0f} steps per day, which is {avg_steps/step_goal:.0%} of your {step_goal} step goal.',
            severity=2,
            is_actionable=True,
            recommendation='Try to increase your daily activity slightly to reach your goal more consistently.'
        ))
    elif avg_steps >= step_goal * 0.5:
        insights.append(Insight(
            user_id=user_id,
            category='activity',
            title='Moderate Activity Level',
            description=f'Your average of {avg_steps:.0f} steps per day is {avg_steps/step_goal:.0%} of your {step_goal} step goal.',
            severity=3,
            is_actionable=True,
            recommendation='Consider adding a daily walk or increasing your current activity to get closer to your goal.'
        ))
    else:
        insights.append(Insight(
            user_id=user_id,
            category='activity',
            title='Low Activity Level',
            description=f'Your average of {avg_steps:.0f} steps per day is significantly below your {step_goal} step goal.',
            severity=4,
            is_actionable=True,
            recommendation='Try to gradually increase your daily steps. Start with small goals like taking the stairs or parking further away.'
        ))
    
    # Sleep insights
    sleep_values = [data.value for data in sleep_data]
    avg_sleep = sum(sleep_values) / len(sleep_values)
    sleep_goal = 8
    
    if avg_sleep >= sleep_goal * 0.9:
        insights.append(Insight(
            user_id=user_id,
            category='sleep',
            title='Optimal Sleep Duration',
            description=f'You\'re consistently getting adequate sleep with an average of {avg_sleep:.1f} hours per night.',
            severity=1,
            is_actionable=False,
            recommendation='Maintain your excellent sleep schedule for optimal health benefits.'
        ))
    elif avg_sleep >= sleep_goal * 0.8:
        insights.append(Insight(
            user_id=user_id,
            category='sleep',
            title='Good Sleep Duration',
            description=f'You\'re getting an average of {avg_sleep:.1f} hours of sleep per night, which is close to your goal of {sleep_goal} hours.',
            severity=2,
            is_actionable=True,
            recommendation='Try to get to bed a little earlier to reach your optimal sleep duration more consistently.'
        ))
    else:
        insights.append(Insight(
            user_id=user_id,
            category='sleep',
            title='Insufficient Sleep',
            description=f'Your average of {avg_sleep:.1f} hours of sleep per night is below your goal of {sleep_goal} hours.',
            severity=3,
            is_actionable=True,
            recommendation='Chronic sleep deprivation can impact health. Try to gradually increase your sleep duration by going to bed earlier and creating a relaxing bedtime routine.'
        ))
    
    # Heart rate insights
    hr_values = [data.value for data in hr_data]
    avg_hr = sum(hr_values) / len(hr_values)
    
    if avg_hr < 60:
        insights.append(Insight(
            user_id=user_id,
            category='heart',
            title='Excellent Resting Heart Rate',
            description=f'Your average resting heart rate of {avg_hr:.0f} bpm indicates excellent cardiovascular fitness.',
            severity=1,
            is_actionable=False,
            recommendation='Continue your current fitness routine to maintain your excellent heart health.'
        ))
    elif avg_hr < 70:
        insights.append(Insight(
            user_id=user_id,
            category='heart',
            title='Good Resting Heart Rate',
            description=f'Your average resting heart rate of {avg_hr:.0f} bpm is within a healthy range.',
            severity=1,
            is_actionable=False,
            recommendation='Maintain your current level of cardiovascular fitness with regular exercise.'
        ))
    else:
        insights.append(Insight(
            user_id=user_id,
            category='heart',
            title='Elevated Resting Heart Rate',
            description=f'Your average resting heart rate of {avg_hr:.0f} bpm is slightly elevated.',
            severity=2,
            is_actionable=True,
            recommendation='Consider increasing your cardiovascular exercise and reducing stress to lower your resting heart rate.'
        ))
    
    # Cross-data insights
    if avg_sleep < sleep_goal * 0.8 and avg_hr > 70:
        insights.append(Insight(
            user_id=user_id,
            category='general',
            title='Sleep and Heart Rate Connection',
            description='Your lower sleep duration may be contributing to your elevated heart rate.',
            severity=3,
            is_actionable=True,
            recommendation='Focus on improving your sleep habits as better sleep can help lower your resting heart rate.'
        ))
    
    if avg_steps > step_goal * 0.8 and avg_hr < 65:
        insights.append(Insight(
            user_id=user_id,
            category='general',
            title='Activity Improving Heart Health',
            description='Your consistent physical activity is positively impacting your heart health as shown by your low resting heart rate.',
            severity=1,
            is_actionable=False,
            recommendation='Keep up your excellent activity levels to maintain your heart health.'
        ))
    
    return insights

def main():
    """Main function to generate test data."""
    print("Generating test data...")
    
    # Create test user
    user = create_test_user()
    
    # Clear existing data for the test user
    db.session.query(HealthData).filter_by(user_id=user.id).delete()
    db.session.query(Insight).filter_by(user_id=user.id).delete()
    db.session.commit()
    
    # Generate health data
    steps_data = generate_steps_data(user.id)
    sleep_data = generate_sleep_data(user.id)
    hr_data = generate_heart_rate_data(user.id)
    
    # Add data to database
    db.session.add_all(steps_data)
    db.session.add_all(sleep_data)
    db.session.add_all(hr_data)
    db.session.commit()
    
    print(f"Added {len(steps_data)} steps records")
    print(f"Added {len(sleep_data)} sleep records")
    print(f"Added {len(hr_data)} heart rate records")
    
    # Generate and add insights
    insights = generate_insights(user.id, steps_data, sleep_data, hr_data)
    db.session.add_all(insights)
    db.session.commit()
    
    print(f"Added {len(insights)} insights")
    print("Data generation complete!")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        main()