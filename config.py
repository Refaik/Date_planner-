import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_TELEGRAM_ID: int = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    # Render передаёт системный порт в переменной PORT (обычно 10000)
    PORT: int = int(os.getenv("PORT", "8000"))
    BASE_URL: str = os.getenv("BASE_URL", "")
    DB_URL: str = os.getenv("DB_URL", "sqlite+aiosqlite:///./date_planner.db")

settings = Settings()