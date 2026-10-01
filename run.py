import asyncio
import logging
import uvicorn
from config import settings
from bot.bot_instance import bot, dp
from main import app

logger = logging.getLogger(__name__)

async def run_fastapi():
    config = uvicorn.Config(
        app=app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

async def run_bot():
    logger.info("Starting Telegram Bot Polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

async def main():
    await asyncio.gather(
        run_fastapi(),
        run_bot()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Date Planner App stopped.")