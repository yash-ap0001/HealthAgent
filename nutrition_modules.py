"""
Nutrition Models and Utilities

This file contains simplified models and classes for nutrition analysis to avoid import issues.
"""
from datetime import datetime, date
from typing import List, Dict, Any, Optional

# Define simplified model classes
class NutritionData:
    """Class for nutrition data points."""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.userId = kwargs.get('userId')
        self.date = kwargs.get('date')
        self.mealType = kwargs.get('mealType', 'unknown')
        self.foodName = kwargs.get('foodName', 'Unknown food')
        self.quantity = kwargs.get('quantity', 1.0)
        self.unit = kwargs.get('unit', 'g')
        self.calories = kwargs.get('calories', 0.0)
        self.protein = kwargs.get('protein', 0.0)
        self.carbs = kwargs.get('carbs', 0.0)
        self.fat = kwargs.get('fat', 0.0)
        self.fiber = kwargs.get('fiber', 0.0)
        self.sugar = kwargs.get('sugar', 0.0)
        self.sodium = kwargs.get('sodium', 0.0)
        self.source = kwargs.get('source')
        self.createdAt = kwargs.get('createdAt')
        self.updatedAt = kwargs.get('updatedAt')

class DailyNutritionSummary:
    """Class for daily nutrition summary."""
    def __init__(self, **kwargs):
        self.date = kwargs.get('date')
        self.totalCalories = kwargs.get('totalCalories', 0.0)
        self.totalProtein = kwargs.get('totalProtein', 0.0)
        self.totalCarbs = kwargs.get('totalCarbs', 0.0)
        self.totalFat = kwargs.get('totalFat', 0.0)
        self.totalFiber = kwargs.get('totalFiber', 0.0)
        self.totalSugar = kwargs.get('totalSugar', 0.0)
        self.totalSodium = kwargs.get('totalSodium', 0.0)
        self.mealBreakdown = kwargs.get('mealBreakdown', {})
        self.nutrientPercentages = kwargs.get('nutrientPercentages', {})
    
    def dict(self):
        """Convert to dictionary."""
        return {
            'date': self.date,
            'totalCalories': self.totalCalories,
            'totalProtein': self.totalProtein,
            'totalCarbs': self.totalCarbs,
            'totalFat': self.totalFat,
            'totalFiber': self.totalFiber,
            'totalSugar': self.totalSugar,
            'totalSodium': self.totalSodium,
            'mealBreakdown': self.mealBreakdown,
            'nutrientPercentages': self.nutrientPercentages
        }

class NutritionInsight:
    """Class for nutrition insights."""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.userId = kwargs.get('userId')
        self.category = kwargs.get('category', 'nutrition')
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.severity = kwargs.get('severity', 1)
        self.isActionable = kwargs.get('isActionable', True)
        self.recommendation = kwargs.get('recommendation')
        self.createdAt = kwargs.get('createdAt')
        self.updatedAt = kwargs.get('updatedAt')
    
    def dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'userId': self.userId,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'isActionable': self.isActionable,
            'recommendation': self.recommendation,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }

class NutrientIntakeTrend:
    """Class for nutrient intake trend analysis."""
    def __init__(self, **kwargs):
        self.nutrient = kwargs.get('nutrient', '')
        self.average = kwargs.get('average', 0.0)
        self.min = kwargs.get('min', 0.0)
        self.max = kwargs.get('max', 0.0)
        self.trend = kwargs.get('trend', 'stable')
        self.dataPoints = kwargs.get('dataPoints', 0)
        self.recommendedIntake = kwargs.get('recommendedIntake')
        self.percentOfRecommended = kwargs.get('percentOfRecommended')

class MealPatternAnalysis:
    """Class for meal pattern analysis."""
    def __init__(self, **kwargs):
        self.mealType = kwargs.get('mealType', '')
        self.frequency = kwargs.get('frequency', 0.0)
        self.averageCalories = kwargs.get('averageCalories', 0.0)
        self.commonFoods = kwargs.get('commonFoods', [])
        self.nutrientBreakdown = kwargs.get('nutrientBreakdown', {})
        self.timePattern = kwargs.get('timePattern')

class NutritionAnalysis:
    """Class for comprehensive nutrition analysis."""
    def __init__(self, **kwargs):
        self.userId = kwargs.get('userId', 0)
        self.period = kwargs.get('period', {})
        self.dailyAverages = kwargs.get('dailyAverages', {})
        self.calorieIntakeTrend = kwargs.get('calorieIntakeTrend')
        self.proteinIntakeTrend = kwargs.get('proteinIntakeTrend')
        self.carbIntakeTrend = kwargs.get('carbIntakeTrend')
        self.fatIntakeTrend = kwargs.get('fatIntakeTrend')
        self.mealPatterns = kwargs.get('mealPatterns', {})
        self.dietaryBalance = kwargs.get('dietaryBalance', {})
        self.nutritionalGaps = kwargs.get('nutritionalGaps', [])
        self.positivePatterns = kwargs.get('positivePatterns', [])

