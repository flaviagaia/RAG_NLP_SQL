from pathlib import Path
import os

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "company_sales.db"
DEFAULT_DATABASE_URI = f"sqlite:///{DB_PATH}"


def load_settings():
    load_dotenv(PROJECT_ROOT / ".env")
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "database_uri": os.getenv("DATABASE_URI", DEFAULT_DATABASE_URI),
    }


def is_default_sample_database(database_uri: str) -> bool:
    return database_uri == DEFAULT_DATABASE_URI
