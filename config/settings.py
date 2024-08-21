from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_PASSWORD: str
    MONGO_USERNAME: str
    MONGO_DATABASE: str
    DB_ADDRESS: str
    LOG_LEVEL: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


@lru_cache
def get_settings():
    return Settings()
