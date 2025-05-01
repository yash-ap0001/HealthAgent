"""
Insights Engine for generating nutrition insights from processed data.
"""
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

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
from models import NutritionInsight
from nutrition_analyzer import NutritionAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutritionInsightsEngine:
    """Engine for generating nutrition insights from processed data."""
    
    def __init__(self, api_client):
        """
        Initialize the insights engine.
        
        Args:
            api_client: The API client for interacting with the backend.
        """
        self.api_client = api_client
        self.analyzer = NutritionAnalyzer()
        logger.info("Initialized NutritionInsightsEngine")
    
    def generate_insights(self, user_id=1):
        """
        Generate nutrition insights from processed data.
        
        Args:
            user_id (int): User ID to generate insights for
            
        Returns:
            list: List of generated insights
        """
        logger.info(f"Generating nutrition insights for user {user_id}")
        
        # Get nutrition data from API
        nutrition_data = self.api_client.get_nutrition_data(user_id=user_id)
        if not nutrition_data:
            logger.warning("No nutrition data available for analysis")
            return []
        
        logger.info(f"Retrieved {len(nutrition_data)} nutrition data points for analysis")
        
        # Perform comprehensive nutrition analysis
        analysis = self.analyzer.analyze_nutrition(nutrition_data, user_id)
        
        # Generate insights based on analysis
        insights = []
        
        # Generate macronutrient balance insights
        balance_insights = self._generate_macronutrient_balance_insights(analysis)
        insights.extend(balance_insights)
        
        # Generate calorie intake insights
        calorie_insights = self._generate_calorie_insights(analysis)
        insights.extend(calorie_insights)
        
        # Generate meal pattern insights
        meal_insights = self._generate_meal_pattern_insights(analysis)
        insights.extend(meal_insights)
        
        # Generate nutritional gap insights
        gap_insights = self._generate_nutritional_gap_insights(analysis)
        insights.extend(gap_insights)
        
        # Generate positive pattern insights
        positive_insights = self._generate_positive_pattern_insights(analysis)
        insights.extend(positive_insights)
        
        # Generate trend insights
        trend_insights = self._generate_trend_insights(analysis)
        insights.extend(trend_insights)
        
        logger.info(f"Generated {len(insights)} nutrition insights")
        
        # Save insights to backend
        saved_insights = []
        for insight in insights:
            saved_insight = self.api_client.create_nutrition_insight(insight.dict())
            if saved_insight:
                saved_insights.append(saved_insight)
        
        logger.info(f"Saved {len(saved_insights)} nutrition insights to backend")
        
        return saved_insights
    
    def _generate_macronutrient_balance_insights(self, analysis):
        """
        Generate insights about macronutrient balance.
        
        Args:
            analysis: The nutrition analysis
            
        Returns:
            list: Macronutrient balance insights
        """
        insights = []
        
        try:
            if not analysis.dietaryBalance:
                return insights
            
            balance_score = analysis.dietaryBalance.get('balance_score', 0)
            macronutrient_ratio = analysis.dietaryBalance.get('macronutrient_ratio', {})
            
            if balance_score < 60:
                # Determine which macronutrients are out of balance
                protein_percent = macronutrient_ratio.get('protein_percent', 0)
                carbs_percent = macronutrient_ratio.get('carbs_percent', 0)
                fat_percent = macronutrient_ratio.get('fat_percent', 0)
                
                # Identify the most imbalanced macronutrient
                ideal = analysis.dietaryBalance.get('ideal_ratio', {})
                protein_diff = abs(protein_percent - ideal.get('protein_percent', 20))
                carbs_diff = abs(carbs_percent - ideal.get('carbs_percent', 50))
                fat_diff = abs(fat_percent - ideal.get('fat_percent', 30))
                
                imbalance_type = None
                if protein_diff > carbs_diff and protein_diff > fat_diff:
                    imbalance_type = "protein"
                    if protein_percent > ideal.get('protein_percent', 20):
                        direction = "high"
                    else:
                        direction = "low"
                elif carbs_diff > protein_diff and carbs_diff > fat_diff:
                    imbalance_type = "carbohydrate"
                    if carbs_percent > ideal.get('carbs_percent', 50):
                        direction = "high"
                    else:
                        direction = "low"
                else:
                    imbalance_type = "fat"
                    if fat_percent > ideal.get('fat_percent', 30):
                        direction = "high"
                    else:
                        direction = "low"
                
                severity = 1
                if balance_score < 40:
                    severity = 2
                if balance_score < 20:
                    severity = 3
                
                title = f"{direction.capitalize()} {imbalance_type} intake detected"
                
                description = f"Your diet shows a {direction} proportion of {imbalance_type} " \
                              f"({round(locals()[imbalance_type + '_percent'], 1)}% of calories vs. " \
                              f"ideal {ideal.get(imbalance_type + '_percent', 0)}%)."
                
                recommendation = ""
                if imbalance_type == "protein":
                    if direction == "high":
                        recommendation = "Consider moderating protein intake and increasing complex carbohydrates. " \
                                        "Focus on plant-based proteins and ensure you're drinking enough water."
                    else:
                        recommendation = "Increase protein intake by adding lean meats, fish, beans, tofu, or " \
                                        "plant-based protein sources to your meals and snacks."
                elif imbalance_type == "carbohydrate":
                    if direction == "high":
                        recommendation = "Reduce refined carbohydrates and focus on complex carbs from whole " \
                                        "grains, fruits, and vegetables. Increase protein and healthy fats."
                    else:
                        recommendation = "Add more complex carbohydrates like whole grains, fruits, and " \
                                        "starchy vegetables to your meals for balanced energy."
                else:  # fat
                    if direction == "high":
                        recommendation = "Reduce fat intake, especially saturated and trans fats. Choose lean " \
                                        "proteins and increase complex carbohydrates from whole foods."
                    else:
                        recommendation = "Include more healthy fats from sources like avocados, nuts, seeds, " \
                                        "and olive oil in your diet."
                
                insights.append(NutritionInsight(
                    category="nutrition",
                    title=title,
                    description=description,
                    severity=severity,
                    isActionable=True,
                    recommendation=recommendation
                ))
            elif balance_score > 80:
                # Good macronutrient balance insight
                insights.append(NutritionInsight(
                    category="nutrition",
                    title="Well-balanced macronutrient intake",
                    description="Your diet shows a healthy balance of proteins, carbohydrates, and fats, " \
                               f"with a balance score of {round(balance_score, 1)} out of 100.",
                    severity=1,
                    isActionable=False,
                    recommendation="Continue maintaining this balanced approach to your diet."
                ))
            
            return insights
        
        except Exception as e:
            logger.error(f"Error generating macronutrient balance insights: {str(e)}")
            return []
    
    def _generate_calorie_insights(self, analysis):
        """
        Generate insights about calorie intake.
        
        Args:
            analysis: The nutrition analysis
            
        Returns:
            list: Calorie-related insights
        """
        insights = []
        
        try:
            calorie_trend = analysis.calorieIntakeTrend
            if not calorie_trend or calorie_trend.dataPoints < 3:
                return insights
            
            avg_calories = calorie_trend.average
            recommended_calories = calorie_trend.recommendedIntake or 2000  # Default recommendation
            percent_of_recommended = calorie_trend.percentOfRecommended or (avg_calories / recommended_calories * 100)
            
            # Check for significantly low calorie intake
            if percent_of_recommended < 70:
                severity = 1
                if percent_of_recommended < 60:
                    severity = 2
                if percent_of_recommended < 50:
                    severity = 3
                
                insights.append(NutritionInsight(
                    category="nutrition",
                    title="Low caloric intake detected",
                    description=f"Your average daily calorie intake ({round(avg_calories)} calories) is " \
                               f"{round(100 - percent_of_recommended)}% below recommended levels.",
                    severity=severity,
                    isActionable=True,
                    recommendation="Consider increasing your caloric intake with nutrient-dense foods " \
                                  "to ensure you're meeting your body's energy needs. Focus on adding " \
                                  "healthy fats, complex carbohydrates, and proteins to your meals."
                ))
            
            # Check for significantly high calorie intake
            elif percent_of_recommended > 130:
                severity = 1
                if percent_of_recommended > 150:
                    severity = 2
                if percent_of_recommended > 180:
                    severity = 3
                
                insights.append(NutritionInsight(
                    category="nutrition",
                    title="High caloric intake detected",
                    description=f"Your average daily calorie intake ({round(avg_calories)} calories) is " \
                               f"{round(percent_of_recommended - 100)}% above recommended levels.",
                    severity=severity,
                    isActionable=True,
                    recommendation="Consider moderating your caloric intake by focusing on nutrient-dense, " \
                                  "filling foods. Increase your consumption of vegetables, lean proteins, " \
                                  "and high-fiber foods, which can help you feel satisfied with fewer calories."
                ))
            
            # Check for calorie trend
            if calorie_trend.trend == "increasing" and percent_of_recommended > 110:
                insights.append(NutritionInsight(
                    category="nutrition",
                    title="Increasing calorie trend detected",
                    description="Your daily calorie intake has been trending upward over time, " \
                               "which may lead to weight gain if continued.",
                    severity=1,
                    isActionable=True,
                    recommendation="Monitor your portion sizes and be mindful of high-calorie foods and beverages. " \
                                  "Consider tracking your meals to become more aware of your daily intake."
                ))
            elif calorie_trend.trend == "decreasing" and percent_of_recommended < 90:
                insights.append(NutritionInsight(
                    category="nutrition",
                    title="Decreasing calorie trend detected",
                    description="Your daily calorie intake has been trending downward over time, " \
                               "which may lead to energy deficits if continued.",
                    severity=1,
                    isActionable=True,
                    recommendation="Make sure you're eating regular meals and including enough energy-dense foods " \
                                  "to meet your body's needs. Consider adding nutrient-rich snacks between meals."
                ))
            
            # Check for high calorie variability
            if calorie_trend.max > calorie_trend.average * 1.5 and calorie_trend.min < calorie_trend.average * 0.5:
                insights.append(NutritionInsight(
                    category="nutrition",
                    title="High calorie intake variability",
                    description=f"Your daily calorie intake varies significantly, ranging from " \
                               f"{round(calorie_trend.min)} to {round(calorie_trend.max)} calories.",
                    severity=1,
                    isActionable=True,
                    recommendation="Try to establish more consistent eating patterns. Large fluctuations " \
                                  "in calorie intake can affect energy levels, metabolism, and hunger signals."
                ))
            
            return insights
        
        except Exception as e:
            logger.error(f"Error generating calorie insights: {str(e)}")
            return []
    
    def _generate_meal_pattern_insights(self, analysis):
        """
        Generate insights about meal patterns.
        
        Args:
            analysis: The nutrition analysis
            
        Returns:
            list: Meal pattern insights
        """
        insights = []
        
        try:
            meal_patterns = analysis.mealPatterns
            if not meal_patterns:
                return insights
            
            # Check for skipped meals
            missing_meals = []
            for meal in ["breakfast", "lunch", "dinner"]:
                if meal not in meal_patterns or meal_patterns[meal].frequency < 70:
                    missing_meals.append(meal)
            
            if missing_meals:
                meal_str = ", ".join(missing_meals)
                insights.append(NutritionInsight(
                    category="nutrition",
                    title=f"Frequently skipped {meal_str}",
                    description=f"You're regularly skipping {meal_str}, which may affect your energy levels " \
                               f"and make it harder to get balanced nutrition throughout the day.",
                    severity=1 if len(missing_meals) == 1 else 2,
                    isActionable=True,
                    recommendation=f"Try to include {meal_str} in your daily routine. Even a small, " \
                                  f"nutritious meal can help maintain energy and reduce overeating later."
                ))
            
            # Check for imbalanced meal calories
            meal_calories = {}
            for meal, pattern in meal_patterns.items():
                if meal in ["breakfast", "lunch", "dinner"]:
                    meal_calories[meal] = pattern.averageCalories
            
            if len(meal_calories) >= 2:
                max_meal = max(meal_calories.items(), key=lambda x: x[1])
                min_meal = min(meal_calories.items(), key=lambda x: x[1])
                
                if max_meal[1] > min_meal[1] * 3:  # One meal has 3x the calories of another
                    insights.append(NutritionInsight(
                        category="nutrition",
                        title="Imbalanced meal calorie distribution",
                        description=f"Your {max_meal[0]} contains significantly more calories " \
                                   f"({round(max_meal[1])} on average) than your {min_meal[0]} " \
                                   f"({round(min_meal[1])} on average).",
                        severity=1,
                        isActionable=True,
                        recommendation="Try to distribute your calories more evenly throughout the day. " \
                                      f"Consider adding more nutrient-dense foods to your {min_meal[0]} " \
                                      f"and lightening your {max_meal[0]} slightly."
                    ))
            
            # Check for high snack frequency
            if "snack" in meal_patterns and meal_patterns["snack"].frequency > 90:
                snack_calories = meal_patterns["snack"].averageCalories
                total_daily_calories = analysis.dailyAverages.get('calories', 0)
                
                if total_daily_calories > 0 and snack_calories / total_daily_calories > 0.3:
                    # Snacks make up over 30% of total calorie intake
                    insights.append(NutritionInsight(
                        category="nutrition",
                        title="High snack calorie intake",
                        description=f"Snacks make up approximately {round(snack_calories / total_daily_calories * 100)}% " \
                                   f"of your total daily calorie intake.",
                        severity=1,
                        isActionable=True,
                        recommendation="Consider the quality of your snacks. Opt for nutrient-dense options " \
                                      "like fruits, vegetables with hummus, nuts, or yogurt instead of " \
                                      "processed snack foods."
                    ))
            
            return insights
        
        except Exception as e:
            logger.error(f"Error generating meal pattern insights: {str(e)}")
            return []
    
    def _generate_nutritional_gap_insights(self, analysis):
        """
        Generate insights about nutritional gaps.
        
        Args:
            analysis: The nutrition analysis
            
        Returns:
            list: Nutritional gap insights
        """
        insights = []
        
        try:
            nutritional_gaps = analysis.nutritionalGaps
            if not nutritional_gaps:
                return insights
            
            # Convert top gaps into insights
            for gap in nutritional_gaps:
                if gap['severity'] >= 2:  # Only create insights for more significant gaps
                    insights.append(NutritionInsight(
                        category="nutrition",
                        title=gap['description'],
                        description=f"Your average {gap['nutrient']} intake is {round(gap['averageIntake'])} " \
                                   f"{gap['nutrient'] if gap['nutrient'] != 'calories' else ''}, which is only " \
                                   f"{round(gap['percentOfRecommended'])}% of the recommended amount.",
                        severity=gap['severity'],
                        isActionable=True,
                        recommendation=gap['recommendation']
                    ))
            
            return insights
        
        except Exception as e:
            logger.error(f"Error generating nutritional gap insights: {str(e)}")
            return []
    
    def _generate_positive_pattern_insights(self, analysis):
        """
        Generate insights about positive nutritional patterns.
        
        Args:
            analysis: The nutrition analysis
            
        Returns:
            list: Positive pattern insights
        """
        insights = []
        
        try:
            positive_patterns = analysis.positivePatterns
            if not positive_patterns:
                return insights
            
            # Convert positive patterns to insights
            for pattern in positive_patterns:
                if pattern['type'] == 'balanced_macros':
                    insights.append(NutritionInsight(
                        category="nutrition",
                        title="Well-balanced macronutrient intake",
                        description="Your diet shows a healthy balance of proteins, carbohydrates, and fats.",
                        severity=1,
                        isActionable=False,
                        recommendation="Continue with your balanced approach to eating."
                    ))
                
                elif pattern['type'] == 'regular_meals':
                    insights.append(NutritionInsight(
                        category="nutrition",
                        title="Consistent meal pattern established",
                        description="You're maintaining a consistent meal schedule, which helps regulate " \
                                   "metabolism and energy levels throughout the day.",
                        severity=1,
                        isActionable=False,
                        recommendation="Maintaining regular meal times helps with digestion and hunger management."
                    ))
                
                elif pattern['type'] == 'adequate_fiber':
                    insights.append(NutritionInsight(
                        category="nutrition",
                        title="Healthy fiber intake",
                        description=f"Your average fiber intake is {round(pattern['details']['average_intake'])}g per day, " \
                                   f"which meets or exceeds recommendations.",
                        severity=1,
                        isActionable=False,
                        recommendation="Continue including high-fiber foods like fruits, vegetables, legumes, " \
                                      "and whole grains in your diet."
                    ))
                
                elif pattern['type'] == 'improving_trends':
                    nutrients = pattern['details']['improving_nutrients']
                    nutrients_str = ", ".join(nutrients)
                    insights.append(NutritionInsight(
                        category="nutrition",
                        title="Improving nutritional trends",
                        description=f"Your diet shows positive changes in {nutrients_str} intake.",
                        severity=1,
                        isActionable=False,
                        recommendation="Keep up with these positive changes to your eating habits."
                    ))
            
            return insights
        
        except Exception as e:
            logger.error(f"Error generating positive pattern insights: {str(e)}")
            return []
    
    def _generate_trend_insights(self, analysis):
        """
        Generate insights about nutrient trends.
        
        Args:
            analysis: The nutrition analysis
            
        Returns:
            list: Trend insights
        """
        insights = []
        
        try:
            # Check for trends in protein, carbs, and fat
            trends_to_check = {
                'protein': analysis.proteinIntakeTrend,
                'carbs': analysis.carbIntakeTrend,
                'fat': analysis.fatIntakeTrend
            }
            
            for nutrient, trend in trends_to_check.items():
                if trend.trend not in ["increasing", "decreasing"]:
                    continue
                
                percent_of_recommended = trend.percentOfRecommended or 0
                
                # Only generate trend insights if the trend is potentially concerning
                if trend.trend == "increasing" and nutrient in ["fat", "carbs"] and percent_of_recommended > 110:
                    insights.append(NutritionInsight(
                        category="nutrition",
                        title=f"Increasing {nutrient} trend",
                        description=f"Your {nutrient} intake has been trending upward, " \
                                   f"and is already above recommended levels.",
                        severity=1,
                        isActionable=True,
                        recommendation=f"Monitor your {nutrient} intake and consider moderating " \
                                      f"foods high in {nutrient}."
                    ))
                
                elif trend.trend == "decreasing" and nutrient == "protein" and percent_of_recommended < 90:
                    insights.append(NutritionInsight(
                        category="nutrition",
                        title="Decreasing protein trend",
                        description="Your protein intake has been trending downward, " \
                                   "and is below recommended levels.",
                        severity=2,
                        isActionable=True,
                        recommendation="Increase your protein intake by adding more lean meats, fish, " \
                                      "eggs, dairy, or plant-based protein sources to your meals."
                    ))
            
            return insights
        
        except Exception as e:
            logger.error(f"Error generating trend insights: {str(e)}")
            return []