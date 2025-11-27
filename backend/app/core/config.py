# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "AI Business Analyst Backend"

    CONFLUENCE_URL: str | None = None
    CONFLUENCE_USER: str | None = None
    CONFLUENCE_API_TOKEN: str | None = None
    CONFLUENCE_SPACE_KEY: str = "AIHACK"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
