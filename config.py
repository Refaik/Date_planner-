import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_TELEGRAM_ID: int = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    # Render передает свой порт в переменную $PORT (по умолчанию 10000)
    PORT: int = int(os.getenv("PORT", "10000"))
    BASE_URL: str = os.getenv("BASE_URL", "https://date-planner-9vny.onrender.com")
    DB_URL: str = os.getenv("DB_URL", "sqlite+aiosqlite:///./date_planner.db")

settings = Settings()