from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# Points to the Backend/ directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "FreelancerRadar"
    APP_VERSION: str = "1.0.0"
    MODE: str = "development"
    DATABASE_URL: str = "sqlite:///./test.db"
    WEBHOOK_SECRET: str 
    CLERK_SECRET_KEY: str 
    JWKS_PUBLIC_KEY: str 
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env", BASE_DIR / ".env.local", ".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
