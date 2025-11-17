"""
Base class for all hazard calculation modules.
Provides a standard interface and structure for hazard calculations.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class HazardResult:
    """Standard result format for hazard calculations."""

    hazard_type: str
    name: str
    score: int  # 1-5 scale
    risk_level: str  # 'Low', 'Moderate', 'High', 'Very High', 'Extreme'
    factors: Dict[str, Any]  # Contributing factors with values
    recommendations: List[str]  # Actionable recommendations
    citation: Dict[str, Any]  # Academic citation information
    confidence: Optional[float] = None  # Optional confidence score (0-1)


class BaseHazard(ABC):
    """
    Abstract base class for hazard calculation modules.

    All hazard modules must inherit from this class and implement
    the calculate() method with their specific methodology.
    """

    # These must be defined by subclasses
    hazard_type: str = ""
    name: str = ""
    description: str = ""

    # Academic citation - must be defined by subclasses
    citation: Dict[str, Any] = {}

    # Risk level thresholds - can be overridden by subclasses
    RISK_LEVELS = {
        1: "Low",
        2: "Moderate",
        3: "High",
        4: "Very High",
        5: "Extreme",
    }

    @abstractmethod
    def calculate(self, weather_data: Dict[str, Any]) -> HazardResult:
        """
        Calculate hazard risk score from weather data.

        Args:
            weather_data: Dictionary containing weather parameters
                         from OpenWeather API

        Returns:
            HazardResult with score, factors, and recommendations

        Raises:
            ValueError: If required data is missing or invalid
        """
        pass

    def get_risk_level(self, score: int) -> str:
        """
        Convert numeric score (1-5) to risk level string.

        Args:
            score: Risk score from 1-5

        Returns:
            Risk level string

        Raises:
            ValueError: If score is outside 1-5 range
        """
        if score < 1 or score > 5:
            raise ValueError(f"Score must be between 1 and 5, got {score}")
        return self.RISK_LEVELS[score]

    def validate_data(self, weather_data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that required fields are present in weather data.

        Args:
            weather_data: Weather data dictionary
            required_fields: List of required field names

        Raises:
            ValueError: If any required field is missing
        """
        missing_fields = [field for field in required_fields if field not in weather_data or weather_data[field] is None]
        if missing_fields:
            raise ValueError(f"Missing required fields for {self.name}: {', '.join(missing_fields)}")

    @staticmethod
    def extract_nested(data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """
        Extract nested value from dictionary using dot notation.

        Args:
            data: Source dictionary
            path: Dot-separated path (e.g., "main.temp")
            default: Default value if path not found

        Returns:
            Value at path or default

        Example:
            >>> data = {"main": {"temp": 20}}
            >>> extract_nested(data, "main.temp")
            20
        """
        keys = path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

        return current

    def get_methodology_info(self) -> Dict[str, Any]:
        """
        Get methodology information for this hazard.

        Returns:
            Dictionary with hazard type, name, description, and citation
        """
        return {
            "hazard_type": self.hazard_type,
            "name": self.name,
            "description": self.description,
            "citation": self.citation,
        }
