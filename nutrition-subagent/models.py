"""
Data models for the Nutrition Sub-Agent.
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class NutritionData(BaseModel):
    """Model for nutrition data points."""
    
    id: Optional[int] = None
    userId: Optional[int] = None
    date: date
    mealType: str  # 'breakfast', 'lunch', 'dinner', 'snack'
    foodName: str
    quantity: float
    unit: str  # 'g', 'ml', 'serving', etc.
    calories: float
    protein: Optional[float] = None  # in grams
    carbs: Optional[float] = None  # in grams
    fat: Optional[float] = None  # in grams
    fiber: Optional[float] = None  # in grams
    sugar: Optional[float] = None  # in grams
    sodium: Optional[float] = None  # in mg
    source: Optional[str] = None  # source of the data
    metadata: Optional[Dict[str, Any]] = None  # additional data
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class DailyNutritionSummary(BaseModel):
    """Model for daily nutrition summary."""
    
    date: date
    totalCalories: float
    totalProtein: float  # in grams
    totalCarbs: float  # in grams
    totalFat: float  # in grams
    totalFiber: Optional[float] = None  # in grams
    totalSugar: Optional[float] = None  # in grams
    totalSodium: Optional[float] = None  # in mg
    mealBreakdown: Dict[str, Dict[str, float]]  # breakdown by meal type
    nutrientPercentages: Dict[str, float]  # percentage of macronutrients

class NutritionInsight(BaseModel):
    """Model for nutrition insights."""
    
    id: Optional[int] = None
    userId: Optional[int] = None
    category: str = "nutrition"
    title: str
    description: str
    severity: Optional[int] = Field(None, ge=1, le=5)
    isActionable: Optional[bool] = True
    recommendation: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class NutrientIntakeTrend(BaseModel):
    """Model for nutrient intake trend analysis."""
    
    nutrient: str  # 'calories', 'protein', 'carbs', 'fat', etc.
    average: float
    min: float
    max: float
    trend: str  # 'increasing', 'decreasing', 'stable', 'fluctuating'
    dataPoints: int
    recommendedIntake: Optional[float] = None
    percentOfRecommended: Optional[float] = None

class MealPatternAnalysis(BaseModel):
    """Model for meal pattern analysis."""
    
    mealType: str  # 'breakfast', 'lunch', 'dinner', 'snack'
    frequency: float  # percentage of days with this meal
    averageCalories: float
    commonFoods: List[Dict[str, Any]]
    nutrientBreakdown: Dict[str, float]
    timePattern: Optional[Dict[str, Any]] = None

class NutritionAnalysis(BaseModel):
    """Model for comprehensive nutrition analysis."""
    
    userId: int
    period: Dict[str, date]  # start and end dates
    dailyAverages: Dict[str, float]
    calorieIntakeTrend: NutrientIntakeTrend
    proteinIntakeTrend: NutrientIntakeTrend
    carbIntakeTrend: NutrientIntakeTrend
    fatIntakeTrend: NutrientIntakeTrend
    mealPatterns: Dict[str, MealPatternAnalysis]
    dietaryBalance: Dict[str, Any]
    nutritionalGaps: List[Dict[str, Any]]
    positivePatterns: List[Dict[str, Any]]