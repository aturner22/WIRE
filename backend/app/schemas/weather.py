"""Weather data schemas."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class WeatherDataSchema(BaseModel):
    """Schema for raw weather data."""
    location_id: str
    timestamp: datetime
    data_type: str  # 'current', 'hourly', 'daily'
    raw_data: Dict[str, Any]
