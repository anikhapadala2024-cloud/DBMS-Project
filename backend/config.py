import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from backend/.env or root .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "agritech_default_secret_key_change_in_production")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # Database config
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "agritech_db")
    ALLOW_SQLITE_FALLBACK = os.getenv("ALLOW_SQLITE_FALLBACK", "True").lower() in ("true", "1", "yes")
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "agritech.db")

    @classmethod
    def get_mysql_uri(cls) -> str:
        """Construct MySQL connection URI with pymysql driver."""
        if cls.DB_PASSWORD:
            return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}?charset=utf8mb4"
        return f"mysql+pymysql://{cls.DB_USER}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}?charset=utf8mb4"

    @classmethod
    def get_sqlite_uri(cls) -> str:
        """Construct SQLite URI fallback."""
        sqlite_full_path = BASE_DIR / cls.SQLITE_DB_PATH
        return f"sqlite:///{sqlite_full_path.as_posix()}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
