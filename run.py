import asyncio
import uvicorn
from main import app
from database.database import init_db
from bot.bot_instance import dp, bot


async def start_fastapi():
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await init_db()

    await asyncio.gather(
        start_fastapi(),
        dp.start_polling(bot)
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Приложение остановлено.")