from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Load environment file
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )

    # --- GROQ Configuration ---
    GROQ_LLM_MODEL: str = "llama-3.3-70b-versatile"
    
    # --- Paths Configuration ---
    DB_PATH: Path = Path("data/cleaned/receipts.db")

    PDF_PATH: Path = Path("data/raw/lidl")
    AH_RAW_PATH: Path = Path("data/raw/ah")
    LIDL_RAW_PATH: Path = Path("data/raw/lidl")




settings = Settings()