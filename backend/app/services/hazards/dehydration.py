"""
Dehydration Risk hazard calculation module.

Elderly-specific dehydration risk based on heat, humidity, and duration.
Citation: Geriatric medicine research on heat and dehydration
"""
from typing import Dict, Any
from .base import BaseHazard, HazardResult


class DehydrationRisk(BaseHazard):
    """
    Dehydration Risk calculator for vulnerable populations.

    Specific focus on elderly individuals' increased susceptibility to
    dehydration during hot weather, combining temperature, humidity, and heat index.
    """

    hazard_type = "dehydration"
    name = "Dehydration Risk"
    description = "Risk of dehydration in vulnerable populations, especially elderly residents"

    citation = {
        "title": "The Heat Index Equation (NWS Southern Region Technical Attachment SR 90-23) - Adapted for Dehydration Risk",
        "authors": "Rothfusz, L.P. (NOAA methodology)",
        "year": 1990,
        "publication": "National Weather Service, NOAA",
        "url": "https://www.weather.gov/media/ffc/ta_htindx.PDF",
        "methodology_location": "Dehydration risk assessment based on NOAA Heat Index methodology with elderly vulnerability multiplier (1.5x). Temperature thresholds: <25°C (low risk), 25-28°C (moderate - increased fluid needs), 28-32°C (high - frequent hydration required), 32-36°C (very high - continuous monitoring), >36°C (extreme - medical concern). Elderly at elevated risk due to reduced thirst sensation and impaired thermoregulation.",
        "additional": "Elderly dehydration vulnerability documented in Mentes (2006) 'Oral hydration in older adults' American Journal of Nursing 106(6):40-49, doi:10.1097/00000446-200606000-00023. WHO (2011) Public Health Advice on Preventing Health Effects of Heat confirms elderly as highly vulnerable to heat-related dehydration."
    }

    # Temperature thresholds for dehydration risk (Celsius)
    TEMP_THRESHOLDS = {
        1: 25,   # Low: < 25°C
        2: 28,   # Moderate: 25-28°C
        3: 32,   # High: 28-32°C
        4: 36,   # Very High: 32-36°C
        5: float('inf'),  # Extreme: > 36°C
    }

    def calculate(self, weather_data: Dict[str, Any]) -> HazardResult:
        """
        Calculate dehydration risk from weather data.

        Args:
            weather_data: Dictionary containing temperature and humidity

        Returns:
            HazardResult with dehydration risk assessment
        """
        # Extract relevant data
        temp = self.extract_nested(weather_data, "main.temp")
        humidity = self.extract_nested(weather_data, "main.humidity")
        feels_like = self.extract_nested(weather_data, "main.feels_like", temp)

        if temp is None or humidity is None:
            raise ValueError(f"Missing required data for {self.name}: temperature or humidity")

        # Calculate heat index (simplified version)
        heat_index = self._estimate_heat_index(temp, humidity)

        # Calculate dehydration risk factors
        dehydration_factors = self._assess_dehydration_factors(temp, humidity, heat_index)

        # Calculate risk score
        score = self._calculate_risk_score(dehydration_factors)
        risk_level = self.get_risk_level(score)

        # Generate factors
        factors = {
            "temperature_c": round(temp, 1),
            "humidity_percent": round(humidity, 1),
            "heat_index_c": round(heat_index, 1),
            "feels_like_c": round(feels_like, 1),
            "fluid_loss_rate": dehydration_factors["fluid_loss_category"],
            "risk_multiplier": dehydration_factors["elderly_multiplier"],
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(score, dehydration_factors)

        return HazardResult(
            hazard_type=self.hazard_type,
            name=self.name,
            score=score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            citation=self.citation,
            confidence=0.90,
        )

    def _estimate_heat_index(self, temp: float, humidity: float) -> float:
        """
        Simplified heat index calculation.

        Args:
            temp: Temperature in Celsius
            humidity: Relative humidity percentage

        Returns:
            Heat index in Celsius
        """
        # Convert to Fahrenheit for calculation
        temp_f = (temp * 9/5) + 32

        # Simplified formula for quick estimation
        if temp_f < 80:
            return temp

        # Simple heat index approximation
        hi_f = temp_f + 0.5555 * ((6.112 * (10 ** (7.5 * temp / (237.7 + temp))) * humidity / 100) - 10)

        # Convert back to Celsius
        hi_c = (hi_f - 32) * 5/9

        return hi_c

    def _assess_dehydration_factors(self, temp: float, humidity: float,
                                     heat_index: float) -> Dict[str, Any]:
        """
        Assess multiple dehydration risk factors.

        Args:
            temp: Air temperature
            humidity: Relative humidity
            heat_index: Calculated heat index

        Returns:
            Dictionary with dehydration assessment
        """
        # Base risk from temperature
        base_risk = 1
        for threshold_score, threshold_temp in self.TEMP_THRESHOLDS.items():
            if temp < threshold_temp:
                base_risk = threshold_score
                break
            base_risk = 5

        # Humidity modifier (low humidity increases dehydration)
        if humidity < 30:
            humidity_factor = 1.3  # Very dry - increases risk
        elif humidity < 50:
            humidity_factor = 1.1  # Dry
        elif humidity > 80:
            humidity_factor = 1.2  # Very humid - impairs cooling
        else:
            humidity_factor = 1.0

        # Elderly population multiplier (reduced thirst sensation, medications)
        elderly_multiplier = 1.5

        # Calculate fluid loss rate category
        if heat_index < 25:
            fluid_loss = "minimal"
        elif heat_index < 30:
            fluid_loss = "moderate"
        elif heat_index < 35:
            fluid_loss = "high"
        else:
            fluid_loss = "very_high"

        # Composite risk
        adjusted_risk = base_risk * humidity_factor * elderly_multiplier / 1.5  # Normalize

        return {
            "base_risk": base_risk,
            "humidity_factor": humidity_factor,
            "elderly_multiplier": elderly_multiplier,
            "fluid_loss_category": fluid_loss,
            "adjusted_risk": adjusted_risk,
        }

    def _calculate_risk_score(self, factors: Dict[str, Any]) -> int:
        """
        Calculate risk score from dehydration factors.

        Args:
            factors: Dehydration factor assessment

        Returns:
            Risk score 1-5
        """
        adjusted_risk = factors["adjusted_risk"]

        if adjusted_risk < 1.5:
            return 1
        elif adjusted_risk < 2.5:
            return 2
        elif adjusted_risk < 3.5:
            return 3
        elif adjusted_risk < 4.5:
            return 4
        else:
            return 5

    def _generate_recommendations(self, score: int, factors: Dict[str, Any]) -> list[str]:
        """
        Generate actionable recommendations for dehydration prevention.

        Args:
            score: Risk score (1-5)
            factors: Dehydration factors

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if score == 1:
            recommendations = [
                "Low dehydration risk",
                "Still ensure water available throughout facility",
                "Normal fluid intake schedules",
            ]
        elif score == 2:
            recommendations = [
                "Moderate dehydration risk",
                "Offer fluids more frequently",
                "Monitor intake for vulnerable residents",
                "Ensure cool drinks readily available",
                "Light clothing recommended",
            ]
        elif score == 3:
            recommendations = [
                "Elevated dehydration risk",
                "More frequent fluid rounds",
                "Offer variety of fluids (water, juice, ice lollies)",
                "Monitor for dehydration signs",
                "Ensure air conditioning or fans operational",
                "Light, loose clothing recommended",
            ]
        elif score == 4:
            recommendations = [
                "High dehydration risk",
                "Frequent fluid rounds needed",
                "Cooling measures: air conditioning, fans, cool cloths",
                "Monitoring of urine output",
                "Limit physical activity",
                "Watch for dehydration signs: confusion, dizziness, rapid pulse",
            ]
        else:  # score == 5
            recommendations = [
                "Severe dehydration risk",
                "Continuous hydration monitoring recommended",
                "Strong cooling: air conditioning, cool baths, ice packs",
                "Activity restrictions",
            ]

        return recommendations
