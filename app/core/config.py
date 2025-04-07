from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str
    DATA_B_URL: str
    FETCH_INTERVAL_SECONDS: int
    WORKERS_COUNT: int
    APP_HOST: str
    APP_PORT: int
    MAX_RETRIES: int
    RETRY_DELAY: int

    model_config = ConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
