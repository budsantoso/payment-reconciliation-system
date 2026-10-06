from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    PROJECT_NAME: str = 'Payment Reconciliation System'
    APP_ENV: str = 'development'
    PORT: int = 8000
    MAX_UPLOAD_SIZE_MB: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
