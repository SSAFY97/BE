import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = os.getenv("DATABASE_URL") or str(BASE_DIR / "localhub.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
