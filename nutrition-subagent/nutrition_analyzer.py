"""
Nutrition Data Analyzer

This module provides specialized analysis for nutrition data.
It includes calorie tracking, macronutrient analysis, and meal pattern detection.
"""
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from typing import List, Dict, Any, Optional

# Import directly instead of using relative imports
# These are imported by the nutrition_agent_runner using the custom import mechanism
import sys
import os
from pathlib import Path

# Add parent directory to path to allow absolute imports
module_dir = Path(__file__).parent
if str(module_dir) not in sys.path:
    sys.path.append(str(module_dir))

# Now import the classes
from models import (
    NutritionData, 
    DailyNutritionSummary, 
    NutrientIntakeTrend, 
    MealPatternAnalysis, 
    NutritionAnalysis
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutritionAnalyzer:
    """Analyzer for nutrition data metrics."""
    
    # Reference values based on a 2000 calorie diet (these could be personalized)
    REFERENCE_VALUES = {
        "calories": 2000,
        "protein": 50,  # g
        "carbs": 275,  # g
        "fat": 78,  # g
        "fiber": 28,  # g
        "sugar": 50,  # g
        "sodium": 2300  # mg
    }
    
    MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]
    
    def __init__(self):
        """Initialize the nutrition analyzer."""
        logger.info("Initializing NutritionAnalyzer")
    
    def _convert_to_dataframe(self, nutrition_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert nutrition data list to pandas DataFrame.
        
        Args:
            nutrition_data (list): List of nutrition data dictionaries
            
        Returns:
            pd.DataFrame: DataFrame with formatted data
        """
        try:
            df = pd.DataFrame(nutrition_data)
            
            # Convert string dates to datetime objects
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            return df
        except Exception as e:
            logger.error(f"Error converting nutrition data to DataFrame: {str(e)}")
            # Return empty DataFrame with expected columns if conversion fails
            return pd.DataFrame(columns=['date', 'mealType', 'foodName', 'calories', 'protein', 'carbs', 'fat'])
    
    def _aggregate_daily_nutrition(self, df: pd.DataFrame) -> Dict[str, DailyNutritionSummary]:
        """
        Aggregate nutrition data to daily summaries.
        
        Args:
            df (pd.DataFrame): DataFrame with nutrition data
            
        Returns:
            Dict[str, DailyNutritionSummary]: Dictionary of daily summaries indexed by date string
        """
        if df.empty:
            logger.warning("No data to aggregate for daily nutrition")
            return {}
        
        try:
            # Group by date and calculate sums for main nutrients
            daily_sums = df.groupby(df['date'].dt.date).agg({
                'calories': 'sum',
                'protein': 'sum',
                'carbs': 'sum',
                'fat': 'sum',
                'fiber': 'sum',
                'sugar': 'sum',
                'sodium': 'sum'
            }).fillna(0).to_dict(orient='index')
            
            # Create meal breakdowns
            daily_summaries = {}
            
            for date, nutrients in daily_sums.items():
                date_str = date.isoformat()
                
                # Get data for this date only
                date_df = df[df['date'].dt.date == date]
                
                # Calculate meal breakdown
                meal_breakdown = {}
                for meal_type in self.MEAL_TYPES:
                    meal_data = date_df[date_df['mealType'] == meal_type]
                    if not meal_data.empty:
                        meal_breakdown[meal_type] = {
                            'calories': meal_data['calories'].sum(),
                            'protein': meal_data['protein'].sum(),
                            'carbs': meal_data['carbs'].sum(),
                            'fat': meal_data['fat'].sum()
                        }
                
                # Calculate macronutrient percentages
                total_calories = nutrients['calories']
                if total_calories > 0:
                    # Macronutrient calories: protein=4kcal/g, carbs=4kcal/g, fat=9kcal/g
                    protein_calories = nutrients['protein'] * 4
                    carb_calories = nutrients['carbs'] * 4
                    fat_calories = nutrients['fat'] * 9
                    
                    nutrient_percentages = {
                        'protein': (protein_calories / total_calories) * 100 if protein_calories > 0 else 0,
                        'carbs': (carb_calories / total_calories) * 100 if carb_calories > 0 else 0,
                        'fat': (fat_calories / total_calories) * 100 if fat_calories > 0 else 0
                    }
                else:
                    nutrient_percentages = {'protein': 0, 'carbs': 0, 'fat': 0}
                
                # Create daily summary
                daily_summaries[date_str] = DailyNutritionSummary(
                    date=date,
                    totalCalories=nutrients['calories'],
                    totalProtein=nutrients['protein'],
                    totalCarbs=nutrients['carbs'],
                    totalFat=nutrients['fat'],
                    totalFiber=nutrients.get('fiber', 0),
                    totalSugar=nutrients.get('sugar', 0),
                    totalSodium=nutrients.get('sodium', 0),
                    mealBreakdown=meal_breakdown,
                    nutrientPercentages=nutrient_percentages
                )
            
            return daily_summaries
        
        except Exception as e:
            logger.error(f"Error aggregating daily nutrition: {str(e)}")
            return {}
    
    def analyze_nutrient_trends(self, nutrition_data: List[Dict[str, Any]]) -> Dict[str, NutrientIntakeTrend]:
        """
        Analyze trends in nutrient intake over time.
        
        Args:
            nutrition_data (list): List of nutrition data dictionaries
            
        Returns:
            Dict[str, NutrientIntakeTrend]: Dictionary of trends for each nutrient
        """
        df = self._convert_to_dataframe(nutrition_data)
        if df.empty:
            logger.warning("No data to analyze for nutrient trends")
            return {}
        
        try:
            # Get daily summaries
            daily_summaries = self._aggregate_daily_nutrition(df)
            if not daily_summaries:
                return {}
            
            # Convert to DataFrame for trend analysis
            summary_df = pd.DataFrame([
                {
                    'date': datetime.fromisoformat(date_str),
                    'calories': summary.totalCalories,
                    'protein': summary.totalProtein,
                    'carbs': summary.totalCarbs,
                    'fat': summary.totalFat,
                    'fiber': summary.totalFiber or 0,
                    'sugar': summary.totalSugar or 0,
                    'sodium': summary.totalSodium or 0
                }
                for date_str, summary in daily_summaries.items()
            ])
            
            summary_df = summary_df.sort_values('date')
            
            # Analyze trends for each nutrient
            nutrient_trends = {}
            nutrients = ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']
            
            for nutrient in nutrients:
                if nutrient not in summary_df.columns:
                    continue
                
                values = summary_df[nutrient].dropna()
                if len(values) < 3:  # Need at least 3 points for a trend
                    continue
                
                # Calculate basic statistics
                avg_value = values.mean()
                min_value = values.min()
                max_value = values.max()
                
                # Determine trend direction
                if len(values) >= 5:
                    # Use linear regression to determine trend
                    x = np.arange(len(values))
                    y = values.values
                    slope, _ = np.polyfit(x, y, 1)
                    
                    if slope > 0.05 * avg_value:  # 5% of average as threshold
                        trend = "increasing"
                    elif slope < -0.05 * avg_value:
                        trend = "decreasing"
                    else:
                        trend = "stable"
                    
                    # Check for fluctuation
                    residuals = y - (slope * x + _)
                    if np.std(residuals) > 0.2 * avg_value:
                        trend = "fluctuating"
                else:
                    # Simple trend determination for few data points
                    if values.iloc[-1] > values.iloc[0] * 1.1:
                        trend = "increasing"
                    elif values.iloc[-1] < values.iloc[0] * 0.9:
                        trend = "decreasing"
                    else:
                        trend = "stable"
                
                # Calculate percentage of recommended intake
                recommended = self.REFERENCE_VALUES.get(nutrient)
                percent_of_recommended = (avg_value / recommended) * 100 if recommended else None
                
                nutrient_trends[nutrient] = NutrientIntakeTrend(
                    nutrient=nutrient,
                    average=avg_value,
                    min=min_value,
                    max=max_value,
                    trend=trend,
                    dataPoints=len(values),
                    recommendedIntake=recommended,
                    percentOfRecommended=percent_of_recommended
                )
            
            return nutrient_trends
        
        except Exception as e:
            logger.error(f"Error analyzing nutrient trends: {str(e)}")
            return {}
    
    def analyze_meal_patterns(self, nutrition_data: List[Dict[str, Any]]) -> Dict[str, MealPatternAnalysis]:
        """
        Analyze patterns in meal consumption.
        
        Args:
            nutrition_data (list): List of nutrition data dictionaries
            
        Returns:
            Dict[str, MealPatternAnalysis]: Dictionary of patterns for each meal type
        """
        df = self._convert_to_dataframe(nutrition_data)
        if df.empty:
            logger.warning("No data to analyze for meal patterns")
            return {}
        
        try:
            # Extract unique dates to calculate meal frequency
            unique_dates = df['date'].dt.date.unique()
            total_days = len(unique_dates)
            
            if total_days == 0:
                return {}
            
            meal_patterns = {}
            
            for meal_type in self.MEAL_TYPES:
                meal_data = df[df['mealType'] == meal_type]
                if meal_data.empty:
                    continue
                
                # Calculate frequency
                meal_dates = meal_data['date'].dt.date.unique()
                frequency = len(meal_dates) / total_days * 100  # as percentage
                
                # Calculate average calories and nutrient breakdown
                avg_calories = meal_data['calories'].mean()
                
                nutrient_breakdown = {
                    'protein': meal_data['protein'].mean(),
                    'carbs': meal_data['carbs'].mean(),
                    'fat': meal_data['fat'].mean()
                }
                
                # Find common foods
                food_counter = Counter(meal_data['foodName'].tolist())
                common_foods = [
                    {'name': food, 'count': count, 'frequency': count / len(meal_data) * 100}
                    for food, count in food_counter.most_common(5)
                ]
                
                # Analyze time patterns if timestamp data is available
                time_pattern = None
                if 'time' in meal_data.columns:
                    # This would depend on having time data, which we're not including now
                    pass
                
                meal_patterns[meal_type] = MealPatternAnalysis(
                    mealType=meal_type,
                    frequency=frequency,
                    averageCalories=avg_calories,
                    commonFoods=common_foods,
                    nutrientBreakdown=nutrient_breakdown,
                    timePattern=time_pattern
                )
            
            return meal_patterns
        
        except Exception as e:
            logger.error(f"Error analyzing meal patterns: {str(e)}")
            return {}
    
    def identify_nutritional_gaps(self, nutrition_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify potential nutritional gaps based on recommended values.
        
        Args:
            nutrition_data (list): List of nutrition data dictionaries
            
        Returns:
            list: List of identified nutritional gaps
        """
        nutrient_trends = self.analyze_nutrient_trends(nutrition_data)
        if not nutrient_trends:
            return []
        
        try:
            gaps = []
            
            for nutrient, trend in nutrient_trends.items():
                if trend.percentOfRecommended is None:
                    continue
                
                # Check if nutrient intake is significantly below recommendation
                if trend.percentOfRecommended < 70:  # Less than 70% of recommended
                    gap = {
                        'nutrient': nutrient,
                        'averageIntake': trend.average,
                        'recommendedIntake': trend.recommendedIntake,
                        'percentOfRecommended': trend.percentOfRecommended,
                        'severity': 1 if trend.percentOfRecommended >= 50 else 
                                  2 if trend.percentOfRecommended >= 30 else 3,
                        'description': f"Low {nutrient} intake detected",
                        'recommendation': self._get_nutrient_recommendation(nutrient, "low")
                    }
                    gaps.append(gap)
                
                # Check for excessive intake for certain nutrients
                if nutrient in ['fat', 'sugar', 'sodium'] and trend.percentOfRecommended > 130:
                    gap = {
                        'nutrient': nutrient,
                        'averageIntake': trend.average,
                        'recommendedIntake': trend.recommendedIntake,
                        'percentOfRecommended': trend.percentOfRecommended,
                        'severity': 1 if trend.percentOfRecommended <= 150 else 
                                  2 if trend.percentOfRecommended <= 200 else 3,
                        'description': f"High {nutrient} intake detected",
                        'recommendation': self._get_nutrient_recommendation(nutrient, "high")
                    }
                    gaps.append(gap)
            
            return gaps
        
        except Exception as e:
            logger.error(f"Error identifying nutritional gaps: {str(e)}")
            return []
    
    def identify_positive_patterns(self, nutrition_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify positive nutritional patterns.
        
        Args:
            nutrition_data (list): List of nutrition data dictionaries
            
        Returns:
            list: List of identified positive patterns
        """
        nutrient_trends = self.analyze_nutrient_trends(nutrition_data)
        meal_patterns = self.analyze_meal_patterns(nutrition_data)
        
        if not nutrient_trends and not meal_patterns:
            return []
        
        try:
            positive_patterns = []
            
            # Check for good nutrient balance
            if ('protein' in nutrient_trends and 'carbs' in nutrient_trends and 'fat' in nutrient_trends):
                protein_percent = nutrient_trends['protein'].percentOfRecommended
                carbs_percent = nutrient_trends['carbs'].percentOfRecommended
                fat_percent = nutrient_trends['fat'].percentOfRecommended
                
                if (protein_percent is not None and 
                    carbs_percent is not None and 
                    fat_percent is not None and
                    80 <= protein_percent <= 120 and 
                    80 <= carbs_percent <= 120 and 
                    80 <= fat_percent <= 120):
                    
                    positive_patterns.append({
                        'type': 'balanced_macros',
                        'description': "Well-balanced macronutrient intake",
                        'details': {
                            'protein': protein_percent,
                            'carbs': carbs_percent,
                            'fat': fat_percent
                        }
                    })
            
            # Check for regular meal patterns
            regular_meals = []
            for meal_type, pattern in meal_patterns.items():
                if pattern.frequency >= 80:  # Meal consumed on 80% or more of days
                    regular_meals.append(meal_type)
            
            if len(regular_meals) >= 3:
                positive_patterns.append({
                    'type': 'regular_meals',
                    'description': "Regular meal pattern established",
                    'details': {
                        'regular_meals': regular_meals,
                        'frequency': {meal: meal_patterns[meal].frequency for meal in regular_meals}
                    }
                })
            
            # Check for good fiber intake
            if 'fiber' in nutrient_trends and nutrient_trends['fiber'].percentOfRecommended is not None:
                fiber_percent = nutrient_trends['fiber'].percentOfRecommended
                if fiber_percent >= 90:
                    positive_patterns.append({
                        'type': 'adequate_fiber',
                        'description': "Adequate fiber intake",
                        'details': {
                            'average_intake': nutrient_trends['fiber'].average,
                            'percent_of_recommended': fiber_percent
                        }
                    })
            
            # Check for improving trends
            improving_nutrients = []
            for nutrient, trend in nutrient_trends.items():
                if trend.trend == "increasing" and nutrient in ['protein', 'fiber'] or \
                   trend.trend == "decreasing" and nutrient in ['sugar', 'sodium', 'fat']:
                    improving_nutrients.append(nutrient)
            
            if improving_nutrients:
                positive_patterns.append({
                    'type': 'improving_trends',
                    'description': "Improving nutritional trends detected",
                    'details': {
                        'improving_nutrients': improving_nutrients
                    }
                })
            
            return positive_patterns
        
        except Exception as e:
            logger.error(f"Error identifying positive patterns: {str(e)}")
            return []
    
    def _get_nutrient_recommendation(self, nutrient: str, level: str) -> str:
        """
        Get recommendation for a nutrient based on its level.
        
        Args:
            nutrient (str): The nutrient name
            level (str): 'low' or 'high'
            
        Returns:
            str: A recommendation for adjusting the nutrient intake
        """
        recommendations = {
            'protein': {
                'low': "Increase protein intake by including more lean meats, fish, beans, or plant-based protein sources in your diet.",
                'high': "Monitor protein intake and ensure it's coming from diverse, high-quality sources."
            },
            'carbs': {
                'low': "Include more complex carbohydrates from whole grains, fruits, and vegetables in your meals.",
                'high': "Focus on high-quality carbohydrates from whole foods rather than refined sources."
            },
            'fat': {
                'low': "Add healthy sources of fat like avocados, nuts, seeds, and olive oil to your diet.",
                'high': "Reduce intake of saturated and trans fats, focusing instead on healthier unsaturated fats."
            },
            'fiber': {
                'low': "Increase fiber intake by eating more whole grains, legumes, fruits, and vegetables.",
                'high': "Your fiber intake is good, but make sure to drink plenty of water to maximize its benefits."
            },
            'sugar': {
                'low': "Your low sugar intake is generally positive for health.",
                'high': "Reduce added sugars by limiting processed foods, desserts, and sweetened beverages."
            },
            'sodium': {
                'low': "Your low sodium intake is generally beneficial for blood pressure.",
                'high': "Reduce sodium by limiting processed foods, canned products, and added salt."
            },
            'calories': {
                'low': "Increase your caloric intake with nutrient-dense foods to maintain energy levels.",
                'high': "Consider moderating caloric intake by focusing on nutrient-dense, filling foods."
            }
        }
        
        if nutrient in recommendations and level in recommendations[nutrient]:
            return recommendations[nutrient][level]
        
        return "Consult with a nutrition professional for personalized recommendations."
    
    def analyze_nutrition(self, nutrition_data: List[Dict[str, Any]], user_id: int = 1) -> NutritionAnalysis:
        """
        Perform comprehensive nutrition analysis.
        
        Args:
            nutrition_data (list): List of nutrition data dictionaries
            user_id (int): User ID
            
        Returns:
            NutritionAnalysis: Comprehensive nutrition analysis
        """
        df = self._convert_to_dataframe(nutrition_data)
        if df.empty:
            logger.warning("No data to perform nutrition analysis")
            # Return minimal analysis with empty values
            return NutritionAnalysis(
                userId=user_id,
                period={'start': datetime.now().date(), 'end': datetime.now().date()},
                dailyAverages={},
                calorieIntakeTrend=NutrientIntakeTrend(
                    nutrient='calories', average=0, min=0, max=0, trend='insufficient_data', dataPoints=0
                ),
                proteinIntakeTrend=NutrientIntakeTrend(
                    nutrient='protein', average=0, min=0, max=0, trend='insufficient_data', dataPoints=0
                ),
                carbIntakeTrend=NutrientIntakeTrend(
                    nutrient='carbs', average=0, min=0, max=0, trend='insufficient_data', dataPoints=0
                ),
                fatIntakeTrend=NutrientIntakeTrend(
                    nutrient='fat', average=0, min=0, max=0, trend='insufficient_data', dataPoints=0
                ),
                mealPatterns={},
                dietaryBalance={},
                nutritionalGaps=[],
                positivePatterns=[]
            )
        
        try:
            # Extract date range
            min_date = df['date'].min().date()
            max_date = df['date'].max().date()
            
            # Calculate daily averages
            daily_summaries = self._aggregate_daily_nutrition(df)
            summary_values = [s.dict() for s in daily_summaries.values()]
            
            daily_averages = {
                'calories': sum(s['totalCalories'] for s in summary_values) / len(summary_values) if summary_values else 0,
                'protein': sum(s['totalProtein'] for s in summary_values) / len(summary_values) if summary_values else 0,
                'carbs': sum(s['totalCarbs'] for s in summary_values) / len(summary_values) if summary_values else 0,
                'fat': sum(s['totalFat'] for s in summary_values) / len(summary_values) if summary_values else 0,
                'fiber': sum(s['totalFiber'] for s in summary_values) / len(summary_values) if summary_values else 0,
                'sugar': sum(s['totalSugar'] for s in summary_values) / len(summary_values) if summary_values else 0,
                'sodium': sum(s['totalSodium'] for s in summary_values) / len(summary_values) if summary_values else 0
            }
            
            # Get nutrient trends
            nutrient_trends = self.analyze_nutrient_trends(nutrition_data)
            
            # Get meal patterns
            meal_patterns = self.analyze_meal_patterns(nutrition_data)
            
            # Calculate dietary balance
            macronutrient_calories = {
                'protein': daily_averages['protein'] * 4,  # 4 calories per gram
                'carbs': daily_averages['carbs'] * 4,  # 4 calories per gram
                'fat': daily_averages['fat'] * 9  # 9 calories per gram
            }
            
            total_caloric_sum = sum(macronutrient_calories.values())
            
            dietary_balance = {
                'macronutrient_ratio': {
                    'protein_percent': (macronutrient_calories['protein'] / total_caloric_sum * 100) if total_caloric_sum else 0,
                    'carbs_percent': (macronutrient_calories['carbs'] / total_caloric_sum * 100) if total_caloric_sum else 0,
                    'fat_percent': (macronutrient_calories['fat'] / total_caloric_sum * 100) if total_caloric_sum else 0
                },
                'ideal_ratio': {
                    'protein_percent': 20,  # Typical recommendation
                    'carbs_percent': 50,  # Typical recommendation
                    'fat_percent': 30  # Typical recommendation
                },
                'balance_score': self._calculate_diet_balance_score(
                    macronutrient_calories['protein'] / total_caloric_sum if total_caloric_sum else 0,
                    macronutrient_calories['carbs'] / total_caloric_sum if total_caloric_sum else 0,
                    macronutrient_calories['fat'] / total_caloric_sum if total_caloric_sum else 0
                )
            }
            
            # Identify nutritional gaps
            nutritional_gaps = self.identify_nutritional_gaps(nutrition_data)
            
            # Identify positive patterns
            positive_patterns = self.identify_positive_patterns(nutrition_data)
            
            # Create comprehensive analysis
            return NutritionAnalysis(
                userId=user_id,
                period={'start': min_date, 'end': max_date},
                dailyAverages=daily_averages,
                calorieIntakeTrend=nutrient_trends.get('calories', NutrientIntakeTrend(
                    nutrient='calories', average=0, min=0, max=0, trend='insufficient_data', dataPoints=0
                )),
                proteinIntakeTrend=nutrient_trends.get('protein', NutrientIntakeTrend(
                    nutrient='protein', average=0, min=0, max=0, trend='insufficient_data', dataPoints=0
                )),
                carbIntakeTrend=nutrient_trends.get('carbs', NutrientIntakeTrend(
                    nutrient='carbs', average=0, min=0, max=0, trend='insufficient_data', dataPoints=0
                )),
                fatIntakeTrend=nutrient_trends.get('fat', NutrientIntakeTrend(
                    nutrient='fat', average=0, min=0, max=0, trend='insufficient_data', dataPoints=0
                )),
                mealPatterns=meal_patterns,
                dietaryBalance=dietary_balance,
                nutritionalGaps=nutritional_gaps,
                positivePatterns=positive_patterns
            )
        
        except Exception as e:
            logger.error(f"Error performing comprehensive nutrition analysis: {str(e)}")
            # Return minimal analysis with empty values
            return NutritionAnalysis(
                userId=user_id,
                period={'start': datetime.now().date(), 'end': datetime.now().date()},
                dailyAverages={},
                calorieIntakeTrend=NutrientIntakeTrend(
                    nutrient='calories', average=0, min=0, max=0, trend='insufficient_data', dataPoints=0
                ),
                proteinIntakeTrend=NutrientIntakeTrend(
                    nutrient='protein', average=0, min=0, max=0, trend='insufficient_data', dataPoints=0
                ),
                carbIntakeTrend=NutrientIntakeTrend(
                    nutrient='carbs', average=0, min=0, max=0, trend='insufficient_data', dataPoints=0
                ),
                fatIntakeTrend=NutrientIntakeTrend(
                    nutrient='fat', average=0, min=0, max=0, trend='insufficient_data', dataPoints=0
                ),
                mealPatterns={},
                dietaryBalance={},
                nutritionalGaps=[],
                positivePatterns=[]
            )
    
    def _calculate_diet_balance_score(self, protein_ratio, carbs_ratio, fat_ratio):
        """
        Calculate a diet balance score based on macronutrient ratios.
        
        Args:
            protein_ratio (float): Protein ratio (0-1)
            carbs_ratio (float): Carbs ratio (0-1)
            fat_ratio (float): Fat ratio (0-1)
            
        Returns:
            float: Balance score from 0-100
        """
        # Ideal macronutrient distributions (fractions)
        ideal_protein = 0.2  # 20%
        ideal_carbs = 0.5  # 50%
        ideal_fat = 0.3  # 30%
        
        # Calculate deviation from ideal
        protein_deviation = abs(protein_ratio - ideal_protein)
        carbs_deviation = abs(carbs_ratio - ideal_carbs)
        fat_deviation = abs(fat_ratio - ideal_fat)
        
        # Calculate total deviation (max possible is 2)
        total_deviation = protein_deviation + carbs_deviation + fat_deviation
        
        # Convert to a 0-100 score where 100 is perfect balance
        balance_score = 100 * (1 - total_deviation / 2)
        
        # Ensure score is within range
        return max(0, min(100, balance_score))