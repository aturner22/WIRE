"""Hazard schemas for API responses."""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class CitationSchema(BaseModel):
    """Academic citation information."""
    title: str
    authors: str
    year: int
    journal: Optional[str] = None
    publication: Optional[str] = None
    url: Optional[str] = None
    doi: Optional[str] = None
    methodology_location: Optional[str] = None
    additional: Optional[str] = None


class HazardResultSchema(BaseModel):
    """Schema for a single hazard calculation result."""
    type: str = Field(..., description="Hazard type identifier")
    name: str = Field(..., description="Human-readable hazard name")
    score: int = Field(..., ge=1, le=5, description="Risk score (1-5)")
    risk_level: str = Field(..., description="Risk level (Low/Moderate/High/Very High/Extreme)")
    factors: Dict[str, Any] = Field(..., description="Contributing factors")
    recommendations: List[str] = Field(..., description="Actionable recommendations")
    citation: CitationSchema = Field(..., description="Academic citation")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score (0-1)")


class HazardSummarySchema(BaseModel):
    """Summary statistics across all hazards."""
    highest_risk: int = Field(..., ge=0, le=5)
    average_risk: float = Field(..., ge=0, le=5)
    extreme_count: int = Field(..., ge=0)
    very_high_count: int = Field(..., ge=0)
    high_count: int = Field(..., ge=0)
    moderate_count: int = Field(..., ge=0)
    low_count: int = Field(..., ge=0)
    total_hazards: int = Field(..., ge=0)
    hazards_above_moderate: int = Field(..., ge=0)


class LocationInfoSchema(BaseModel):
    """Location information."""
    latitude: float
    longitude: float


class WeatherDataSchema(BaseModel):
    """Weather data summary for display."""
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    description: Optional[str] = None


class AllHazardsResponse(BaseModel):
    """Response schema for all hazards calculation."""
    location: LocationInfoSchema
    timestamp: int = Field(..., description="Unix timestamp")
    hazards: Dict[str, HazardResultSchema]
    summary: HazardSummarySchema
    weather_data: Optional[WeatherDataSchema] = None
    errors: Optional[Dict[str, str]] = Field(None, description="Any errors encountered")


class HazardForecastPoint(BaseModel):
    """Single forecast point for hazards."""
    timestamp: int
    dt_txt: Optional[str] = None
    hazards: Dict[str, HazardResultSchema]
    summary: HazardSummarySchema


class HazardMethodologySchema(BaseModel):
    """Schema for hazard methodology information."""
    hazard_type: str
    name: str
    description: str
    citation: CitationSchema
