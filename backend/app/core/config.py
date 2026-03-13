"""
Application configuration via pydantic-settings.
All environment variables are managed here.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str
    github_username: str = "luisalarcon-gauntlet"
    github_token: str = ""
    cache_ttl_minutes: int = 60
    
    # JWT settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
