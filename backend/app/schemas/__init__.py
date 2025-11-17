"""Pydantic schemas for API requests and responses."""
from .location import LocationSearch
from .hazard import (
    HazardResultSchema,
    AllHazardsResponse,
    HazardForecastPoint,
)

__all__ = [
    "LocationSearch",
    "HazardResultSchema",
    "AllHazardsResponse",
    "HazardForecastPoint",
]
