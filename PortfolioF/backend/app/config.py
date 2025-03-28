import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Base settings class for the application."""
    ENVIRONMENT: str = "development"
    APP_NAME: str = "Portfolio API"
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Email settings
    EMAIL_FROM: str = "noreply@example.com"
    EMAIL_TO: str = "contact@example.com"
    SMTP_SERVER: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",
        env_prefix=""
    )

class DevSettings(Settings):
    """Development environment settings."""
    DEBUG: bool = True

class ProdSettings(Settings):
    """Production environment settings."""
    CORS_ORIGINS: List[str] = ["https://yourproductiondomain.com"]

def get_settings() -> Settings:
    """Get the appropriate settings based on the environment."""
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        return ProdSettings()
    return DevSettings()

settings = get_settings() 