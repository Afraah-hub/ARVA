from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Database connection string:
    # MySQL: mysql+pymysql://user:password@localhost:3306/arva_db
    # SQLite fallback: sqlite:///./arva.db
    DATABASE_URL: str = "sqlite:///./arva.db"
    
    # Open-Meteo
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    WEATHER_CACHE_HOURS: int = 3
    
    # Default Demo Farm Coordinates (Bangalore Agro-Climatic Zone)
    DEFAULT_LATITUDE: float = 12.9716
    DEFAULT_LONGITUDE: float = 77.5946
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