# Define a simplified analyzer class for nutrition data
class NutritionAnalyzer:
    """Simplified analyzer for nutrition data metrics."""
    
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
        pass
    
    def analyze_nutrition(self, nutrition_data, user_id=1):
        """
        Perform a simplified nutrition analysis.
        
        Args:
            nutrition_data: List of nutrition data dictionaries
            user_id: User ID
            
        Returns:
            NutritionAnalysis: Nutrition analysis
        """
        if not nutrition_data:
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
        
        # Calculate basics
        dates = [data.get('date') for data in nutrition_data]
        if dates:
            try:
                # Convert string dates to datetime
                dates = [datetime.fromisoformat(d) if isinstance(d, str) else d for d in dates]
                min_date = min(dates).date()
                max_date = max(dates).date()
            except:
                min_date = datetime.now().date()
                max_date = datetime.now().date()
        else:
            min_date = datetime.now().date()
            max_date = datetime.now().date()
        
        # Calculate daily averages
        total_calories = sum([data.get('calories', 0) for data in nutrition_data])
        total_protein = sum([data.get('protein', 0) for data in nutrition_data])
        total_carbs = sum([data.get('carbs', 0) for data in nutrition_data])
        total_fat = sum([data.get('fat', 0) for data in nutrition_data])
        
        avg_calories = total_calories / len(nutrition_data) if nutrition_data else 0
        avg_protein = total_protein / len(nutrition_data) if nutrition_data else 0
        avg_carbs = total_carbs / len(nutrition_data) if nutrition_data else 0
        avg_fat = total_fat / len(nutrition_data) if nutrition_data else 0
        
        # Create simple trends
        calorie_trend = NutrientIntakeTrend(
            nutrient='calories',
            average=avg_calories,
            min=min([data.get('calories', 0) for data in nutrition_data]) if nutrition_data else 0,
            max=max([data.get('calories', 0) for data in nutrition_data]) if nutrition_data else 0,
            trend='stable',
            dataPoints=len(nutrition_data),
            recommendedIntake=self.REFERENCE_VALUES.get('calories'),
            percentOfRecommended=(avg_calories / self.REFERENCE_VALUES.get('calories')) * 100 if self.REFERENCE_VALUES.get('calories') else None
        )
        
        protein_trend = NutrientIntakeTrend(
            nutrient='protein',
            average=avg_protein,
            min=min([data.get('protein', 0) for data in nutrition_data]) if nutrition_data else 0,
            max=max([data.get('protein', 0) for data in nutrition_data]) if nutrition_data else 0,
            trend='stable',
            dataPoints=len(nutrition_data),
            recommendedIntake=self.REFERENCE_VALUES.get('protein'),
            percentOfRecommended=(avg_protein / self.REFERENCE_VALUES.get('protein')) * 100 if self.REFERENCE_VALUES.get('protein') else None
        )
        
        carbs_trend = NutrientIntakeTrend(
            nutrient='carbs',
            average=avg_carbs,
            min=min([data.get('carbs', 0) for data in nutrition_data]) if nutrition_data else 0,
            max=max([data.get('carbs', 0) for data in nutrition_data]) if nutrition_data else 0,
            trend='stable',
            dataPoints=len(nutrition_data),
            recommendedIntake=self.REFERENCE_VALUES.get('carbs'),
            percentOfRecommended=(avg_carbs / self.REFERENCE_VALUES.get('carbs')) * 100 if self.REFERENCE_VALUES.get('carbs') else None
        )
        
        fat_trend = NutrientIntakeTrend(
            nutrient='fat',
            average=avg_fat,
            min=min([data.get('fat', 0) for data in nutrition_data]) if nutrition_data else 0,
            max=max([data.get('fat', 0) for data in nutrition_data]) if nutrition_data else 0,
            trend='stable',
            dataPoints=len(nutrition_data),
            recommendedIntake=self.REFERENCE_VALUES.get('fat'),
            percentOfRecommended=(avg_fat / self.REFERENCE_VALUES.get('fat')) * 100 if self.REFERENCE_VALUES.get('fat') else None
        )
        
        # Group data by meal type
        meal_data = {}
        for meal_type in self.MEAL_TYPES:
            meal_records = [data for data in nutrition_data if data.get('mealType') == meal_type]
            if meal_records:
                meal_calories = sum([data.get('calories', 0) for data in meal_records]) / len(meal_records)
                meal_frequency = len(meal_records) / len(nutrition_data) * 100 if nutrition_data else 0
                
                # Find common foods
                food_names = [data.get('foodName', '') for data in meal_records]
                food_counts = {}
                for food in food_names:
                    if food:
                        food_counts[food] = food_counts.get(food, 0) + 1
                
                common_foods = []
                for food, count in food_counts.items():
                    common_foods.append({
                        'name': food,
                        'count': count,
                        'frequency': count / len(meal_records) * 100
                    })
                
                meal_data[meal_type] = MealPatternAnalysis(
                    mealType=meal_type,
                    frequency=meal_frequency,
                    averageCalories=meal_calories,
                    commonFoods=sorted(common_foods, key=lambda x: x['count'], reverse=True)[:5],
                    nutrientBreakdown={
                        'protein': sum([data.get('protein', 0) for data in meal_records]) / len(meal_records),
                        'carbs': sum([data.get('carbs', 0) for data in meal_records]) / len(meal_records),
                        'fat': sum([data.get('fat', 0) for data in meal_records]) / len(meal_records)
                    }
                )
        
        # Create simple dietary balance
        macronutrient_calories = {
            'protein': avg_protein * 4,  # 4 calories per gram
            'carbs': avg_carbs * 4,  # 4 calories per gram
            'fat': avg_fat * 9  # 9 calories per gram
        }
        
        total_caloric_sum = sum(macronutrient_calories.values())
        
        if total_caloric_sum > 0:
            protein_percent = (macronutrient_calories['protein'] / total_caloric_sum) * 100
            carbs_percent = (macronutrient_calories['carbs'] / total_caloric_sum) * 100
            fat_percent = (macronutrient_calories['fat'] / total_caloric_sum) * 100
        else:
            protein_percent = 0
            carbs_percent = 0
            fat_percent = 0
        
        dietary_balance = {
            'macronutrient_ratio': {
                'protein_percent': protein_percent,
                'carbs_percent': carbs_percent,
                'fat_percent': fat_percent
            },
            'ideal_ratio': {
                'protein_percent': 20,  # Typical recommendation
                'carbs_percent': 50,  # Typical recommendation
                'fat_percent': 30  # Typical recommendation
            },
            'balance_score': 100 - (abs(protein_percent - 20) + abs(carbs_percent - 50) + abs(fat_percent - 30)) / 2
        }
        
        # Return the analysis
        return NutritionAnalysis(
            userId=user_id,
            period={'start': min_date, 'end': max_date},
            dailyAverages={
                'calories': avg_calories,
                'protein': avg_protein,
                'carbs': avg_carbs,
                'fat': avg_fat
            },
            calorieIntakeTrend=calorie_trend,
            proteinIntakeTrend=protein_trend,
            carbIntakeTrend=carbs_trend,
            fatIntakeTrend=fat_trend,
            mealPatterns=meal_data,
            dietaryBalance=dietary_balance,
            nutritionalGaps=[],
            positivePatterns=[]
        )

