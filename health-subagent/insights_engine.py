"""
Insights Engine for generating health insights from processed data.
"""
import logging
from datetime import datetime, timedelta
import json
from processors.steps_processor import StepsProcessor
from processors.sleep_processor import SleepProcessor
from processors.heart_rate_processor import HeartRateProcessor

logger = logging.getLogger(__name__)

class InsightsEngine:
    """Engine for generating health insights from processed data."""
    
    def __init__(self, api_client):
        """
        Initialize the insights engine.
        
        Args:
            api_client (ApiClient): The API client for interacting with the backend.
        """
        self.api_client = api_client
        self.config = api_client.config
        
        # Initialize processors
        self.steps_processor = StepsProcessor(api_client)
        self.sleep_processor = SleepProcessor(api_client)
        self.heart_rate_processor = HeartRateProcessor(api_client)
    
    def generate_insights(self):
        """
        Generate health insights from processed data.
        """
        logger.info("Generating health insights...")
        
        # Process data from different sources
        steps_analysis = self.steps_processor.process()
        sleep_analysis = self.sleep_processor.process()
        heart_rate_analysis = self.heart_rate_processor.process()
        
        # Generate insights
        insights = []
        
        # Add steps insights
        if steps_analysis:
            steps_insights = self.generate_steps_insights(steps_analysis)
            insights.extend(steps_insights)
        
        # Add sleep insights
        if sleep_analysis:
            sleep_insights = self.generate_sleep_insights(sleep_analysis)
            insights.extend(sleep_insights)
        
        # Add heart rate insights
        if heart_rate_analysis:
            hr_insights = self.generate_heart_rate_insights(heart_rate_analysis)
            insights.extend(hr_insights)
        
        # Add cross-data insights
        if steps_analysis and sleep_analysis:
            cross_insights = self.generate_cross_data_insights(steps_analysis, sleep_analysis, heart_rate_analysis)
            insights.extend(cross_insights)
        
        # Save insights to the backend
        saved_count = 0
        for insight in insights:
            result = self.api_client.create_insight(insight)
            if result:
                saved_count += 1
        
        logger.info(f"Generated and saved {saved_count} insights out of {len(insights)}")
        
        return insights
    
    def generate_steps_insights(self, steps_analysis):
        """
        Generate insights from steps data analysis.
        
        Args:
            steps_analysis (dict): The steps data analysis.
            
        Returns:
            list: A list of insights.
        """
        insights = []
        
        if not steps_analysis or 'trend_analysis' not in steps_analysis:
            return insights
        
        # Activity level insight
        trend = steps_analysis['trend_analysis']
        if trend['data_points'] >= self.config.min_data_points:
            avg_steps = trend['average']
            step_goal = self.config.step_goal
            
            if avg_steps is not None:
                achievement_rate = steps_analysis.get('goal_achievement_rate', 0)
                
                if achievement_rate >= 0.9:  # 90% or more of goal
                    insights.append({
                        'category': 'activity',
                        'title': 'Excellent Activity Level',
                        'description': f'Great job! You\'re consistently reaching your step goal of {step_goal} steps per day with an average of {avg_steps:.0f} steps.',
                        'severity': 1,
                        'isActionable': False,
                        'recommendation': 'Keep up the good work and maintain this excellent activity level.'
                    })
                elif achievement_rate >= 0.7:  # 70-90% of goal
                    insights.append({
                        'category': 'activity',
                        'title': 'Good Activity Level',
                        'description': f'You\'re doing well with an average of {avg_steps:.0f} steps per day, which is {achievement_rate:.0%} of your {step_goal} step goal.',
                        'severity': 2,
                        'isActionable': True,
                        'recommendation': 'Try to increase your daily activity slightly to reach your goal more consistently.'
                    })
                elif achievement_rate >= 0.5:  # 50-70% of goal
                    insights.append({
                        'category': 'activity',
                        'title': 'Moderate Activity Level',
                        'description': f'Your average of {avg_steps:.0f} steps per day is {achievement_rate:.0%} of your {step_goal} step goal.',
                        'severity': 3,
                        'isActionable': True,
                        'recommendation': 'Consider adding a daily walk or increasing your current activity to get closer to your goal.'
                    })
                else:  # Less than 50% of goal
                    insights.append({
                        'category': 'activity',
                        'title': 'Low Activity Level',
                        'description': f'Your average of {avg_steps:.0f} steps per day is significantly below your {step_goal} step goal.',
                        'severity': 4,
                        'isActionable': True,
                        'recommendation': 'Try to gradually increase your daily steps. Start with small goals like taking the stairs or parking further away.'
                    })
        
        # Activity trend insight
        if trend['trend'] == 'increasing':
            insights.append({
                'category': 'activity',
                'title': 'Increasing Activity Trend',
                'description': 'Your daily step count is showing an upward trend. Keep up the good work!',
                'severity': 1,
                'isActionable': False,
                'recommendation': 'Continue this positive trend by maintaining or gradually increasing your activity level.'
            })
        elif trend['trend'] == 'decreasing':
            insights.append({
                'category': 'activity',
                'title': 'Decreasing Activity Trend',
                'description': 'Your daily step count has been decreasing over time.',
                'severity': 3,
                'isActionable': True,
                'recommendation': 'Try to identify what's changed in your routine and find opportunities to add more steps to your day.'
            })
        
        # Unusual days insight
        unusual_days = steps_analysis.get('unusual_days', [])
        if unusual_days:
            high_days = [day for day in unusual_days if day['direction'] == 'high']
            low_days = [day for day in unusual_days if day['direction'] == 'low']
            
            if high_days:
                dates = ', '.join([day['date'] for day in high_days[:3]])
                insights.append({
                    'category': 'activity',
                    'title': 'Unusually Active Days',
                    'description': f'You had unusually high activity on: {dates}.' + 
                                   (f' (and {len(high_days)-3} more days)' if len(high_days) > 3 else ''),
                    'severity': 1,
                    'isActionable': False,
                    'recommendation': 'These are your most active days. What made these days different? Try to incorporate those activities more often.'
                })
            
            if low_days:
                dates = ', '.join([day['date'] for day in low_days[:3]])
                insights.append({
                    'category': 'activity',
                    'title': 'Unusually Inactive Days',
                    'description': f'You had unusually low activity on: {dates}.' + 
                                   (f' (and {len(low_days)-3} more days)' if len(low_days) > 3 else ''),
                    'severity': 2,
                    'isActionable': True,
                    'recommendation': 'Try to identify what prevented you from being active on these days and plan accordingly in the future.'
                })
        
        return insights
    
    def generate_sleep_insights(self, sleep_analysis):
        """
        Generate insights from sleep data analysis.
        
        Args:
            sleep_analysis (dict): The sleep data analysis.
            
        Returns:
            list: A list of insights.
        """
        insights = []
        
        if not sleep_analysis or 'trend_analysis' not in sleep_analysis:
            return insights
        
        # Sleep duration insight
        trend = sleep_analysis['trend_analysis']
        if trend['data_points'] >= self.config.min_data_points:
            avg_sleep = trend['average']
            sleep_goal = self.config.sleep_goal_hours
            
            if avg_sleep is not None:
                achievement_rate = sleep_analysis.get('goal_achievement_rate', 0)
                
                if achievement_rate >= 0.9:  # 90% or more of goal
                    insights.append({
                        'category': 'sleep',
                        'title': 'Optimal Sleep Duration',
                        'description': f'You\'re consistently getting adequate sleep with an average of {avg_sleep:.1f} hours per night.',
                        'severity': 1,
                        'isActionable': False,
                        'recommendation': 'Maintain your excellent sleep schedule for optimal health benefits.'
                    })
                elif achievement_rate >= 0.8:  # 80-90% of goal
                    insights.append({
                        'category': 'sleep',
                        'title': 'Good Sleep Duration',
                        'description': f'You\'re getting an average of {avg_sleep:.1f} hours of sleep per night, which is close to your goal of {sleep_goal} hours.',
                        'severity': 2,
                        'isActionable': True,
                        'recommendation': 'Try to get to bed a little earlier to reach your optimal sleep duration more consistently.'
                    })
                elif achievement_rate >= 0.7:  # 70-80% of goal
                    insights.append({
                        'category': 'sleep',
                        'title': 'Slightly Insufficient Sleep',
                        'description': f'Your average of {avg_sleep:.1f} hours of sleep per night is below your goal of {sleep_goal} hours.',
                        'severity': 3,
                        'isActionable': True,
                        'recommendation': 'Prioritize sleep by establishing a consistent bedtime routine and aiming for an earlier bedtime.'
                    })
                else:  # Less than 70% of goal
                    insights.append({
                        'category': 'sleep',
                        'title': 'Insufficient Sleep',
                        'description': f'Your average of {avg_sleep:.1f} hours of sleep per night is significantly below your goal of {sleep_goal} hours.',
                        'severity': 4,
                        'isActionable': True,
                        'recommendation': 'Chronic sleep deprivation can impact health. Try to gradually increase your sleep duration by going to bed earlier and creating a relaxing bedtime routine.'
                    })
        
        # Sleep consistency insight
        consistency = sleep_analysis.get('sleep_consistency', {})
        if consistency and consistency.get('consistency') != 'insufficient_data':
            if consistency['consistency'] == 'very_consistent':
                insights.append({
                    'category': 'sleep',
                    'title': 'Excellent Sleep Consistency',
                    'description': 'Your sleep schedule is very consistent, with minimal variation in sleep duration from day to day.',
                    'severity': 1,
                    'isActionable': False,
                    'recommendation': 'A consistent sleep schedule helps optimize your body\'s circadian rhythm. Keep up the good work!'
                })
            elif consistency['consistency'] == 'consistent':
                insights.append({
                    'category': 'sleep',
                    'title': 'Good Sleep Consistency',
                    'description': 'Your sleep schedule is fairly consistent, with moderate variation in sleep duration.',
                    'severity': 2,
                    'isActionable': True,
                    'recommendation': 'Try to maintain consistent sleep and wake times, even on weekends, for optimal sleep quality.'
                })
            elif consistency['consistency'] == 'moderately_consistent':
                insights.append({
                    'category': 'sleep',
                    'title': 'Moderate Sleep Consistency',
                    'description': 'Your sleep duration varies moderately from day to day.',
                    'severity': 3,
                    'isActionable': True,
                    'recommendation': 'Work on establishing a more consistent sleep schedule. Try to go to bed and wake up at similar times each day.'
                })
            else:  # inconsistent
                insights.append({
                    'category': 'sleep',
                    'title': 'Inconsistent Sleep Pattern',
                    'description': 'Your sleep duration varies significantly from day to day, which can disrupt your body\'s natural rhythm.',
                    'severity': 4,
                    'isActionable': True,
                    'recommendation': 'Irregular sleep patterns can affect sleep quality and overall health. Try to establish a consistent sleep schedule, even on weekends.'
                })
        
        # Sleep trend insight
        if trend['trend'] == 'increasing':
            insights.append({
                'category': 'sleep',
                'title': 'Improving Sleep Duration',
                'description': 'Your sleep duration is showing an upward trend. This is a positive change for your health.',
                'severity': 1,
                'isActionable': False,
                'recommendation': 'Continue this positive trend by maintaining your good sleep habits.'
            })
        elif trend['trend'] == 'decreasing':
            insights.append({
                'category': 'sleep',
                'title': 'Decreasing Sleep Duration',
                'description': 'Your sleep duration has been decreasing over time, which may affect your health and performance.',
                'severity': 3,
                'isActionable': True,
                'recommendation': 'Try to identify what's affecting your sleep duration and prioritize getting adequate rest.'
            })
        
        return insights
    
    def generate_heart_rate_insights(self, hr_analysis):
        """
        Generate insights from heart rate data analysis.
        
        Args:
            hr_analysis (dict): The heart rate data analysis.
            
        Returns:
            list: A list of insights.
        """
        insights = []
        
        if not hr_analysis or 'resting_heart_rate' not in hr_analysis:
            return insights
        
        # Resting heart rate insight
        resting_hr = hr_analysis['resting_heart_rate']
        if resting_hr.get('average') is not None:
            avg_rhr = resting_hr['average']
            
            if resting_hr.get('is_elevated', False):
                insights.append({
                    'category': 'heart_health',
                    'title': 'Elevated Resting Heart Rate',
                    'description': f'Your average resting heart rate of {avg_rhr:.0f} bpm is above the threshold of {resting_hr["threshold"]} bpm.',
                    'severity': 3,
                    'isActionable': True,
                    'recommendation': 'An elevated resting heart rate can be a sign of stress or reduced fitness. Consider increasing physical activity, reducing stress, and ensuring adequate hydration.'
                })
            else:
                insights.append({
                    'category': 'heart_health',
                    'title': 'Healthy Resting Heart Rate',
                    'description': f'Your average resting heart rate of {avg_rhr:.0f} bpm is within a healthy range.',
                    'severity': 1,
                    'isActionable': False,
                    'recommendation': 'Continue maintaining your cardiovascular health through regular exercise and stress management.'
                })
        
        # Heart rate trend insight
        rhr_trend = resting_hr.get('trend')
        if rhr_trend == 'increasing':
            insights.append({
                'category': 'heart_health',
                'title': 'Increasing Resting Heart Rate',
                'description': 'Your resting heart rate has been trending upward, which may indicate changes in your cardiovascular health or stress levels.',
                'severity': 3,
                'isActionable': True,
                'recommendation': 'Monitor this trend. Consider factors like stress, sleep quality, and physical activity that might be affecting your heart rate.'
            })
        elif rhr_trend == 'decreasing':
            insights.append({
                'category': 'heart_health',
                'title': 'Decreasing Resting Heart Rate',
                'description': 'Your resting heart rate has been trending downward, which is often a sign of improving cardiovascular fitness.',
                'severity': 1,
                'isActionable': False,
                'recommendation': 'Continue your healthy habits that are contributing to this positive trend.'
            })
        
        # Heart rate zones insight
        hr_zones = hr_analysis.get('heart_rate_zones', {})
        if hr_zones and hr_zones.get('percentages'):
            percentages = hr_zones['percentages']
            
            # Check if user is getting any cardiovascular exercise
            moderate_plus = percentages.get('moderate', 0) + percentages.get('vigorous', 0) + percentages.get('max', 0)
            
            if moderate_plus > 5:  # More than 5% of readings in moderate or higher zones
                insights.append({
                    'category': 'heart_health',
                    'title': 'Good Cardiovascular Exercise',
                    'description': f'You\'re spending {moderate_plus:.1f}% of your time in moderate to high intensity heart rate zones, which is good for cardiovascular health.',
                    'severity': 1,
                    'isActionable': False,
                    'recommendation': 'Continue incorporating cardiovascular exercise into your routine for heart health benefits.'
                })
            else:
                insights.append({
                    'category': 'heart_health',
                    'title': 'Limited Cardiovascular Exercise',
                    'description': 'You\'re spending very little time in moderate to high intensity heart rate zones.',
                    'severity': 3,
                    'isActionable': True,
                    'recommendation': 'Try to incorporate more cardiovascular exercise into your routine, aiming for at least 150 minutes of moderate activity per week.'
                })
        
        return insights
    
    def generate_cross_data_insights(self, steps_analysis, sleep_analysis, hr_analysis):
        """
        Generate insights by analyzing relationships between different health metrics.
        
        Args:
            steps_analysis (dict): The steps data analysis.
            sleep_analysis (dict): The sleep data analysis.
            hr_analysis (dict): The heart rate data analysis.
            
        Returns:
            list: A list of insights.
        """
        insights = []
        
        if not steps_analysis or not sleep_analysis:
            return insights
        
        # Check if activity level correlates with sleep quality
        steps_achievement = steps_analysis.get('goal_achievement_rate', 0)
        sleep_achievement = sleep_analysis.get('goal_achievement_rate', 0)
        
        # Both activity and sleep are good
        if steps_achievement >= 0.8 and sleep_achievement >= 0.8:
            insights.append({
                'category': 'lifestyle',
                'title': 'Balanced Activity and Sleep',
                'description': 'You\'re maintaining a good balance of physical activity and sleep, which is optimal for overall health.',
                'severity': 1,
                'isActionable': False,
                'recommendation': 'Continue this balanced approach to activity and rest for optimal health benefits.'
            })
        
        # Good activity but poor sleep
        elif steps_achievement >= 0.8 and sleep_achievement < 0.7:
            insights.append({
                'category': 'lifestyle',
                'title': 'Active but Undersleeping',
                'description': 'While you\'re maintaining good activity levels, you\'re not getting enough sleep to fully recover.',
                'severity': 3,
                'isActionable': True,
                'recommendation': 'Physical activity is important, but adequate sleep is essential for recovery and overall health. Try to prioritize sleep alongside your activity.'
            })
        
        # Poor activity but good sleep
        elif steps_achievement < 0.7 and sleep_achievement >= 0.8:
            insights.append({
                'category': 'lifestyle',
                'title': 'Well-Rested but Inactive',
                'description': 'You\'re getting good sleep, but your activity level is lower than recommended for optimal health.',
                'severity': 2,
                'isActionable': True,
                'recommendation': 'Your good sleep habits will help you have energy for increased activity. Try to gradually increase your daily movement.'
            })
        
        # Both activity and sleep are poor
        elif steps_achievement < 0.7 and sleep_achievement < 0.7:
            insights.append({
                'category': 'lifestyle',
                'title': 'Low Activity and Sleep',
                'description': 'Both your activity level and sleep duration are below recommended levels, which can impact your overall health.',
                'severity': 4,
                'isActionable': True,
                'recommendation': 'Consider which is easier to address first - sleep or activity. Improving one often makes it easier to improve the other.'
            })
        
        # Heart rate and activity correlation
        if hr_analysis and 'resting_heart_rate' in hr_analysis:
            rhr = hr_analysis['resting_heart_rate']
            if rhr.get('average') is not None and steps_achievement < 0.6 and rhr.get('is_elevated', False):
                insights.append({
                    'category': 'heart_health',
                    'title': 'Elevated Heart Rate with Low Activity',
                    'description': 'Your elevated resting heart rate combined with low physical activity may indicate opportunities to improve cardiovascular health.',
                    'severity': 3,
                    'isActionable': True,
                    'recommendation': 'Regular physical activity can help lower resting heart rate and improve cardiovascular health. Start with small, achievable increases in daily activity.'
                })
        
        return insights
