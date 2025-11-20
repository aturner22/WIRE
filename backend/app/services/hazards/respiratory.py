"""
Respiratory Risk hazard calculation module.

Implements air quality risk assessment using EPA AQI and UK DAQI standards.
Citation: EPA Air Quality Index + COMEAP Guidelines
"""
from typing import Dict, Any
from .base import BaseHazard, HazardResult


class RespiratoryRisk(BaseHazard):
    """
    Respiratory Risk calculator using Air Quality Index (AQI).

    Assesses risk from air pollutants (PM2.5, PM10, NO2, O3, SO2, CO)
    with thresholds calibrated for vulnerable populations.
    """

    hazard_type = "respiratory"
    name = "Respiratory Risk"
    description = "Risk of respiratory distress from air pollution including asthma and COPD exacerbation"

    citation = {
        "title": "Technical Assistance Document for the Reporting of Daily Air Quality - the Air Quality Index (AQI)",
        "authors": "U.S. Environmental Protection Agency (EPA)",
        "year": 2018,
        "publication": "EPA-454/B-18-007",
        "url": "https://www.airnow.gov/publications/air-quality-index/technical-assistance-document-for-reporting-the-daily-aqi/",
        "methodology_location": "PM2.5 breakpoints (μg/m³): 0-12.0 (Good), 12.1-35.4 (Moderate), 35.5-55.4 (Unhealthy for Sensitive Groups), 55.5-150.4 (Unhealthy), 150.5-250.4 (Very Unhealthy), 250.5+ (Hazardous). PM10: 0-54 (Good), 55-154 (Moderate), 155-254 (USG), 255-354 (Unhealthy), 355-424 (Very Unhealthy), 425+ (Hazardous).",
        "additional": "Health impacts on vulnerable populations documented in Hoek et al. (2013) 'Long-term air pollution exposure and cardio-respiratory mortality' Environmental Health 12:43, doi:10.1186/1476-069X-12-43"
    }

    # AQI breakpoints for PM2.5 (μg/m³)
    PM25_BREAKPOINTS = [
        (0, 12.0, 1),      # Good
        (12.1, 35.4, 2),   # Moderate
        (35.5, 55.4, 3),   # Unhealthy for Sensitive Groups
        (55.5, 150.4, 4),  # Unhealthy
        (150.5, 500, 5),   # Very Unhealthy / Hazardous
    ]

    # AQI breakpoints for PM10 (μg/m³)
    PM10_BREAKPOINTS = [
        (0, 54, 1),
        (55, 154, 2),
        (155, 254, 3),
        (255, 354, 4),
        (355, 604, 5),
    ]

    # Ozone breakpoints (μg/m³)
    O3_BREAKPOINTS = [
        (0, 100, 1),
        (101, 160, 2),
        (161, 200, 3),
        (201, 300, 4),
        (301, 500, 5),
    ]

    # NO2 breakpoints (μg/m³)
    NO2_BREAKPOINTS = [
        (0, 67, 1),
        (68, 134, 2),
        (135, 200, 3),
        (201, 400, 4),
        (401, 1000, 5),
    ]

    def calculate(self, weather_data: Dict[str, Any]) -> HazardResult:
        """
        Calculate respiratory risk from air quality data.

        Args:
            weather_data: Dictionary containing air quality data

        Returns:
            HazardResult with respiratory risk assessment
        """
        # Extract air quality components
        air_quality = weather_data.get("air_quality", {})

        if not air_quality:
            raise ValueError(f"Missing air quality data for {self.name}")

        # Get pollutant concentrations from nested structure
        components = {}
        if "list" in air_quality and len(air_quality["list"]) > 0:
            components = air_quality["list"][0].get("components", {})
            main_aqi = air_quality["list"][0].get("main", {}).get("aqi", None)
        else:
            components = air_quality.get("components", {})
            main_aqi = air_quality.get("main", {}).get("aqi", None)

        pm2_5 = components.get("pm2_5")
        pm10 = components.get("pm10")
        no2 = components.get("no2")
        o3 = components.get("o3")
        so2 = components.get("so2")
        co = components.get("co")

        # Calculate individual pollutant scores
        scores = []
        if pm2_5 is not None:
            scores.append(self._calculate_pollutant_score(pm2_5, self.PM25_BREAKPOINTS))
        if pm10 is not None:
            scores.append(self._calculate_pollutant_score(pm10, self.PM10_BREAKPOINTS))
        if o3 is not None:
            scores.append(self._calculate_pollutant_score(o3, self.O3_BREAKPOINTS))
        if no2 is not None:
            scores.append(self._calculate_pollutant_score(no2, self.NO2_BREAKPOINTS))

        # Overall score is the maximum (worst) pollutant
        if not scores:
            raise ValueError("No valid pollutant data available")

        score = max(scores)
        risk_level = self.get_risk_level(score)

        # Generate factors
        factors = {
            "overall_aqi": main_aqi if main_aqi else score,
            "pm2_5_ugm3": round(pm2_5, 1) if pm2_5 else None,
            "pm10_ugm3": round(pm10, 1) if pm10 else None,
            "no2_ugm3": round(no2, 1) if no2 else None,
            "o3_ugm3": round(o3, 1) if o3 else None,
            "so2_ugm3": round(so2, 1) if so2 else None,
            "co_ugm3": round(co, 1) if co else None,
            "primary_pollutant": self._identify_primary_pollutant(components),
        }

        # Remove None values
        factors = {k: v for k, v in factors.items() if v is not None}

        # Generate recommendations
        recommendations = self._generate_recommendations(score, factors)

        return HazardResult(
            hazard_type=self.hazard_type,
            name=self.name,
            score=score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            citation=self.citation,
            confidence=0.98,  # Air quality data is highly reliable
        )

    def _calculate_pollutant_score(self, concentration: float, breakpoints: list) -> int:
        """
        Calculate risk score for a single pollutant.

        Args:
            concentration: Pollutant concentration
            breakpoints: List of (min, max, score) tuples

        Returns:
            Risk score 1-5
        """
        for min_val, max_val, score in breakpoints:
            if min_val <= concentration <= max_val:
                return score

        # If concentration exceeds all breakpoints, return max score
        return 5

    def _identify_primary_pollutant(self, components: Dict[str, float]) -> str:
        """
        Identify which pollutant is the primary concern.

        Args:
            components: Dictionary of pollutant concentrations

        Returns:
            Name of primary pollutant
        """
        pollutant_scores = {}

        if "pm2_5" in components and components["pm2_5"]:
            pollutant_scores["PM2.5"] = self._calculate_pollutant_score(components["pm2_5"], self.PM25_BREAKPOINTS)
        if "pm10" in components and components["pm10"]:
            pollutant_scores["PM10"] = self._calculate_pollutant_score(components["pm10"], self.PM10_BREAKPOINTS)
        if "o3" in components and components["o3"]:
            pollutant_scores["Ozone"] = self._calculate_pollutant_score(components["o3"], self.O3_BREAKPOINTS)
        if "no2" in components and components["no2"]:
            pollutant_scores["NO2"] = self._calculate_pollutant_score(components["no2"], self.NO2_BREAKPOINTS)

        if not pollutant_scores:
            return "Unknown"

        return max(pollutant_scores, key=pollutant_scores.get)

    def _generate_recommendations(self, score: int, factors: Dict[str, Any]) -> list[str]:
        """
        Generate actionable recommendations based on air quality.

        Args:
            score: Risk score (1-5)
            factors: Air quality factors

        Returns:
            List of recommendation strings
        """
        primary = factors.get("primary_pollutant", "pollutants")

        recommendations = []

        if score == 1:
            recommendations = [
                "Good air quality",
                "Normal outdoor activities suitable",
                "No special precautions needed",
            ]
        elif score == 2:
            recommendations = [
                "Acceptable air quality for most individuals",
                "Sensitive individuals may experience minor irritation",
                "Those with respiratory conditions may want to monitor symptoms",
                f"Primary pollutant: {primary}",
            ]
        elif score == 3:
            recommendations = [
                "Air quality may affect sensitive groups",
                "Individuals with asthma, COPD, or heart conditions may experience symptoms",
                "Prolonged outdoor exposure may cause discomfort for vulnerable persons",
                "Indoor air quality management becomes relevant",
                f"Primary pollutant: {primary}",
            ]
        elif score == 4:
            recommendations = [
                "Unhealthy air quality - widespread effects possible",
                "Outdoor activities may aggravate respiratory conditions",
                "Keeping windows closed may help maintain indoor air quality",
                "Those with respiratory conditions should monitor symptoms closely",
                "Rescue medications should be accessible for those who need them",
                f"High levels of {primary}",
            ]
        else:  # score == 5
            recommendations = [
                "Hazardous air quality - serious health implications",
                "Outdoor exposure poses significant health risks",
                "Indoor air filtration becomes important",
                "Respiratory symptoms likely in vulnerable populations",
                "Medical assistance may be needed for those with breathing difficulties",
                f"Dangerous levels of {primary}",
            ]

        return recommendations
