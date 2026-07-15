import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'localhub.db'}"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
TMAP_API_KEY = os.getenv("TMAP_API_KEY", "")
TMAP_API_TIMEOUT_SECONDS = float(os.getenv("TMAP_API_TIMEOUT_SECONDS", "8"))
