"""
Storm/Severe Weather hazard calculation module.

Implements composite severe weather risk assessment.
Citation: Storm severity indices from meteorological research
"""
from typing import Dict, Any
from .base import BaseHazard, HazardResult


class StormRisk(BaseHazard):
    """
    Storm/Severe Weather risk calculator.

    Composite assessment based on wind speed, precipitation intensity,
    pressure trends, and weather conditions.
    """

    hazard_type = "storm"
    name = "Storm/Severe Weather"
    description = "Risk from severe weather including thunderstorms, heavy rain, and extreme conditions"

    citation = {
        "title": "Guidelines on Multi-hazard Impact-based Forecast and Warning Services",
        "authors": "World Meteorological Organization (WMO)",
        "year": 2015,
        "publication": "WMO-No. 1150",
        "url": "https://library.wmo.int/index.php?lvl=notice_display&id=17257",
        "methodology_location": "Chapter 4.3: Severe Weather Warning Thresholds - Wind speed thresholds (gale force >75 km/h, storm force >90 km/h), precipitation intensity classifications (heavy >15 mm/h, extreme >50 mm/h), and low pressure system indicators (<995 hPa). Section 4.5 discusses composite risk assessment for vulnerable populations.",
        "additional": "Beaufort Wind Scale (UK Met Office) for wind severity classification and National Weather Service severe weather criteria",
    }

    def calculate(self, weather_data: Dict[str, Any]) -> HazardResult:
        """
        Calculate storm/severe weather risk from weather data.

        Args:
            weather_data: Dictionary containing weather parameters

        Returns:
            HazardResult with storm risk assessment
        """
        # Extract meteorological parameters
        pressure = self.extract_nested(weather_data, "main.pressure")
        wind_speed_ms = self.extract_nested(weather_data, "wind.speed", 0)
        wind_speed = wind_speed_ms * 3.6  # Convert to km/h
        wind_gust_ms = self.extract_nested(weather_data, "wind.gust", wind_speed_ms * 1.5)  # Estimate if not provided
        wind_gust = wind_gust_ms * 3.6
        rain_1h = self.extract_nested(weather_data, "rain.1h", 0)
        rain_3h = self.extract_nested(weather_data, "rain.3h", rain_1h * 3)
        clouds = self.extract_nested(weather_data, "clouds.all", 0)
        weather_main = self.extract_nested(weather_data, "weather.0.main", "")
        weather_desc = self.extract_nested(weather_data, "weather.0.description", "")

        # Calculate composite storm indicators
        storm_indicators = self._assess_storm_indicators(
            pressure, wind_speed, wind_gust, rain_1h, clouds, weather_main, weather_desc
        )

        # Calculate risk score
        score = self._calculate_risk_score(storm_indicators)
        risk_level = self.get_risk_level(score)

        # Generate factors
        factors = {
            "wind_gust_kmh": round(wind_gust, 1),
            "precipitation_rate_mmh": round(rain_1h, 1),
            "pressure_hpa": round(pressure, 1) if pressure else None,
            "cloud_cover_percent": round(clouds, 0),
            "weather_condition": weather_main,
            "storm_score": storm_indicators["score"],
            "active_warnings": storm_indicators["warnings"],
        }

        # Remove None values
        factors = {k: v for k, v in factors.items() if v is not None}

        # Generate recommendations
        recommendations = self._generate_recommendations(score, storm_indicators)

        return HazardResult(
            hazard_type=self.hazard_type,
            name=self.name,
            score=score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            citation=self.citation,
            confidence=0.85,
        )

    def _assess_storm_indicators(self, pressure: float, wind_speed: float, wind_gust: float,
                                  rain_rate: float, clouds: int, weather_main: str,
                                  weather_desc: str) -> Dict[str, Any]:
        """
        Assess multiple storm indicators and combine into composite score.

        Args:
            pressure: Atmospheric pressure
            wind_speed: Sustained wind speed (km/h)
            wind_gust: Wind gust speed (km/h)
            rain_rate: Precipitation rate (mm/h)
            clouds: Cloud cover percentage
            weather_main: Primary weather condition
            weather_desc: Detailed weather description

        Returns:
            Dictionary with storm assessment
        """
        warnings = []
        component_scores = []

        # Wind component
        if wind_gust > 90:
            component_scores.append(5)
            warnings.append("Storm force winds")
        elif wind_gust > 75:
            component_scores.append(4)
            warnings.append("Gale force winds")
        elif wind_gust > 50:
            component_scores.append(3)
            warnings.append("Strong winds")
        elif wind_gust > 30:
            component_scores.append(2)
        else:
            component_scores.append(1)

        # Precipitation component
        if rain_rate > 50:
            component_scores.append(5)
            warnings.append("Extreme rainfall")
        elif rain_rate > 30:
            component_scores.append(4)
            warnings.append("Heavy rainfall")
        elif rain_rate > 15:
            component_scores.append(3)
            warnings.append("Moderate rainfall")
        elif rain_rate > 5:
            component_scores.append(2)
        else:
            component_scores.append(1)

        # Pressure component (low pressure systems)
        # Note: Normal sea-level pressure is ~1013 hPa
        # Only flag significant low pressure systems
        if pressure and pressure < 980:
            component_scores.append(4)
            warnings.append("Low pressure system")
        elif pressure and pressure < 995:
            component_scores.append(3)
        elif pressure and pressure < 1005:
            component_scores.append(2)
        else:
            component_scores.append(1)

        # Weather type component
        weather_lower = (weather_main + " " + weather_desc).lower()
        if "thunderstorm" in weather_lower or "tornado" in weather_lower:
            component_scores.append(5)
            warnings.append("Thunderstorm activity")
        elif "squall" in weather_lower or "storm" in weather_lower:
            component_scores.append(4)
            warnings.append("Storm conditions")
        elif "heavy" in weather_lower:
            component_scores.append(3)

        # Composite score (weighted average, max emphasis)
        if component_scores:
            avg_score = sum(component_scores) / len(component_scores)
            max_score = max(component_scores)
            # Weighted: 70% max, 30% average
            composite_score = 0.7 * max_score + 0.3 * avg_score
        else:
            composite_score = 1.0

        return {
            "score": composite_score,
            "warnings": warnings,
            "wind_component": component_scores[0] if len(component_scores) > 0 else 1,
            "rain_component": component_scores[1] if len(component_scores) > 1 else 1,
            "pressure_component": component_scores[2] if len(component_scores) > 2 else 1,
        }

    def _calculate_risk_score(self, indicators: Dict[str, Any]) -> int:
        """
        Map composite storm score to 1-5 risk scale.

        Args:
            indicators: Storm indicator assessment

        Returns:
            Risk score from 1-5
        """
        score = indicators["score"]

        if score >= 4.5:
            return 5
        elif score >= 3.5:
            return 4
        elif score >= 2.5:
            return 3
        elif score >= 1.5:
            return 2
        else:
            return 1

    def _generate_recommendations(self, score: int, indicators: Dict[str, Any]) -> list[str]:
        """
        Generate actionable recommendations based on storm risk.

        Args:
            score: Risk score (1-5)
            indicators: Storm indicators

        Returns:
            List of recommendation strings
        """
        warnings = indicators.get("warnings", [])
        recommendations = []

        if score == 1:
            recommendations = [
                "Normal weather conditions",
                "No storm-related concerns",
            ]
        elif score == 2:
            recommendations = [
                "Unsettled weather conditions developing",
                "Monitoring weather updates may be helpful",
                "Lightweight outdoor items may be at risk of displacement",
            ]
        elif score == 3:
            recommendations = [
                "Severe weather conditions possible",
                "Outdoor furniture and equipment may be displaced by wind",
                "Outdoor activities may become uncomfortable or unsafe",
                "Power interruptions could occur",
                "Weather warnings may be issued for the area",
            ]
            if warnings:
                recommendations.insert(0, f"Current conditions: {', '.join(warnings)}")

        elif score == 4:
            recommendations = [
                "Severe weather conditions likely",
                "Strong winds pose risk to outdoor items and potentially windows",
                "Outdoor activities pose safety risks",
                "Power outages are possible",
                "Emergency services response may be affected",
                "Official weather warnings likely in effect",
            ]
            if warnings:
                recommendations.insert(0, f"Active weather conditions: {', '.join(warnings)}")

        else:  # score == 5
            recommendations = [
                "Extreme weather conditions present or imminent",
                "Outdoor exposure poses serious safety risks",
                "Windows and external building areas may be hazardous",
                "Power loss and structural damage are possible",
                "Emergency services may be severely limited",
                "Building integrity could be compromised in worst cases",
                "This represents the highest level of weather risk",
            ]
            if warnings:
                recommendations.insert(0, f"Severe conditions: {', '.join(warnings)}")

        return recommendations
