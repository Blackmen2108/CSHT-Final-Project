import os

IS_READ_ENV = os.getenv("IS_READ_ENV", "False").lower() == "true"


from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnhancedBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env" if IS_READ_ENV else None,
        extra="ignore",
    )
    pass
