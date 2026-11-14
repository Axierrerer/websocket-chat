from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH / ".env", extra="ignore")


class AppSettings(Settings):
    HOST: str = Field(alias="APP_HOST")
    PORT: int = Field(alias="APP_PORT")


class RedisSettings(Settings):
    HOST: str = Field(alias="REDIS_HOST")
    PORT: int = Field(alias="REDIS_PORT")

    @property
    def redis_url(self) -> str:
        return f"redis://{self.HOST}:{self.PORT}/0"


class AllSettings(BaseModel):
    app: AppSettings = Field(default_factory=AppSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
