from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Load environment file
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )


    # --- Paths Configuration ---
    DB_PATH: Path = Path("data/cleaned/receipts.db")

    PDF_PATH: Path = Path("data/raw/lidl")
    PDF_AH_PATH: Path = Path("data/raw/ah")
    PDF_LIDL_PATH: Path = Path("data/raw/lidl")



settings = Settings()