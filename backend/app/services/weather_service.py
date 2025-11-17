"""
OpenWeather API client for fetching weather and air quality data.
"""
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import settings


class WeatherService:
    """Client for interacting with OpenWeather API."""

    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = settings.OPENWEATHER_BASE_URL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetch current weather data for a location.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Dict containing current weather data
        """
        url = f"{self.base_url}/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",  # Celsius, m/s
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_hourly_forecast(self, lat: float, lon: float, hours: int = 96) -> Dict[str, Any]:
        """
        Fetch hourly forecast for a location (up to 96 hours/4 days).

        Args:
            lat: Latitude
            lon: Longitude
            hours: Number of hours to fetch (max 96)

        Returns:
            Dict containing hourly forecast data
        """
        url = f"{self.base_url}/data/2.5/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
            "cnt": min(hours // 3, 40),  # API returns 3-hour intervals, max 40 items (5 days)
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_daily_forecast(self, lat: float, lon: float, days: int = 16) -> Dict[str, Any]:
        """
        Fetch daily forecast for a location (up to 16 days).

        Args:
            lat: Latitude
            lon: Longitude
            days: Number of days to fetch (max 16)

        Returns:
            Dict containing daily forecast data
        """
        url = f"{self.base_url}/data/2.5/forecast/daily"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
            "cnt": min(days, 16),
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_air_quality(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetch current air quality data for a location.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Dict containing air quality data with AQI and pollutant levels
        """
        url = f"{self.base_url}/data/2.5/air_pollution"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_air_quality_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetch air quality forecast for a location.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Dict containing air quality forecast data
        """
        url = f"{self.base_url}/data/2.5/air_pollution/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def geocode_location(self, query: str, limit: int = 5) -> list[Dict[str, Any]]:
        """
        Geocode a location query to get coordinates.

        Args:
            query: Location search query (city name, address, etc.)
            limit: Maximum number of results

        Returns:
            List of location results with coordinates
        """
        url = f"{self.base_url}/geo/1.0/direct"
        params = {
            "q": query,
            "limit": limit,
            "appid": self.api_key,
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def reverse_geocode(self, lat: float, lon: float, limit: int = 1) -> list[Dict[str, Any]]:
        """
        Reverse geocode coordinates to get location name.

        Args:
            lat: Latitude
            lon: Longitude
            limit: Maximum number of results

        Returns:
            List of location results
        """
        url = f"{self.base_url}/geo/1.0/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "limit": limit,
            "appid": self.api_key,
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def fetch_all_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetch all relevant data for a location in one call.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Dict containing current weather, forecasts, and air quality
        """
        current_weather = await self.get_current_weather(lat, lon)
        hourly_forecast = await self.get_hourly_forecast(lat, lon)
        air_quality = await self.get_air_quality(lat, lon)

        return {
            "current": current_weather,
            "hourly_forecast": hourly_forecast,
            "air_quality": air_quality,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Global instance
weather_service = WeatherService()
