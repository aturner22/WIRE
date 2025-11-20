"""
Heat Stress hazard calculation module.

Implements NOAA Heat Index methodology for calculating heat stress risk.
Citation: Rothfusz, L.P. (1990). "The Heat Index Equation", NWS Technical Attachment SR 90-23
"""
from typing import Dict, Any
from .base import BaseHazard, HazardResult


class HeatStress(BaseHazard):
    """
    Heat Stress risk calculator using NOAA Heat Index.

    Calculates apparent temperature based on air temperature and relative humidity,
    then maps to risk levels calibrated for vulnerable populations.
    """

    hazard_type = "heat_stress"
    name = "Heat Stress"
    description = "Risk of heat-related illness including heat exhaustion and heat stroke"

    citation = {
        "title": "Heat illness during working and preventive considerations from body fluid homeostasis",
        "authors": "Kamijo, Y., Nose, H.",
        "year": 2006,
        "journal": "Industrial Health",
        "publication": "Volume 44, Issue 3, Pages 345-358",
        "url": "https://www.jstage.jst.go.jp/article/indhealth/44/3/44_3_345/_article",
        "doi": "10.2486/indhealth.44.345",
        "methodology_location": "Section 2-3: Thermoregulatory responses during heat exposure and age-related thermoregulation decline. Discusses heat stress thresholds for vulnerable populations including elderly, with emphasis on temperature-humidity interactions and dehydration risk.",
        "additional": "Heat Index calculation uses Rothfusz (1990) NWS equation validated by Anderson et al. (2013) 'Methods to calculate the heat index as an exposure metric in environmental health research' Environmental Health Perspectives 121(10):1111-1119, doi:10.1289/ehp.1206273"
    }

    # Risk thresholds in Celsius (Heat Index values)
    THRESHOLDS = {
        1: 27,  # Low: < 27°C
        2: 32,  # Moderate: 27-32°C
        3: 39,  # High: 32-39°C
        4: 51,  # Very High: 39-51°C
        5: float('inf'),  # Extreme: > 51°C
    }

    def calculate(self, weather_data: Dict[str, Any]) -> HazardResult:
        """
        Calculate heat stress risk from weather data.

        Args:
            weather_data: Dictionary containing temperature and humidity

        Returns:
            HazardResult with heat stress assessment
        """
        # Extract temperature and humidity
        temp = self.extract_nested(weather_data, "main.temp")
        humidity = self.extract_nested(weather_data, "main.humidity")

        # Validate required data
        if temp is None or humidity is None:
            raise ValueError(f"Missing required data for {self.name}: temperature or humidity")

        # Calculate Heat Index
        heat_index = self._calculate_heat_index(temp, humidity)

        # Calculate risk score
        score = self._calculate_risk_score(heat_index)

        # Get risk level
        risk_level = self.get_risk_level(score)

        # Generate factors
        factors = {
            "temperature_c": round(temp, 1),
            "relative_humidity_percent": round(humidity, 1),
            "heat_index_c": round(heat_index, 1),
            "feels_like_c": round(self.extract_nested(weather_data, "main.feels_like", temp), 1),
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(score, heat_index)

        return HazardResult(
            hazard_type=self.hazard_type,
            name=self.name,
            score=score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            citation=self.citation,
            confidence=0.95 if temp > 15 else 0.85,  # Higher confidence in warm weather
        )

    def _calculate_heat_index(self, temp_c: float, humidity: float) -> float:
        """
        Calculate Heat Index using Rothfusz regression equation.

        This is the NOAA/NWS standard Heat Index calculation.

        Args:
            temp_c: Air temperature in Celsius
            humidity: Relative humidity as percentage (0-100)

        Returns:
            Heat Index in Celsius
        """
        # Convert to Fahrenheit for the formula
        temp_f = (temp_c * 9/5) + 32

        # Simple formula for lower temperatures
        if temp_f < 80:
            return temp_c

        # Rothfusz regression equation
        hi = -42.379 + \
             2.04901523 * temp_f + \
             10.14333127 * humidity - \
             0.22475541 * temp_f * humidity - \
             6.83783e-3 * temp_f**2 - \
             5.481717e-2 * humidity**2 + \
             1.22874e-3 * temp_f**2 * humidity + \
             8.5282e-4 * temp_f * humidity**2 - \
             1.99e-6 * temp_f**2 * humidity**2

        # Adjustments for extreme conditions
        if humidity < 13 and 80 <= temp_f <= 112:
            adjustment = ((13 - humidity) / 4) * ((17 - abs(temp_f - 95)) / 17)**0.5
            hi -= adjustment
        elif humidity > 85 and 80 <= temp_f <= 87:
            adjustment = ((humidity - 85) / 10) * ((87 - temp_f) / 5)
            hi += adjustment

        # Convert back to Celsius
        hi_c = (hi - 32) * 5/9

        return hi_c

    def _calculate_risk_score(self, heat_index: float) -> int:
        """
        Map Heat Index to 1-5 risk scale.

        Thresholds are calibrated for vulnerable populations (elderly, children).

        Args:
            heat_index: Heat Index in Celsius

        Returns:
            Risk score from 1-5
        """
        if heat_index < self.THRESHOLDS[1]:
            return 1
        elif heat_index < self.THRESHOLDS[2]:
            return 2
        elif heat_index < self.THRESHOLDS[3]:
            return 3
        elif heat_index < self.THRESHOLDS[4]:
            return 4
        else:
            return 5

    def _generate_recommendations(self, score: int, heat_index: float) -> list[str]:
        """
        Generate actionable recommendations based on risk level.

        Args:
            score: Risk score (1-5)
            heat_index: Heat Index value

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if score == 1:
            recommendations = [
                "Normal conditions",
                "Standard hydration practices apply",
                "Comfortable for outdoor activities",
            ]
        elif score == 2:
            recommendations = [
                "Warm conditions developing",
                "Consider increased fluid availability",
                "Monitor comfort levels during outdoor activities",
                "Ensure adequate ventilation in indoor spaces",
            ]
        elif score == 3:
            recommendations = [
                "Hot conditions: outdoor exposure may be uncomfortable",
                "Hydration becomes important for vulnerable individuals",
                "Air conditioning recommended for comfort",
                "Outdoor activities may need to be shortened",
                "Watch for early signs of heat discomfort (flushing, excessive sweating)",
            ]
        elif score == 4:
            recommendations = [
                "Very hot conditions - significant heat stress risk",
                "Outdoor activities may pose health risks",
                "Cooling systems become important for vulnerable persons",
                "Close attention to hydration status recommended",
                "Heat exhaustion becomes a concern (symptoms: weakness, dizziness, nausea)",
            ]
        else:  # score == 5
            recommendations = [
                "Extreme heat - dangerous conditions for vulnerable populations",
                "Outdoor exposure poses serious health risks",
                "Cooling systems essential for safety",
                "Heat stroke risk elevated (symptoms: confusion, rapid pulse, loss of consciousness)",
                "Medical emergency planning may be prudent",
            ]

        return recommendations
