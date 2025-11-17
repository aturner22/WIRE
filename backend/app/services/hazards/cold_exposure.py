"""
Cold Exposure hazard calculation module.

Implements Wind Chill Index methodology for calculating cold exposure risk.
Citation: Environment Canada Wind Chill Calculator + NHS Cold Weather Plan
"""
from typing import Dict, Any
from .base import BaseHazard, HazardResult


class ColdExposure(BaseHazard):
    """
    Cold Exposure risk calculator using Wind Chill Index.

    Calculates apparent temperature based on air temperature and wind speed,
    then maps to risk levels calibrated for vulnerable populations.
    """

    hazard_type = "cold_exposure"
    name = "Cold Exposure"
    description = "Risk of hypothermia, frostbite, and cold-related illness"

    citation = {
        "title": "Cold exposure and winter mortality from ischaemic heart disease, cerebrovascular disease, respiratory disease, and all causes in warm and cold regions of Europe",
        "authors": "The Eurowinter Group (Keatinge, W.R., Donaldson, G.C., et al.)",
        "year": 1997,
        "journal": "The Lancet",
        "publication": "Volume 349, Issue 9062, Pages 1341-1346",
        "url": "https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(96)12338-2/fulltext",
        "doi": "10.1016/S0140-6736(96)12338-2",
        "methodology_location": "Pages 1343-1344: Table 2 shows temperature-mortality relationships; Figure 3 demonstrates wind chill effects on vulnerable populations",
        "additional": "Wind chill calculation from Osczevski & Bluestein (2005) Bulletin of the American Meteorological Society 86(10):1453-1458, doi:10.1175/BAMS-86-10-1453"
    }

    # Risk thresholds in Celsius (Wind Chill values)
    THRESHOLDS = {
        1: 10,   # Low: > 10°C
        2: 0,    # Moderate: 0-10°C
        3: -10,  # High: -10-0°C
        4: -27,  # Very High: -27 to -10°C (frostbite risk in 10-30 min)
        5: float('-inf'),  # Extreme: < -27°C (frostbite risk in <10 min)
    }

    def calculate(self, weather_data: Dict[str, Any]) -> HazardResult:
        """
        Calculate cold exposure risk from weather data.

        Args:
            weather_data: Dictionary containing temperature and wind speed

        Returns:
            HazardResult with cold exposure assessment
        """
        # Extract temperature and wind speed
        temp = self.extract_nested(weather_data, "main.temp")
        wind_speed = self.extract_nested(weather_data, "wind.speed")  # m/s

        # Validate required data
        if temp is None or wind_speed is None:
            raise ValueError(f"Missing required data for {self.name}: temperature or wind speed")

        # Convert wind speed to km/h
        wind_kmh = wind_speed * 3.6

        # Calculate Wind Chill
        wind_chill = self._calculate_wind_chill(temp, wind_kmh)

        # Calculate risk score
        score = self._calculate_risk_score(temp, wind_chill)

        # Get risk level
        risk_level = self.get_risk_level(score)

        # Generate factors
        factors = {
            "temperature_c": round(temp, 1),
            "wind_speed_kmh": round(wind_kmh, 1),
            "wind_speed_ms": round(wind_speed, 1),
            "wind_chill_c": round(wind_chill, 1),
            "feels_like_c": round(self.extract_nested(weather_data, "main.feels_like", temp), 1),
        }

        # Add frostbite timing if applicable
        if wind_chill < -27:
            factors["frostbite_time"] = "< 10 minutes"
        elif wind_chill < -10:
            factors["frostbite_time"] = "10-30 minutes"

        # Generate recommendations
        recommendations = self._generate_recommendations(score, wind_chill)

        return HazardResult(
            hazard_type=self.hazard_type,
            name=self.name,
            score=score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            citation=self.citation,
            confidence=0.95 if temp < 15 else 0.85,
        )

    def _calculate_wind_chill(self, temp_c: float, wind_kmh: float) -> float:
        """
        Calculate Wind Chill using Environment Canada formula.

        Args:
            temp_c: Air temperature in Celsius
            wind_kmh: Wind speed in km/h

        Returns:
            Wind Chill temperature in Celsius
        """
        # Wind chill only applies below 10°C and with wind > 4.8 km/h
        if temp_c > 10 or wind_kmh < 4.8:
            return temp_c

        # Environment Canada Wind Chill Index formula
        wind_chill = 13.12 + 0.6215 * temp_c - 11.37 * (wind_kmh ** 0.16) + 0.3965 * temp_c * (wind_kmh ** 0.16)

        return wind_chill

    def _calculate_risk_score(self, temp: float, wind_chill: float) -> int:
        """
        Map temperature and wind chill to 1-5 risk scale.

        Args:
            temp: Actual temperature
            wind_chill: Calculated wind chill

        Returns:
            Risk score from 1-5
        """
        # Use the lower of temp or wind_chill for risk assessment
        effective_temp = min(temp, wind_chill)

        if effective_temp >= self.THRESHOLDS[1]:
            return 1
        elif effective_temp >= self.THRESHOLDS[2]:
            return 2
        elif effective_temp >= self.THRESHOLDS[3]:
            return 3
        elif effective_temp >= self.THRESHOLDS[4]:
            return 4
        else:
            return 5

    def _generate_recommendations(self, score: int, wind_chill: float) -> list[str]:
        """
        Generate actionable recommendations based on risk level.

        Args:
            score: Risk score (1-5)
            wind_chill: Wind chill value

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if score == 1:
            recommendations = [
                "Normal precautions apply",
                "Ensure adequate heating is available",
                "Light outdoor clothing appropriate",
            ]
        elif score == 2:
            recommendations = [
                "Monitor indoor temperatures (minimum 18°C for vulnerable persons)",
                "Ensure residents have warm clothing for outdoor activities",
                "Check heating systems are functioning properly",
                "Monitor prolonged outdoor exposure",
            ]
        elif score == 3:
            recommendations = [
                "Increase indoor temperature checks",
                "Ensure all residents have winter clothing before going outside",
                "Minimize outdoor activities duration",
                "Check on vulnerable individuals frequently",
                "Ensure hot drinks and meals available",
            ]
        elif score == 4:
            recommendations = [
                "Cold warning - Enhanced precautions required",
                "Restrict outdoor activities",
                "Ensure residents in adequately heated areas",
                "Layer multiple warm clothing items for outdoor exposure",
                "Be vigilant for signs of cold and hypothermia (shivering, confusion, drowsiness)",
            ]
        else:  # score == 5
            recommendations = [
                "Extreme cold - action required",
                "Avoid outdoor activities",
                "Frostbite risk: Exposed skin freezes in under 10 minutes",
                "Continuous monitoring of all residents",
                "Prepare for potential medical emergencies",
            ]

        return recommendations
