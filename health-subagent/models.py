"""
Data models for the Health Sub-Agent.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class HealthData(BaseModel):
    """Model for health data points."""
    
    id: Optional[int] = None
    dataType: str
    date: date
    value: float
    unit: Optional[str] = None
    metadata: Optional[str] = None
    source: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class Insight(BaseModel):
    """Model for health insights."""
    
    id: Optional[int] = None
    category: str
    title: str
    description: str
    severity: Optional[int] = Field(None, ge=1, le=5)
    isActionable: Optional[bool] = True
    recommendation: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class TrendAnalysis(BaseModel):
    """Model for trend analysis results."""
    
    average: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    trend: str  # 'increasing', 'decreasing', 'stable', 'insufficient_data'
    data_points: int

class StepsAnalysis(BaseModel):
    """Model for steps data analysis."""
    
    trend_analysis: TrendAnalysis
    goal_achievement_rate: float
    unusual_days: List[Dict[str, Any]]

class SleepAnalysis(BaseModel):
    """Model for sleep data analysis."""
    
    trend_analysis: TrendAnalysis
    goal_achievement_rate: float
    sleep_consistency: Dict[str, Any]
    unusual_days: List[Dict[str, Any]]

class HeartRateAnalysis(BaseModel):
    """Model for heart rate data analysis."""
    
    trend_analysis: TrendAnalysis
    resting_heart_rate: Dict[str, Any]
    heart_rate_zones: Dict[str, Any]
    unusual_patterns: List[Dict[str, Any]]
