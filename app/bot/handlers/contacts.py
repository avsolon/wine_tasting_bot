from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.bot.keyboards.main_menu import get_main_menu

router = Router()

CONTACTS_TEXT = (
    "📍 *Контакты клуба «Tasting & Talk»*\n\n"
    "🏠 *Адрес:* г. Новосибирск, ул. Винная, д. 1\n"
    "🕐 *Часы работы:* Ежедневно с 17:00 до 23:00\n"
    "📞 *Телефон:* +7 (999) 123-45-67\n\n"
    "Подписывайтесь на наши соцсети и вступайте в чат!"
)


@router.message(F.text == "📍 Контакты")
async def show_contacts(message: types.Message) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📱 Telegram-чат", url="https://t.me/+ExampleChat"),
            InlineKeyboardButton(text="📸 Instagram", url="https://instagram.com/example"),
        ],
        [
            InlineKeyboardButton(text="🌐 Сайт", url="https://example.com"),
        ],
    ])

    await message.answer(
        CONTACTS_TEXT,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
