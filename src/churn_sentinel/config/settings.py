from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    raw_path: str = Field(validation_alias='RAW_DATA_PATH')

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()