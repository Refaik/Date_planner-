import asyncio
import logging
import uvicorn
from aiogram.types import MenuButtonWebApp, WebAppInfo

from config import settings
from main import app
from bot.bot_instance import bot, dp, set_current_webapp_url
from tunnel import start_tunnel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("run")

async def run_server(server: uvicorn.Server):
    await server.serve()

async def run_bot(tunnel_proc):
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Бот запущен и ожидает сообщений...")
        await dp.start_polling(bot)
    finally:
        if tunnel_proc and tunnel_proc.returncode is None:
            logger.info("Остановка Cloudflare Tunnel...")
            try:
                tunnel_proc.terminate()
                await tunnel_proc.wait()
            except Exception:
                pass

async def main():
    # 1. Запуск веб-сервера FastAPI (Uvicorn)
    config = uvicorn.Config(
        app=app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(run_server(server))

    # Ожидаем готовности локального сервера перед подключением туннеля
    while not server.started:
        await asyncio.sleep(0.1)

    # 2. Запуск Cloudflare Tunnel (с ожиданием Registered tunnel connection)
    try:
        tunnel_url, tunnel_proc = await start_tunnel(settings.PORT)
    except Exception as e:
        logger.error(f"Ошибка запуска туннеля: {e}")
        server.should_exit = True
        await server_task
        return

    set_current_webapp_url(tunnel_url)

    print("\n" + "=" * 60)
    print("✨ СЕРВИС УСПЕШНО ЗАПУЩЕН И ГОТОВ К РАБОТЕ!")
    print(f"🔗 Публичный WebApp URL: {tunnel_url}")
    print(f"🏠 Локальный адрес: http://127.0.0.1:{settings.PORT}")
    print("=" * 60 + "\n")
    # 4. Запуск Telegram-бота
    try:
        await run_bot(tunnel_proc)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Остановка программы...")
    finally:
        server.should_exit = True
        await server_task
        if tunnel_proc and tunnel_proc.returncode is None:
            try:
                tunnel_proc.terminate()
            except Exception:
                pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПрограмма остановлена.")