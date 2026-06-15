from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.bot.keyboards.main_menu import get_main_menu

router = Router()

REVIEW_URL = "https://example.com/review"
GOOGLE_REVIEWS_URL = "https://g.page/r/example/review"


@router.message(F.text == "⭐ Оставить отзыв")
async def show_review_links(message: types.Message) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти на сайт", url=REVIEW_URL)],
        [InlineKeyboardButton(text="Google Reviews", url=GOOGLE_REVIEWS_URL)],
    ])

    await message.answer(
        "⭐ Хотите оставить отзыв о нашем клубе?\n\n"
        "Вы можете сделать это по одной из ссылок ниже:",
        reply_markup=keyboard,
    )
