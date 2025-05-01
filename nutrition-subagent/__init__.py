"""
Nutrition Sub-Agent Package

This package contains components for analyzing nutritional data,
identifying dietary patterns, and generating personalized nutrition insights.
"""

from .api_client import NutritionApiClient
from .models import (
    NutritionData, 
    DailyNutritionSummary, 
    NutritionInsight, 
    NutrientIntakeTrend, 
    MealPatternAnalysis, 
    NutritionAnalysis
)
from .nutrition_analyzer import NutritionAnalyzer
from .insights_engine import NutritionInsightsEngine

__all__ = [
    'NutritionApiClient',
    'NutritionData', 
    'DailyNutritionSummary', 
    'NutritionInsight', 
    'NutrientIntakeTrend', 
    'MealPatternAnalysis', 
    'NutritionAnalysis',
    'NutritionAnalyzer',
    'NutritionInsightsEngine'
]