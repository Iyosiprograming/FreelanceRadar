from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# Points to the Backend/ directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
class Settings(BaseSettings):
    APP_NAME: str = "FreelancerRadar"
    APP_VERSION: str = "1.0.0"
    MODE: str = "development"
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()