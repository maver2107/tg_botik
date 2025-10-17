from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    BOT_TOKEN: str

    LOG_LEVEL: str
    LOG_FORMAT: str
    LOG_ROTATION: str
    LOG_RETENTION: str
    LOG_FILE_PATH: str
    LOG_COMPRESSION: str = "gz"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache(maxsize=None)
def get_settings():
    return Settings()


settings = get_settings()
