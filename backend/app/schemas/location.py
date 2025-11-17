"""Location schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional


class LocationSearch(BaseModel):
    """Schema for location search results from geocoding."""
    name: str = Field(..., description="Location display name")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    country: str = Field(..., description="Country code")
    state: Optional[str] = Field(None, description="State/region name")

    class Config:
        from_attributes = True
