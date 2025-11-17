"""Location management API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.schemas.location import LocationSearch
from app.services.weather_service import weather_service

router = APIRouter()


@router.get("/search", response_model=List[LocationSearch])
async def search_locations(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(5, ge=1, le=10)
):
    """
    Search for locations using OpenWeather geocoding API.

    Args:
        q: Search query (city name, address, etc.)
        limit: Maximum number of results

    Returns:
        List of matching locations
    """
    try:
        results = await weather_service.geocode_location(q, limit)

        return [
            LocationSearch(
                name=f"{r.get('name', '')}, {r.get('country', '')}",
                latitude=r.get('lat'),
                longitude=r.get('lon'),
                country=r.get('country'),
                state=r.get('state'),
            )
            for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding failed: {str(e)}")
