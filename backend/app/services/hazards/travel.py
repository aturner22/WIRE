"""
Travel/Visibility Risk hazard calculation module.

Weather-related travel accident risk based on visibility, precipitation, and wind.
Citation: Transportation Research Board weather impact studies
"""
from typing import Dict, Any
from .base import BaseHazard, HazardResult


class TravelRisk(BaseHazard):
    """
    Travel/Visibility Risk calculator for transport safety.

    Assesses risk for transport (ambulances, staff vehicles, resident transport)
    based on visibility, precipitation, and wind conditions.
    """

    hazard_type = "travel"
    name = "Travel/Visibility Risk"
    description = "Risk for road transport due to reduced visibility, precipitation, and adverse conditions"

    citation = {
        "title": "The relationship between road accident severity and recorded weather",
        "authors": "Edwards, J.B.",
        "year": 1999,
        "journal": "Journal of Safety Research",
        "publication": "Volume 29, Issue 4, Pages 249-262",
        "url": "https://www.sciencedirect.com/science/article/pii/S0022437598000516",
        "doi": "10.1016/S0022-4375(98)00051-6",
        "methodology_location": "Pages 254-258: Analysis of weather conditions and accident severity; Tables 2-4 show relationships between precipitation, visibility, and crash rates",
        "additional": "FHWA Road Weather Management Program - How Do Weather Events Impact Roads?",
    }

    # Visibility thresholds (meters)
    VISIBILITY_THRESHOLDS = {
        1: 10000,   # Good: > 10 km
        2: 4000,    # Moderate: 4-10 km
        3: 1000,    # Poor: 1-4 km
        4: 200,     # Very Poor: 200m-1km (fog)
        5: 0,       # Extremely Poor: < 200m (dense fog)
    }

    def calculate(self, weather_data: Dict[str, Any]) -> HazardResult:
        """
        Calculate travel/visibility risk from weather data.

        Args:
            weather_data: Dictionary containing visibility, precipitation, wind

        Returns:
            HazardResult with travel risk assessment
        """
        # Extract relevant data
        visibility = self.extract_nested(weather_data, "visibility", 10000)  # Default 10km
        rain_1h = self.extract_nested(weather_data, "rain.1h", 0)
        snow_1h = self.extract_nested(weather_data, "snow.1h", 0)
        wind_speed_ms = self.extract_nested(weather_data, "wind.speed", 0)
        wind_speed = wind_speed_ms * 3.6  # km/h
        wind_gust_ms = self.extract_nested(weather_data, "wind.gust", wind_speed_ms * 1.5)  # Estimate if not provided
        wind_gust = wind_gust_ms * 3.6

        weather_main = self.extract_nested(weather_data, "weather.0.main", "")
        weather_desc = self.extract_nested(weather_data, "weather.0.description", "")

        # Assess travel conditions
        travel_assessment = self._assess_travel_conditions(
            visibility, rain_1h, snow_1h, wind_speed, wind_gust, weather_main, weather_desc
        )

        # Calculate risk score
        score = self._calculate_risk_score(travel_assessment)
        risk_level = self.get_risk_level(score)

        # Generate factors
        factors = {
            "visibility_category": travel_assessment["visibility_category"],
            "precipitation_mmh": round(rain_1h + snow_1h, 1),
            "wind_speed_kmh": round(wind_speed, 1),
            "wind_gust_kmh": round(wind_gust, 1),
            "road_conditions": travel_assessment["road_conditions"],
            "hazards": travel_assessment["hazards"],
            "visibility_m": visibility,
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(score, travel_assessment)

        return HazardResult(
            hazard_type=self.hazard_type,
            name=self.name,
            score=score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            citation=self.citation,
            confidence=0.88,
        )

    def _assess_travel_conditions(self, visibility: float, rain: float, snow: float,
                                   wind_speed: float, wind_gust: float,
                                   weather_main: str, weather_desc: str) -> Dict[str, Any]:
        """
        Assess multiple travel risk factors.

        Args:
            visibility: Visibility distance in meters
            rain: Rain rate (mm/h)
            snow: Snow rate (mm/h)
            wind_speed: Wind speed (km/h)
            wind_gust: Wind gust (km/h)
            weather_main: Weather condition
            weather_desc: Weather description

        Returns:
            Travel condition assessment
        """
        hazards = []
        component_scores = []

        # Visibility assessment
        if visibility < 200:
            visibility_cat = "extremely_poor"
            component_scores.append(5)
            hazards.append("Dense fog")
        elif visibility < 1000:
            visibility_cat = "very_poor"
            component_scores.append(4)
            hazards.append("Fog/poor visibility")
        elif visibility < 4000:
            visibility_cat = "poor"
            component_scores.append(3)
            hazards.append("Reduced visibility")
        elif visibility < 10000:
            visibility_cat = "moderate"
            component_scores.append(2)
        else:
            visibility_cat = "good"
            component_scores.append(1)

        # Precipitation assessment
        if snow > 0:
            if snow > 5:
                component_scores.append(5)
                hazards.append("Heavy snow")
            elif snow > 2:
                component_scores.append(4)
                hazards.append("Moderate snow")
            else:
                component_scores.append(3)
                hazards.append("Light snow")
        elif rain > 10:
            component_scores.append(4)
            hazards.append("Heavy rain")
        elif rain > 5:
            component_scores.append(3)
            hazards.append("Moderate rain")
        elif rain > 0:
            component_scores.append(2)
        else:
            component_scores.append(1)

        # Wind assessment
        if wind_gust > 70:
            component_scores.append(4)
            hazards.append("Strong winds affecting vehicles")
        elif wind_gust > 50:
            component_scores.append(3)
            hazards.append("Gusty winds")
        elif wind_gust > 30:
            component_scores.append(2)
        else:
            component_scores.append(1)

        # Determine road conditions
        if snow > 0:
            road_conditions = "snow/ice"
        elif rain > 5:
            road_conditions = "wet/hazardous"
        elif rain > 0:
            road_conditions = "wet"
        elif "fog" in weather_desc.lower() or "mist" in weather_desc.lower():
            road_conditions = "fog"
        else:
            road_conditions = "clear"

        # Composite score
        if component_scores:
            max_score = max(component_scores)
            avg_score = sum(component_scores) / len(component_scores)
            # Weighted combination
            composite = 0.6 * max_score + 0.4 * avg_score
        else:
            composite = 1.0

        return {
            "visibility_category": visibility_cat,
            "road_conditions": road_conditions,
            "hazards": hazards,
            "composite_score": composite,
            "visibility_score": component_scores[0] if len(component_scores) > 0 else 1,
            "precipitation_score": component_scores[1] if len(component_scores) > 1 else 1,
            "wind_score": component_scores[2] if len(component_scores) > 2 else 1,
        }

    def _calculate_risk_score(self, assessment: Dict[str, Any]) -> int:
        """
        Calculate risk score from travel assessment.

        Args:
            assessment: Travel condition assessment

        Returns:
            Risk score 1-5
        """
        composite = assessment["composite_score"]

        if composite >= 4.5:
            return 5
        elif composite >= 3.5:
            return 4
        elif composite >= 2.5:
            return 3
        elif composite >= 1.5:
            return 2
        else:
            return 1

    def _generate_recommendations(self, score: int, assessment: Dict[str, Any]) -> list[str]:
        """
        Generate actionable recommendations for travel safety.

        Args:
            score: Risk score (1-5)
            assessment: Travel assessment details

        Returns:
            List of recommendation strings
        """
        hazards = assessment.get("hazards", [])
        recommendations = []

        if score == 1:
            recommendations = [
                "Good travel conditions",
                "Normal driving conditions present",
                "No weather-related travel concerns",
            ]
        elif score == 2:
            recommendations = [
                "Moderate travel conditions with minor weather impacts",
                "Visibility or road surface may be slightly compromised",
                "Journey times may be slightly extended",
                "Vehicle lighting helps with visibility",
            ]
            if hazards:
                recommendations.insert(0, f"Weather conditions: {', '.join(hazards)}")

        elif score == 3:
            recommendations = [
                "Difficult travel conditions due to weather",
                "Road surfaces may be slippery or visibility reduced",
                "Journey times likely to be extended",
                "Non-urgent travel may be worth postponing",
                "Families should be aware of potential transport delays",
                "Emergency vehicle response times may be affected",
            ]
            if hazards:
                recommendations.insert(0, f"Weather hazards: {', '.join(hazards)}")

        elif score == 4:
            recommendations = [
                "Dangerous travel conditions present",
                "High risk of accidents due to weather conditions",
                "Non-essential travel poses significant safety risks",
                "Medical appointments may need rescheduling",
                "Journey times severely affected",
                "Emergency services response significantly impacted",
            ]
            if hazards:
                recommendations.insert(0, f"Hazardous conditions: {', '.join(hazards)}")

        else:  # score == 5
            recommendations = [
                "Severe travel hazards: extremely dangerous conditions",
                "Roads may be impassable or pose extreme safety risk",
                "All non-emergency transport poses serious danger",
                "Staff may be unable to travel safely",
                "Emergency services severely compromised",
                "Vehicles may become stranded",
                "This represents the most dangerous travel conditions",
            ]
            if hazards:
                recommendations.insert(0, f"Extreme conditions: {', '.join(hazards)}")

        return recommendations
