from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="register_confirm"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="register_cancel"),
        ]
    ])


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="register_cancel")],
    ])
