import os
import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings powered by Pydantic BaseSettings.
    Loads values from environment variables or .env file.
    """
    APP_NAME: str = "DiaSense AI Backend"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database Settings
    DATABASE_URL: str = "sqlite:///./diasense.db"

    # Security & JWT Settings
    SECRET_KEY: str = "diasense_super_secret_jwt_key_change_in_production_2026_x99!"
    ALGORITHM: str = "HS256"
    # FIX H4: Was 60 minutes — mobile users were kicked out after 1 hour.
    # Extended to 1440 minutes (24 hours) for mobile-friendly sessions.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Contact Admin Email Notification Target
    ADMIN_EMAIL: str = "gagankamati643@gmail.com"

    # SMTP Settings (Optional for live delivery)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Generative AI Key
    GEMINI_API_KEY: str = ""

    # Google Places API Key (Optional; defaults to OpenStreetMap Overpass & Nominatim)
    GOOGLE_PLACES_API_KEY: str = ""

    # CORS Settings (Allow local Vite ports & wildcards in development)
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
