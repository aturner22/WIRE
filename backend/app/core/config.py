"""
Application configuration management using Pydantic settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    APP_NAME: str = "WIRE"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # OpenWeather API
    OPENWEATHER_API_KEY: str
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org"

    # Security (not currently used but available for future JWT/session management)
    SECRET_KEY: Optional[str] = None

    # CORS - Allow vercel origins in production, or specific origins in development
    CORS_ORIGINS: list[str] = ["https://wire-delta.vercel.app"] if os.getenv("ENVIRONMENT") == "production" else [
        "http://localhost:3000",
        "http://localhost:3001"
    ]

    class Config:
        env_file = "../.env"
        case_sensitive = True


settings = Settings()
