"""
Hazard Calculator Service - Orchestrates all hazard modules.

Fetches weather data and calculates all hazard risk scores.
"""
import logging
from typing import Dict, Any, List, Optional
from .weather_service import weather_service
from .hazards.base import HazardResult
from .hazards.heat_stress import HeatStress
from .hazards.cold_exposure import ColdExposure
from .hazards.respiratory import RespiratoryRisk
from .hazards.slip_fall import SlipFallRisk
from .hazards.storm import StormRisk
from .hazards.flood import FloodRisk
from .hazards.dehydration import DehydrationRisk
from .hazards.travel import TravelRisk

# Set up logger
logger = logging.getLogger(__name__)


class HazardCalculator:
    """
    Main hazard calculator service.

    Coordinates fetching weather data and calculating all hazard risks.
    """

    def __init__(self):
        """Initialize all hazard modules."""
        self.hazard_modules = {
            "heat_stress": HeatStress(),
            "cold_exposure": ColdExposure(),
            "respiratory": RespiratoryRisk(),
            "slip_fall": SlipFallRisk(),
            "storm": StormRisk(),
            "flood": FloodRisk(),
            "dehydration": DehydrationRisk(),
            "travel": TravelRisk(),
        }

    async def calculate_all_hazards(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Calculate all hazard scores for a location.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Dictionary with all hazard results and metadata
        """
        # Fetch weather and air quality data
        weather_data = await weather_service.get_current_weather(lat, lon)
        air_quality = await weather_service.get_air_quality(lat, lon)

        # Combine data
        combined_data = {
            **weather_data,
            "air_quality": air_quality,
        }

        # Calculate each hazard
        results = {}
        errors = {}

        for hazard_type, module in self.hazard_modules.items():
            try:
                # Special handling for respiratory hazard
                if hazard_type == "respiratory":
                    result = module.calculate(combined_data)
                else:
                    result = module.calculate(weather_data)

                results[hazard_type] = self._format_hazard_result(result)
            except Exception as e:
                errors[hazard_type] = str(e)
                # Log error but continue with other hazards
                logger.error(f"Error calculating {hazard_type}: {e}", exc_info=True)

        # Calculate summary statistics
        summary = self._calculate_summary(results)

        # Extract weather summary for display
        weather_summary = {
            "temperature": weather_data.get("main", {}).get("temp"),
            "humidity": weather_data.get("main", {}).get("humidity"),
            "wind_speed": weather_data.get("wind", {}).get("speed"),
            "description": weather_data.get("weather", [{}])[0].get("description", "Unknown"),
        }

        return {
            "location": {
                "latitude": lat,
                "longitude": lon,
            },
            "timestamp": weather_data.get("dt"),
            "hazards": results,
            "summary": summary,
            "weather_data": weather_summary,
            "errors": errors if errors else None,
        }

    async def calculate_single_hazard(self, hazard_type: str, lat: float, lon: float) -> HazardResult:
        """
        Calculate a single hazard score.

        Args:
            hazard_type: Type of hazard to calculate
            lat: Latitude
            lon: Longitude

        Returns:
            HazardResult for the specified hazard

        Raises:
            ValueError: If hazard type is unknown
        """
        if hazard_type not in self.hazard_modules:
            raise ValueError(f"Unknown hazard type: {hazard_type}. Available: {list(self.hazard_modules.keys())}")

        module = self.hazard_modules[hazard_type]

        # Fetch appropriate data
        weather_data = await weather_service.get_current_weather(lat, lon)

        if hazard_type == "respiratory":
            air_quality = await weather_service.get_air_quality(lat, lon)
            combined_data = {**weather_data, "air_quality": air_quality}
            result = module.calculate(combined_data)
        else:
            result = module.calculate(weather_data)

        return result

    async def calculate_forecast_hazards(self, lat: float, lon: float, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Calculate hazard forecasts for upcoming hours.

        Args:
            lat: Latitude
            lon: Longitude
            hours: Number of hours to forecast

        Returns:
            List of hazard calculations for each forecast timestamp
        """
        # Fetch forecast data
        forecast_data = await weather_service.get_hourly_forecast(lat, lon, hours)

        # Fetch air quality forecast data
        try:
            air_quality_forecast = await weather_service.get_air_quality_forecast(lat, lon)
            aq_forecast_list = air_quality_forecast.get("list", [])
        except Exception as e:
            logger.warning(f"Unable to fetch air quality forecast: {e}. Respiratory hazard will be omitted from forecast.")
            aq_forecast_list = []

        forecast_results = []

        # Process each forecast point
        for forecast_point in forecast_data.get("list", [])[:hours // 3]:  # 3-hour intervals
            try:
                # Calculate hazards for this forecast point
                results = {}
                forecast_timestamp = forecast_point.get("dt")

                for hazard_type, module in self.hazard_modules.items():
                    try:
                        if hazard_type == "respiratory":
                            # Find matching air quality forecast point (closest timestamp)
                            if aq_forecast_list:
                                aq_point = self._find_closest_aq_forecast(forecast_timestamp, aq_forecast_list)
                                if aq_point:
                                    combined_data = {**forecast_point, "air_quality": aq_point}
                                    result = module.calculate(combined_data)
                                    results[hazard_type] = self._format_hazard_result(result)
                                else:
                                    logger.debug(f"No matching air quality data for timestamp {forecast_timestamp}")
                            # If no AQ data available, skip respiratory hazard
                        else:
                            result = module.calculate(forecast_point)
                            results[hazard_type] = self._format_hazard_result(result)
                    except Exception as e:
                        logger.error(f"Error calculating forecast {hazard_type}: {e}", exc_info=True)

                summary = self._calculate_summary(results)

                forecast_results.append({
                    "timestamp": forecast_point.get("dt"),
                    "dt_txt": forecast_point.get("dt_txt"),
                    "hazards": results,
                    "summary": summary,
                })

            except Exception as e:
                logger.error(f"Error processing forecast point: {e}", exc_info=True)
                continue

        return forecast_results

    def get_hazard_methodologies(self) -> List[Dict[str, Any]]:
        """
        Get methodology information for all hazards.

        Returns:
            List of methodology dictionaries
        """
        methodologies = []

        for hazard_type, module in self.hazard_modules.items():
            methodologies.append(module.get_methodology_info())

        return methodologies

    def get_hazard_types(self) -> List[str]:
        """
        Get list of all available hazard types.

        Returns:
            List of hazard type strings
        """
        return list(self.hazard_modules.keys())

    def _format_hazard_result(self, result: HazardResult) -> Dict[str, Any]:
        """
        Format HazardResult to dictionary.

        Args:
            result: HazardResult object

        Returns:
            Dictionary representation
        """
        return {
            "type": result.hazard_type,
            "name": result.name,
            "score": result.score,
            "risk_level": result.risk_level,
            "factors": result.factors,
            "recommendations": result.recommendations,
            "citation": result.citation,
            "confidence": result.confidence,
        }

    def _find_closest_aq_forecast(self, target_timestamp: int, aq_forecast_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find the air quality forecast point closest to the target timestamp.

        Args:
            target_timestamp: Target timestamp (Unix time)
            aq_forecast_list: List of air quality forecast data points

        Returns:
            Closest air quality forecast point, or None if list is empty
        """
        if not aq_forecast_list:
            return None

        closest_point = None
        min_diff = float('inf')

        for aq_point in aq_forecast_list:
            aq_timestamp = aq_point.get("dt")
            if aq_timestamp is not None:
                diff = abs(aq_timestamp - target_timestamp)
                if diff < min_diff:
                    min_diff = diff
                    closest_point = aq_point

        return closest_point

    def _calculate_summary(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary statistics across all hazards.

        Args:
            results: Dictionary of hazard results

        Returns:
            Summary statistics
        """
        if not results:
            return {
                "highest_risk": 0,
                "extreme_count": 0,
                "very_high_count": 0,
                "high_count": 0,
                "moderate_count": 0,
                "low_count": 0,
                "total_hazards": 0,
            }

        scores = [r["score"] for r in results.values()]

        level_counts = {
            "Low": 0,
            "Moderate": 0,
            "High": 0,
            "Very High": 0,
            "Extreme": 0,
        }

        for result in results.values():
            level = result["risk_level"]
            if level in level_counts:
                level_counts[level] += 1

        return {
            "highest_risk": max(scores) if scores else 0,
            "average_risk": round(sum(scores) / len(scores), 2) if scores else 0,
            "extreme_count": level_counts["Extreme"],
            "very_high_count": level_counts["Very High"],
            "high_count": level_counts["High"],
            "moderate_count": level_counts["Moderate"],
            "low_count": level_counts["Low"],
            "total_hazards": len(results),
            "hazards_above_moderate": level_counts["High"] + level_counts["Very High"] + level_counts["Extreme"],
        }


# Global instance
hazard_calculator = HazardCalculator()
