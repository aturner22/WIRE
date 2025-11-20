"""
Wind Hazard calculation module.

Implements Beaufort Scale and mobility impact assessment for high winds.
Citation: UK Met Office Wind Impact Guidance
"""
from typing import Dict, Any
from .base import BaseHazard, HazardResult


class WindHazard(BaseHazard):
    """
    Wind Hazard calculator using modified Beaufort Scale.

    Assesses risk from high winds affecting mobility aids, outdoor equipment,
    and general safety for vulnerable populations.
    """

    hazard_type = "wind"
    name = "Wind Hazard"
    description = "Risk from high winds affecting mobility, outdoor safety, and building hazards"

    citation = {
        "title": "Towards rules of thumb for wind comfort and air quality",
        "authors": "Bottema, M.",
        "year": 1999,
        "journal": "Atmospheric Environment",
        "publication": "Volume 33, Issue 24, Pages 4009-4017",
        "url": "https://www.sciencedirect.com/science/article/pii/S1352231099001429",
        "doi": "10.1016/S1352-2310(99)00142-9",
        "methodology_location": "Pages 4010-4012: Wind speed thresholds for pedestrian comfort and safety. Establishes criteria for acceptable wind conditions in urban planning with consideration for vulnerable populations including elderly and mobility-impaired individuals.",
        "additional": "Beaufort Wind Scale (UK Met Office): Force 5 (39 km/h) - moderate breeze, Force 7 (62 km/h) - near gale, Force 9 (88 km/h) - strong gale. Thresholds calibrated for elderly pedestrian safety and mobility aid users.",
    }

    # Wind speed thresholds in km/h (based on gust speeds)
    # Aligned with Beaufort Wind Scale adapted for vulnerable populations
    THRESHOLDS = {
        1: 20,   # Low: < 20 km/h (Beaufort 1-3: light air to gentle breeze)
        2: 39,   # Moderate: 20-39 km/h (Beaufort 4-5: moderate to fresh breeze)
        3: 62,   # High: 39-62 km/h (Beaufort 6-7: strong breeze to near gale)
        4: 75,   # Very High: 62-75 km/h (Beaufort 8-9: gale to strong gale)
        5: float('inf'),  # Extreme: > 75 km/h (Beaufort 10+: storm to hurricane force)
    }

    def calculate(self, weather_data: Dict[str, Any]) -> HazardResult:
        """
        Calculate wind hazard risk from weather data.

        Args:
            weather_data: Dictionary containing wind speed and gust data

        Returns:
            HazardResult with wind hazard assessment
        """
        # Extract wind data
        wind_speed = self.extract_nested(weather_data, "wind.speed")  # m/s
        wind_gust = self.extract_nested(weather_data, "wind.gust", wind_speed)  # m/s
        wind_deg = self.extract_nested(weather_data, "wind.deg", 0)

        if wind_speed is None:
            raise ValueError(f"Missing wind speed data for {self.name}")

        # Convert to km/h
        wind_speed_kmh = wind_speed * 3.6
        wind_gust_kmh = wind_gust * 3.6 if wind_gust else wind_speed_kmh * 1.5  # Estimate if missing

        # Use the higher of sustained wind or gust for risk assessment
        max_wind = max(wind_speed_kmh, wind_gust_kmh)

        # Calculate risk score
        score = self._calculate_risk_score(max_wind)
        risk_level = self.get_risk_level(score)

        # Determine wind direction
        wind_direction = self._get_wind_direction(wind_deg)

        # Generate factors
        factors = {
            "wind_speed_kmh": round(wind_speed_kmh, 1),
            "wind_speed_ms": round(wind_speed, 1),
            "wind_gust_kmh": round(wind_gust_kmh, 1),
            "wind_direction": wind_direction,
            "wind_degrees": round(wind_deg, 0),
            "beaufort_scale": self._get_beaufort_scale(max_wind),
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(score, max_wind)

        return HazardResult(
            hazard_type=self.hazard_type,
            name=self.name,
            score=score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            citation=self.citation,
            confidence=0.92,
        )

    def _calculate_risk_score(self, wind_kmh: float) -> int:
        """
        Map wind speed to 1-5 risk scale.

        Args:
            wind_kmh: Wind speed in km/h

        Returns:
            Risk score from 1-5
        """
        if wind_kmh < self.THRESHOLDS[1]:
            return 1
        elif wind_kmh < self.THRESHOLDS[2]:
            return 2
        elif wind_kmh < self.THRESHOLDS[3]:
            return 3
        elif wind_kmh < self.THRESHOLDS[4]:
            return 4
        else:
            return 5

    def _get_beaufort_scale(self, wind_kmh: float) -> int:
        """
        Convert wind speed to Beaufort scale.

        Args:
            wind_kmh: Wind speed in km/h

        Returns:
            Beaufort scale number (0-12)
        """
        if wind_kmh < 1:
            return 0
        elif wind_kmh < 6:
            return 1
        elif wind_kmh < 12:
            return 2
        elif wind_kmh < 20:
            return 3
        elif wind_kmh < 29:
            return 4
        elif wind_kmh < 39:
            return 5
        elif wind_kmh < 50:
            return 6
        elif wind_kmh < 62:
            return 7
        elif wind_kmh < 75:
            return 8
        elif wind_kmh < 89:
            return 9
        elif wind_kmh < 103:
            return 10
        elif wind_kmh < 118:
            return 11
        else:
            return 12

    def _get_wind_direction(self, degrees: float) -> str:
        """
        Convert wind degrees to compass direction.

        Args:
            degrees: Wind direction in degrees (0-360)

        Returns:
            Compass direction string
        """
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(degrees / 22.5) % 16
        return directions[index]

    def _generate_recommendations(self, score: int, _wind_kmh: float) -> list[str]:
        """
        Generate actionable recommendations based on wind conditions.

        Args:
            score: Risk score (1-5)
            wind_kmh: Wind speed in km/h

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if score == 1:
            recommendations = [
                "Normal wind conditions",
                "No wind-related concerns",
                "Comfortable for all outdoor activities",
            ]
        elif score == 2:
            recommendations = [
                "Moderate winds present",
                "Lightweight outdoor items may be displaced",
                "Those using mobility aids may experience mild difficulty",
                "Loose debris may be blown around",
            ]
        elif score == 3:
            recommendations = [
                "Strong winds affecting outdoor conditions",
                "Outdoor furniture and equipment at risk of displacement",
                "Mobility aids (walking frames, wheelchairs) may be difficult to control",
                "Areas near trees may have falling branches",
                "Outdoor activities may be uncomfortable for frail individuals",
            ]
        elif score == 4:
            recommendations = [
                "Gale force winds creating hazardous conditions",
                "Outdoor movement poses safety risk",
                "Mobility aids will be very difficult or unsafe to use outdoors",
                "Outdoor equipment requires securing",
                "Building materials (tiles, gutters) could become loose",
                "Power outages are possible",
            ]
        else:  # score == 5
            recommendations = [
                "Storm force winds: extremely dangerous conditions",
                "Outdoor activities pose serious safety risk",
                "Windows and external building areas may be hazardous",
                "Power outages and structural damage are possible",
                "Emergency services may be limited",
            ]

        return recommendations
