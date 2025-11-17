"""
Flood Risk hazard calculation module.

Implements precipitation accumulation analysis for flooding risk.
Citation: Flood risk assessment methodologies
"""
from typing import Dict, Any
from .base import BaseHazard, HazardResult


class FloodRisk(BaseHazard):
    """
    Flood Risk calculator using precipitation accumulation.

    Assesses flooding risk based on rainfall intensity and accumulation.
    """

    hazard_type = "flood"
    name = "Flood Risk"
    description = "Risk of flooding affecting facility access and operations"

    citation = {
        "title": "Rainfall intensity–duration thresholds for the initiation of urban drainage flash floods",
        "authors": "Versini, P.A., Gaume, E., Andrieu, H.",
        "year": 2010,
        "journal": "Journal of Hydrology",
        "publication": "Volume 394, Issues 3-4, Pages 421-429",
        "url": "https://www.sciencedirect.com/science/article/pii/S0022169410005445",
        "doi": "10.1016/j.jhydrol.2010.10.005",
        "methodology_location": "Pages 424-426: Rainfall intensity-duration thresholds for urban flash flooding; Figure 4 and Table 2 show critical precipitation rates for different accumulation periods",
        "additional": "Jonkman & Kelman (2005) 'An analysis of the causes and circumstances of flood disaster deaths' Disasters 29(1):75-97, doi:10.1111/j.0361-3666.2005.00275.x for vulnerability assessment",
    }

    # Precipitation rate thresholds (mm/hour)
    RATE_THRESHOLDS = {
        1: 2.5,   # Low: < 2.5 mm/h (light rain)
        2: 10,    # Moderate: 2.5-10 mm/h (moderate rain)
        3: 30,    # High: 10-30 mm/h (heavy rain)
        4: 50,    # Very High: 30-50 mm/h (very heavy rain)
        5: float('inf'),  # Extreme: > 50 mm/h (extreme rain)
    }

    # 24-hour accumulation thresholds (mm)
    ACCUMULATION_THRESHOLDS = {
        1: 10,
        2: 25,
        3: 50,
        4: 100,
        5: float('inf'),
    }

    def calculate(self, weather_data: Dict[str, Any]) -> HazardResult:
        """
        Calculate flood risk from precipitation data.

        Args:
            weather_data: Dictionary containing precipitation data

        Returns:
            HazardResult with flood risk assessment
        """
        # Extract precipitation data
        rain_1h = self.extract_nested(weather_data, "rain.1h", 0)
        rain_3h = self.extract_nested(weather_data, "rain.3h", 0)
        snow_1h = self.extract_nested(weather_data, "snow.1h", 0)  # Snow water equivalent

        # Estimate 24h accumulation if available in forecast
        # For now, use extrapolation from short-term data
        if rain_3h > 0:
            estimated_24h = rain_3h * 8  # Rough estimate
        else:
            estimated_24h = rain_1h * 24

        # Total precipitation (rain + snow water equivalent)
        total_1h = rain_1h + (snow_1h * 0.1)  # Snow to water ratio ~10:1

        # Get weather description
        weather_main = self.extract_nested(weather_data, "weather.0.main", "")
        weather_desc = self.extract_nested(weather_data, "weather.0.description", "")

        # Assess flood risk
        flood_assessment = self._assess_flood_risk(total_1h, estimated_24h, weather_main, weather_desc)

        # Calculate risk score
        score = self._calculate_risk_score(flood_assessment)
        risk_level = self.get_risk_level(score)

        # Generate factors
        factors = {
            "rainfall_rate_mmh": round(total_1h, 1),
            "estimated_24h_accumulation_mm": round(estimated_24h, 1),
            "intensity_category": flood_assessment["intensity"],
            "flood_likelihood": flood_assessment["likelihood"],
        }

        if rain_3h > 0:
            factors["rainfall_3h_mm"] = round(rain_3h, 1)

        # Generate recommendations
        recommendations = self._generate_recommendations(score, flood_assessment)

        return HazardResult(
            hazard_type=self.hazard_type,
            name=self.name,
            score=score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            citation=self.citation,
            confidence=0.80,  # Moderate confidence - depends on forecast accuracy
        )

    def _assess_flood_risk(self, rate_1h: float, accumulation_24h: float,
                           weather_main: str, weather_desc: str) -> Dict[str, Any]:
        """
        Assess flood risk from precipitation parameters.

        Args:
            rate_1h: Hourly precipitation rate
            accumulation_24h: Estimated 24-hour accumulation
            weather_main: Weather condition
            weather_desc: Weather description

        Returns:
            Flood risk assessment dictionary
        """
        # Determine intensity category
        if rate_1h < 2.5:
            intensity = "light"
        elif rate_1h < 10:
            intensity = "moderate"
        elif rate_1h < 30:
            intensity = "heavy"
        elif rate_1h < 50:
            intensity = "very_heavy"
        else:
            intensity = "extreme"

        # Determine likelihood based on rate AND accumulation
        rate_score = self._get_threshold_score(rate_1h, self.RATE_THRESHOLDS)
        accum_score = self._get_threshold_score(accumulation_24h, self.ACCUMULATION_THRESHOLDS)

        # Use the higher score as baseline
        max_score = max(rate_score, accum_score)

        # Adjust for sustained heavy rainfall
        if rate_1h > 10 and accumulation_24h > 50:
            max_score = min(max_score + 1, 5)

        # Check for flash flood conditions
        flash_flood_risk = rate_1h > 30 or "thunderstorm" in (weather_main + weather_desc).lower()

        if flash_flood_risk:
            likelihood = "high"
        elif max_score >= 4:
            likelihood = "high"
        elif max_score >= 3:
            likelihood = "moderate"
        elif max_score >= 2:
            likelihood = "low"
        else:
            likelihood = "minimal"

        return {
            "intensity": intensity,
            "likelihood": likelihood,
            "rate_score": rate_score,
            "accumulation_score": accum_score,
            "flash_flood_risk": flash_flood_risk,
            "composite_score": max_score,
        }

    def _get_threshold_score(self, value: float, thresholds: Dict[int, float]) -> int:
        """
        Get score based on threshold comparison.

        Args:
            value: Value to assess
            thresholds: Dictionary of score -> threshold mappings

        Returns:
            Score 1-5
        """
        for score in range(1, 6):
            if value < thresholds[score]:
                return score
        return 5

    def _calculate_risk_score(self, assessment: Dict[str, Any]) -> int:
        """
        Calculate risk score from flood assessment.

        Args:
            assessment: Flood risk assessment

        Returns:
            Risk score 1-5
        """
        return assessment["composite_score"]

    def _generate_recommendations(self, score: int, assessment: Dict[str, Any]) -> list[str]:
        """
        Generate actionable recommendations based on flood risk.

        Args:
            score: Risk score (1-5)
            assessment: Flood assessment details

        Returns:
            List of recommendation strings
        """
        flash_flood = assessment.get("flash_flood_risk", False)
        recommendations = []

        if score == 1:
            recommendations = [
                "Minimal flood risk",
                "Normal operations appropriate",
                "Routine weather monitoring sufficient",
            ]
        elif score == 2:
            recommendations = [
                "Low flood risk from light to moderate rainfall",
                "Drainage systems should be functioning normally",
                "Local flood alerts may provide additional context",
                "Standard emergency contacts should be accessible",
            ]
        elif score == 3:
            recommendations = [
                "Moderate flood risk from sustained or heavy rainfall",
                "Drainage systems may become stressed",
                "Ground floor areas could experience water ingress if drains overwhelmed",
                "Local flood warnings may be issued",
                "Access routes could be affected",
            ]
        elif score == 4:
            recommendations = [
                "High flood risk: significant rainfall creating flooding potential",
                "Ground floor spaces are at risk of flooding",
                "Road access may be compromised",
                "Electrical equipment at ground level may be at risk",
                "Emergency services response may be affected",
                "Evacuation routes should be considered in advance",
            ]
            if flash_flood:
                recommendations.insert(0, "Rapid-onset flooding possible due to intense rainfall or thunderstorms")

        else:  # score == 5
            recommendations = [
                "Severe flood risk: dangerous conditions for ground floor areas",
                "Ground floor likely to flood or already flooding",
                "Moving water poses serious safety hazards",
                "Electrical systems at ground level are at serious risk",
                "Emergency services may be unable to respond promptly",
                "Evacuation may become necessary if flooding affects living areas",
                "Upper floors provide safer refuge from flood water",
            ]
            if flash_flood:
                recommendations.insert(0, "Flash flooding conditions: extremely rapid water level rise possible")

        return recommendations