# Simplified insights engine
class NutritionInsightsEngine:
    """Simplified engine for generating nutrition insights from processed data."""
    
    def __init__(self, api_client):
        """Initialize the insights engine."""
        self.api_client = api_client
        self.analyzer = NutritionAnalyzer()
    
    def generate_insights(self, user_id=1):
        """Generate nutrition insights for a user."""
        # Get nutrition data
        nutrition_data = self.api_client.get_nutrition_data(user_id=user_id)
        if not nutrition_data:
            return []
        
        # Analyze nutrition data
        analysis = self.analyzer.analyze_nutrition(nutrition_data, user_id)
        
        # Generate basic insights
        insights = []
        
        # Check for dietary balance
        if analysis.dietaryBalance:
            balance_score = analysis.dietaryBalance.get('balance_score', 0)
            macronutrient_ratio = analysis.dietaryBalance.get('macronutrient_ratio', {})
            
            if balance_score < 60:
                # Identify imbalanced macronutrient
                protein_percent = macronutrient_ratio.get('protein_percent', 0)
                carbs_percent = macronutrient_ratio.get('carbs_percent', 0)
                fat_percent = macronutrient_ratio.get('fat_percent', 0)
                
                ideal = analysis.dietaryBalance.get('ideal_ratio', {})
                protein_diff = abs(protein_percent - ideal.get('protein_percent', 20))
                carbs_diff = abs(carbs_percent - ideal.get('carbs_percent', 50))
                fat_diff = abs(fat_percent - ideal.get('fat_percent', 30))
                
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
                
                # Create an insight
                value = locals()[imbalance_type + '_percent']
                title = f"{direction.capitalize()} {imbalance_type} intake detected"
                description = f"Your diet shows a {direction} proportion of {imbalance_type} ({round(value, 1)}% of calories vs. ideal {ideal.get(imbalance_type + '_percent', 0)}%)."
                
                recommendation = ""
                if imbalance_type == "protein":
                    if direction == "high":
                        recommendation = "Consider moderating protein intake and increasing complex carbohydrates. Focus on plant-based proteins and ensure you're drinking enough water."
                    else:
                        recommendation = "Increase protein intake by adding lean meats, fish, beans, tofu, or plant-based protein sources to your meals and snacks."
                elif imbalance_type == "carbohydrate":
                    if direction == "high":
                        recommendation = "Reduce refined carbohydrates and focus on complex carbs from whole grains, fruits, and vegetables. Increase protein and healthy fats."
                    else:
                        recommendation = "Add more complex carbohydrates like whole grains, fruits, and starchy vegetables to your meals for balanced energy."
                else:  # fat
                    if direction == "high":
                        recommendation = "Reduce fat intake, especially saturated and trans fats. Choose lean proteins and increase complex carbohydrates from whole foods."
                    else:
                        recommendation = "Include more healthy fats from sources like avocados, nuts, seeds, and olive oil in your diet."
                
                insight = NutritionInsight(
                    userId=user_id,
                    category="nutrition",
                    title=title,
                    description=description,
                    severity=severity,
                    isActionable=True,
                    recommendation=recommendation
                )
                insights.append(insight)
            elif balance_score > 80:
                # Good macronutrient balance insight
                insight = NutritionInsight(
                    userId=user_id,
                    category="nutrition",
                    title="Well-balanced macronutrient intake",
                    description=f"Your diet shows a healthy balance of proteins, carbohydrates, and fats, with a balance score of {round(balance_score, 1)} out of 100.",
                    severity=1,
                    isActionable=False,
                    recommendation="Continue maintaining this balanced approach to your diet."
                )
                insights.append(insight)
        
        # Check for calorie intake issues
        if analysis.calorieIntakeTrend:
            calorie_trend = analysis.calorieIntakeTrend
            if calorie_trend.percentOfRecommended:
                percent = calorie_trend.percentOfRecommended
                avg_calories = calorie_trend.average
                
                if percent < 70:
                    # Low calorie intake
                    severity = 1
                    if percent < 60:
                        severity = 2
                    if percent < 50:
                        severity = 3
                    
                    insight = NutritionInsight(
                        userId=user_id,
                        category="nutrition",
                        title="Low caloric intake detected",
                        description=f"Your average daily calorie intake ({round(avg_calories)} calories) is {round(100 - percent)}% below recommended levels.",
                        severity=severity,
                        isActionable=True,
                        recommendation="Consider increasing your caloric intake with nutrient-dense foods to ensure you're meeting your body's energy needs."
                    )
                    insights.append(insight)
                elif percent > 130:
                    # High calorie intake
                    severity = 1
                    if percent > 150:
                        severity = 2
                    if percent > 180:
                        severity = 3
                    
                    insight = NutritionInsight(
                        userId=user_id,
                        category="nutrition",
                        title="High caloric intake detected",
                        description=f"Your average daily calorie intake ({round(avg_calories)} calories) is {round(percent - 100)}% above recommended levels.",
                        severity=severity,
                        isActionable=True,
                        recommendation="Consider moderating your caloric intake by focusing on nutrient-dense, filling foods."
                    )
                    insights.append(insight)
        
        # Check for meal pattern issues
        if analysis.mealPatterns:
            missing_meals = []
            for meal in ["breakfast", "lunch", "dinner"]:
                if meal not in analysis.mealPatterns or analysis.mealPatterns[meal].frequency < 70:
                    missing_meals.append(meal)
            
            if missing_meals:
                meal_str = ", ".join(missing_meals)
                insight = NutritionInsight(
                    userId=user_id,
                    category="nutrition",
                    title=f"Frequently skipped {meal_str}",
                    description=f"You're regularly skipping {meal_str}, which may affect your energy levels and make it harder to get balanced nutrition throughout the day.",
                    severity=1 if len(missing_meals) == 1 else 2,
                    isActionable=True,
                    recommendation=f"Try to include {meal_str} in your daily routine. Even a small, nutritious meal can help maintain energy and reduce overeating later."
                )
                insights.append(insight)
        
        # Save insights to the database
        saved_insights = []
        for insight in insights:
            saved_insight = self.api_client.create_nutrition_insight(insight.dict())
            if saved_insight:
                saved_insights.append(saved_insight)
        
        return saved_insights