import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    SERPAPI_KEY: Optional[str] = None
    GOOGLE_SERVICE_ACCOUNT_JSON: Optional[str] = None
    MAX_FILE_SIZE_MB: int = 50
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
