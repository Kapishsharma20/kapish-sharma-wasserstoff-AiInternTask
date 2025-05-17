from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # File Handling
    UPLOAD_DIR: str = "data/uploads"
    MAX_FILE_SIZE: int = 1024 * 1024 * 100  # 100MB
    ALLOWED_TYPES: list = [".pdf", ".png", ".jpg", ".jpeg"]
    
    # OCR
    TESSERACT_PATH: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    POPPLER_PATH: str = r"C:\Release-24.08.0-0\poppler-24.08.0\Library\bin"
    PDF_DENSITY: int = 300
    MIN_CONFIDENCE: int = 70
    
    # Database
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_NAME: str = "documents"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
