import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
WORKSPACE_DIR = BASE_DIR

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "VisionTrust AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Evidence-based integrity assurance for computer vision pipelines."
    API_PREFIX: str = "/api"
    OFFLINE_MODE: bool = True
    
    # Security & Auth
    SECRET_KEY: str = "visiontrust-secret-key-airgapped-demo-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for demo sessions
    
    # Database
    DATABASE_URL: str = "sqlite:///./visiontrust.db"
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Pipeline file storage locations
    DATA_DIR: Path = WORKSPACE_DIR / "data"
    DEMO_DATA_DIR: Path = WORKSPACE_DIR / "data" / "demo"
    MODELS_DIR: Path = WORKSPACE_DIR / "models"
    REPORTS_DIR: Path = WORKSPACE_DIR / "reports"
    SIMULATOR_DIR: Path = WORKSPACE_DIR / "simulator"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.DEMO_DATA_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
os.makedirs(settings.SIMULATOR_DIR, exist_ok=True)
