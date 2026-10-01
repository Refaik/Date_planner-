import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    webapp_url = settings.BASE_URL
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать свидание 💖", web_app=WebAppInfo(url=webapp_url))]
    ])
    await message.answer(
        "Привет, любимая! 💕\n\nНажми на кнопку ниже, чтобы открыть наш сервис и выбрать самое лучшее свидание ✨",
        reply_markup=kb
    )

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != settings.ADMIN_TELEGRAM_ID:
        await message.answer("Доступ только для администратора.")
        return
    admin_url = f"{settings.BASE_URL}/admin"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Панель добавления свиданий ➕", web_app=WebAppInfo(url=admin_url))]
    ])
    await message.answer("Панель управления свиданиями:", reply_markup=kb)

async def notify_admin_date_chosen(
    idea_title: str,
    description: str,
    requirements: str,
    requires_booking: bool,
    active_date_id: int,
    place_link: str = "",
    dress_code: str = ""
):
    if not settings.ADMIN_TELEGRAM_ID or not settings.BOT_TOKEN:
        return

    booking_str = "Да ⚠️ (нужно забронировать заранее!)" if requires_booking else "Нет ❌"
    text = (
        f"🎉 *Твоя девушка выбрала свидание!*\n\n"
        f"📌 *Название:* {idea_title}\n"
        f"📝 *Описание:* {description}\n"
        f"👗 *Дресс-код (ей сказано):* {dress_code or 'Комфортный стиль'}\n"
        f"🎟 *Нужна бронь:* {booking_str}\n\n"
        f"🛒 *Что требуется подготовить:*\n{requirements or 'Ничего специального'}"
    )
    if place_link:
        text += f"\n\n📍 *Место / Ссылка на карте:*\n{place_link}"
    text += f"\n\n🆔 ID активности: `{active_date_id}`"

    try:
        await bot.send_message(
            chat_id=settings.ADMIN_TELEGRAM_ID,
            text=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to send telegram notification: {e}")

async def notify_admin_date_completed(rating: int, review: str, photos_count: int):
    if not settings.ADMIN_TELEGRAM_ID or not settings.BOT_TOKEN:
        return

    stars = "⭐" * max(1, min(5, rating))
    text = (
        f"📸 *Сдан отчет о свидании!*\n\n"
        f"Оценка: {stars} ({rating}/5)\n"
        f"Отзыв: {review}\n"
        f"Загружено фото: {photos_count} шт."
    )
    try:
        await bot.send_message(
            chat_id=settings.ADMIN_TELEGRAM_ID,
            text=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to send completion notification: {e}")