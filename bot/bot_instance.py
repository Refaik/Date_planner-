from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import BOT_TOKEN, WEBAPP_URL, ADMIN_TELEGRAM_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💖 Выбрать свидание",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )],
        [InlineKeyboardButton(
            text="⚙️ Панель Парня (Админа)",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin")
        )]
    ])
    await message.answer(
        "Привет! Это ваше личное приложение для свиданий 💕\n\nНажмите кнопку ниже, чтобы открыть WebApp!",
        reply_markup=kb
    )

async def notify_admin_about_choice(idea_title: str, description: str, requirements: str, requires_booking: bool, active_date_id: int):
    booking_str = "Да ⚠️ (нужно забронировать!)" if requires_booking else "Нет ❌"
    text = (
        f"🎉 **Твоя девушка выбрала свидание!**\n\n"
        f"📌 **Название:** {idea_title}\n"
        f"📝 **Описание:** {description}\n"
        f"🎟 **Нужна бронь:** {booking_str}\n\n"
        f"🛒 **Что требуется / Чек-лист:**\n{requirements or 'Ничего специального'}\n\n"
        f"🆔 ID активности: `{active_date_id}`"
    )
    await bot.send_message(chat_id=ADMIN_TELEGRAM_ID, text=text, parse_mode="Markdown")

async def notify_admin_report(rating: int, review: str, photos_count: int):
    stars = "⭐" * rating
    text = (
        f"📸 **Сдан отчет о свидании!**\n\n"
        f"Оценка: {stars} ({rating}/5)\n"
        f"Отзыв: {review}\n"
        f"Загружено фото: {photos_count} шт."
    )
    await bot.send_message(chat_id=ADMIN_TELEGRAM_ID, text=text, parse_mode="Markdown")