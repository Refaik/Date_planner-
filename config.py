import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "123456789"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./date_planner.db")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-domain.com")