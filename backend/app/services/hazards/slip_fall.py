"""
Slip/Fall Risk hazard calculation module.

Implements road surface temperature prediction and wet surface detection.
Citation: UK Met Office Road Surface Temperature Prediction
"""
from typing import Dict, Any
from .base import BaseHazard, HazardResult


class SlipFallRisk(BaseHazard):
    """
    Slip/Fall Risk calculator using surface condition analysis.

    Assesses risk from ice, frost, and wet surfaces based on temperature,
    precipitation, and atmospheric conditions.
    """

    hazard_type = "slip_fall"
    name = "Slip/Fall Risk"
    description = "Risk of slips, trips, and falls due to ice, frost, or wet surfaces"

    citation = {
        "title": "A systems perspective of slip and fall accidents on icy and snowy surfaces",
        "authors": "Gao, C., Abeysekera, J., Hirvonen, M., Grönqvist, R.",
        "year": 2004,
        "journal": "Ergonomics",
        "publication": "Volume 47, Issue 5, Pages 573-598",
        "url": "https://pubmed.ncbi.nlm.nih.gov/15204304/",
        "doi": "10.1080/00140130410001658718",
        "methodology_location": "Section 3.1-3.3: Environmental factors affecting slip risk. Ice is most slippery near melting point (-2°C to +2°C) due to pressure melting creating water film. Elderly populations show 3.5 injuries per 1000 per year from ice/snow falls, with highest rates in those aged 65+.",
        "additional": "Snow on ground increases slip risk more than 3x compared to no-snow conditions. Two-thirds of women 50+ experience fractures from ice/snow falls."
    }

    def calculate(self, weather_data: Dict[str, Any]) -> HazardResult:
        """
        Calculate slip/fall risk from weather data.

        Args:
            weather_data: Dictionary containing temperature, precipitation, humidity

        Returns:
            HazardResult with slip/fall risk assessment
        """
        # Extract relevant data
        temp = self.extract_nested(weather_data, "main.temp")
        feels_like = self.extract_nested(weather_data, "main.feels_like", temp)
        humidity = self.extract_nested(weather_data, "main.humidity")

        # Precipitation data (can be rain or snow)
        rain_1h = self.extract_nested(weather_data, "rain.1h", 0)
        snow_1h = self.extract_nested(weather_data, "snow.1h", 0)
        clouds = self.extract_nested(weather_data, "clouds.all", 0)

        # Weather description
        weather_main = self.extract_nested(weather_data, "weather.0.main", "Clear")

        if temp is None:
            raise ValueError(f"Missing temperature data for {self.name}")

        # Calculate surface condition
        surface_condition = self._assess_surface_condition(
            temp, humidity, rain_1h, snow_1h, weather_main
        )

        # Calculate risk score
        score = self._calculate_risk_score(surface_condition, temp, rain_1h, snow_1h)
        risk_level = self.get_risk_level(score)

        # Generate factors
        factors = {
            "temperature_c": round(temp, 1),
            "feels_like_c": round(feels_like, 1),
            "humidity_percent": round(humidity, 1) if humidity else None,
            "surface_condition": surface_condition["condition"],
            "ice_risk": surface_condition["ice_risk"],
            "wet_surface": surface_condition["wet"],
        }

        if rain_1h > 0:
            factors["rain_1h_mm"] = round(rain_1h, 1)
        if snow_1h > 0:
            factors["snow_1h_mm"] = round(snow_1h, 1)

        # Remove None values
        factors = {k: v for k, v in factors.items() if v is not None}

        # Generate recommendations
        recommendations = self._generate_recommendations(score, surface_condition)

        return HazardResult(
            hazard_type=self.hazard_type,
            name=self.name,
            score=score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            citation=self.citation,
            confidence=0.88,  # Moderate confidence due to surface estimation
        )

    def _assess_surface_condition(self, temp: float, humidity: float,
                                   rain: float, snow: float, weather: str) -> Dict[str, Any]:
        """
        Assess surface conditions based on weather parameters.

        Args:
            temp: Air temperature
            humidity: Relative humidity
            rain: Rain in last hour
            snow: Snow in last hour
            weather: Weather condition

        Returns:
            Dictionary with surface condition assessment
        """
        ice_risk = False
        wet = False
        condition = "dry"

        # Check for precipitation
        has_precipitation = rain > 0 or snow > 0 or "rain" in weather.lower() or "drizzle" in weather.lower()

        # Ice conditions
        if temp <= 0:
            if has_precipitation or humidity > 85:
                ice_risk = True
                condition = "ice"
            elif temp < -2:
                ice_risk = True
                condition = "frost"
        elif temp <= 2 and has_precipitation:
            # Near freezing with precipitation - black ice risk
            ice_risk = True
            condition = "possible_ice"

        # Wet conditions (if not ice)
        if not ice_risk:
            if rain > 0:
                wet = True
                if rain > 5:
                    condition = "very_wet"
                else:
                    condition = "wet"
            elif snow > 0:
                wet = True
                condition = "snow"
            elif humidity > 90 or "rain" in weather.lower():
                wet = True
                condition = "damp"

        return {
            "condition": condition,
            "ice_risk": ice_risk,
            "wet": wet,
            "precipitation": has_precipitation,
        }

    def _calculate_risk_score(self, surface_condition: Dict[str, Any],
                              temp: float, rain: float, snow: float) -> int:
        """
        Calculate risk score based on surface conditions.

        Physics note: Ice is most slippery near melting point (-2°C to +2°C)
        due to pressure melting creating water film. Colder ice is less slippery.

        Args:
            surface_condition: Surface condition assessment
            temp: Temperature
            rain: Rain amount
            snow: Snow amount

        Returns:
            Risk score 1-5
        """
        condition = surface_condition["condition"]
        ice_risk = surface_condition["ice_risk"]
        wet = surface_condition["wet"]

        # Extreme conditions: Ice at melting point (most dangerous)
        # -2°C to 0°C with precipitation = maximum slip risk
        if condition == "ice" or condition == "possible_ice":
            return 5

        # Active precipitation below freezing (forming ice)
        if temp < 0 and (rain > 0 or snow > 0):
            return 5

        # High risk: Snow/very wet conditions
        if condition == "snow" or condition == "very_wet":
            return 4

        # High risk: Just above freezing (surfaces may still have ice/refreezing risk)
        if 0 < temp <= 2 and (wet or ice_risk):
            return 4

        # Moderate risk: Cold temperatures with wet surfaces (potential ice overnight)
        if condition == "wet" and temp < 5:
            return 3

        # Moderate risk: Frost present
        # Note: While colder ice has higher friction coefficient, for vulnerable
        # populations (elderly, children), ANY ice presence warrants elevated caution
        if condition == "frost":
            return 3  # Consistent elevated risk when ice/frost present

        # Low-moderate risk: Damp or wet conditions
        if condition == "damp" or (wet and temp >= 5):
            return 2

        # Minimal risk
        return 1

    def _generate_recommendations(self, score: int, surface_condition: Dict[str, Any]) -> list[str]:
        """
        Generate actionable recommendations based on slip/fall risk.

        Args:
            score: Risk score (1-5)
            surface_condition: Surface condition details

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if score == 1:
            recommendations = [
                "Low slip/fall risk",
                "Dry surfaces - normal outdoor access suitable",
                "Standard precautions apply",
            ]
        elif score == 2:
            recommendations = [
                "Slight slip risk from damp or wet surfaces",
                "Outdoor paths may be slippery in places",
                "Those with mobility issues may want extra caution",
                "Adequate lighting helps visibility of surface conditions",
            ]
        elif score == 3:
            recommendations = [
                "Moderate slip/fall risk - surfaces may be hazardous",
                "Wet or cold conditions affecting surface grip",
                "Appropriate footwear becomes important",
                "Physical support may be needed for those with mobility challenges",
                "Non-slip mats at entrances can help",
            ]
        elif score == 4:
            recommendations = [
                "High slip/fall risk - hazardous surface conditions",
                "Ice formation possible or very wet surfaces present",
                "Treatment of outdoor surfaces (salt/grit) recommended",
                "Outdoor movement poses fall risk for vulnerable persons",
                "Assistance advisable for those venturing outside",
                "Postponing non-essential outdoor activities worth considering",
            ]
        else:  # score == 5
            recommendations = [
                "Extreme slip/fall risk - ice or black ice conditions likely",
                "Outdoor surfaces extremely hazardous",
                "Surface treatment (gritting/salting) urgently needed",
                "Falls highly likely without appropriate precautions",
                "Outdoor access should be carefully evaluated",
                "Staff escort essential for any outdoor movement",
            ]

        return recommendations
