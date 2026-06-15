from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.database.models.tasting import Tasting


def get_tastings_keyboard(tastings: list[Tasting]) -> InlineKeyboardMarkup:
    buttons = []
    for t in tastings:
        buttons.append([
            InlineKeyboardButton(
                text=f"{t.title} ({t.date}) — {t.available_seats}/{t.total_seats} мест",
                callback_data=f"tasting_view:{t.id}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_tasting_detail_keyboard(tasting_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Записаться", callback_data=f"tasting_register:{tasting_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="tastings_back")],
    ])


def get_tasting_selection_keyboard(tastings: list[Tasting]) -> InlineKeyboardMarkup:
    buttons = []
    for t in tastings:
        buttons.append([
            InlineKeyboardButton(
                text=f"{t.title} ({t.date})",
                callback_data=f"register_select:{t.id}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_wine_tastings_keyboard(tastings: list[Tasting]) -> InlineKeyboardMarkup:
    buttons = []
    for t in tastings:
        buttons.append([
            InlineKeyboardButton(
                text=f"{t.title} ({t.date})",
                callback_data=f"wine_tasting:{t.id}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
