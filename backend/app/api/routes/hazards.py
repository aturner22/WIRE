"""Hazard assessment API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.schemas.hazard import AllHazardsResponse, HazardResultSchema, HazardForecastPoint
from app.services.hazard_calculator import hazard_calculator

router = APIRouter()


@router.get("/hazards/forecast")
async def get_forecast_by_coordinates(
    lat: float = Query(..., ge=-90, le=90, description="Latitude (-90 to 90)"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude (-180 to 180)"),
    name: str = Query("Unknown Location", description="Location name"),
    hours: int = Query(120, ge=3, le=120, description="Forecast hours (3-120)")
):
    """
    Get hazard forecast for coordinates.

    This endpoint provides forecast hazard assessments for care home planning:
    - 24 hours: Operational decisions (gritting, staffing)
    - 48 hours: Medical appointment scheduling
    - 120 hours (5 days): Supply planning, strategic decisions

    Args:
        lat: Latitude
        lon: Longitude
        name: Location name (optional)
        hours: Forecast horizon in hours

    Returns:
        Forecast hazard assessments with timing recommendations

    Example:
        /api/v1/hazards/forecast?lat=51.5074&lon=-0.1278&name=London&hours=120
    """
    try:
        result = await hazard_calculator.calculate_forecast_hazards(
            lat=lat,
            lon=lon,
            hours=hours
        )

        return {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "name": name
            },
            "forecast_hours": hours,
            "forecasts": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate forecast: {str(e)}"
        )


@router.get("/types")
async def get_hazard_types():
    """
    Get list of all hazard types supported by the system.

    Returns:
        List of hazard types with descriptions
    """
    types = hazard_calculator.get_hazard_types()
    return types


@router.get("/methodologies")
async def get_methodologies():
    """
    Get all hazard calculation methodologies.

    Returns detailed information about each hazard calculation methodology,
    including academic citations and references.

    Returns:
        List of methodology objects with citations
    """
    methodologies = hazard_calculator.get_hazard_methodologies()
    return methodologies


@router.get("/methodologies/{hazard_type}")
async def get_methodology(hazard_type: str):
    """
    Get methodology for a specific hazard type.

    Args:
        hazard_type: Type of hazard (e.g., 'heat_stress', 'cold_exposure')

    Returns:
        Methodology object with citations

    Raises:
        HTTPException: If hazard type not found
    """
    methodologies = hazard_calculator.get_hazard_methodologies()

    for methodology in methodologies:
        if methodology["hazard_type"] == hazard_type:
            return methodology

    raise HTTPException(status_code=404, detail="Hazard type not found")


@router.get("/hazards", response_model=AllHazardsResponse)
async def get_hazards_by_coordinates(
    lat: float = Query(..., ge=-90, le=90, description="Latitude (-90 to 90)"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude (-180 to 180)"),
    name: str = Query("Unknown Location", description="Location name")
):
    """
    Get current hazard scores for coordinates.

    This endpoint calculates hazards directly from coordinates.

    Args:
        lat: Latitude
        lon: Longitude
        name: Location name (optional)

    Returns:
        All current hazard assessments

    Raises:
        HTTPException: If calculation fails
    """
    try:
        # Calculate all hazards directly
        result = await hazard_calculator.calculate_all_hazards(
            lat=lat,
            lon=lon
        )

        # Add location name if not in result
        if "location_name" not in result:
            result["location_name"] = name

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate hazards: {str(e)}"
        )
