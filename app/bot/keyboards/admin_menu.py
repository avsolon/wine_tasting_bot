from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from app.core.constants import ADMIN_MENU_BUTTONS
from app.database.models.tasting import Tasting
from app.database.models.wine import Wine


def get_admin_menu() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text=ADMIN_MENU_BUTTONS["manage_tastings"])],
        [KeyboardButton(text=ADMIN_MENU_BUTTONS["manage_wines"])],
        [KeyboardButton(text=ADMIN_MENU_BUTTONS["manage_gallery"])],
        [KeyboardButton(text=ADMIN_MENU_BUTTONS["manage_reviews"])],
        [KeyboardButton(text=ADMIN_MENU_BUTTONS["manage_applications"])],
        [KeyboardButton(text=ADMIN_MENU_BUTTONS["statistics"])],
        [KeyboardButton(text=ADMIN_MENU_BUTTONS["settings"])],
        [KeyboardButton(text="🚪 Выход")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_tasting_management_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать дегустацию", callback_data="admin_tasting_create")],
        [InlineKeyboardButton(text="✏️ Изменить дегустацию", callback_data="admin_tasting_edit_list")],
        [InlineKeyboardButton(text="❌ Удалить дегустацию", callback_data="admin_tasting_delete_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")],
    ])


def get_wine_management_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить вино", callback_data="admin_wine_create")],
        [InlineKeyboardButton(text="✏️ Изменить вино", callback_data="admin_wine_edit_list")],
        [InlineKeyboardButton(text="❌ Удалить вино", callback_data="admin_wine_delete_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")],
    ])


def get_gallery_management_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить фото", callback_data="admin_gallery_add")],
        [InlineKeyboardButton(text="❌ Удалить фото", callback_data="admin_gallery_delete_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")],
    ])


def get_review_management_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить отзыв", callback_data="admin_review_create")],
        [InlineKeyboardButton(text="✏️ Изменить отзыв", callback_data="admin_review_edit_list")],
        [InlineKeyboardButton(text="❌ Удалить отзыв", callback_data="admin_review_delete_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")],
    ])


def get_application_list_keyboard(applications: list, page: int = 0, page_size: int = 5) -> InlineKeyboardMarkup:
    buttons = []
    start = page * page_size
    end = start + page_size
    for app in applications[start:end]:
        buttons.append([
            InlineKeyboardButton(
                text=f"#{app.id} — {app.name}",
                callback_data=f"admin_app_view:{app.id}",
            )
        ])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"admin_app_page:{page - 1}"))
    if end < len(applications):
        nav.append(InlineKeyboardButton(text="▶️ Вперед", callback_data=f"admin_app_page:{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_tasting_list_keyboard(tastings: list[Tasting], action: str) -> InlineKeyboardMarkup:
    buttons = []
    for t in tastings:
        buttons.append([
            InlineKeyboardButton(
                text=f"{t.title} ({t.date})",
                callback_data=f"admin_tasting_{action}:{t.id}",
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_wine_list_keyboard(wines: list[Wine], action: str) -> InlineKeyboardMarkup:
    buttons = []
    for w in wines:
        buttons.append([
            InlineKeyboardButton(
                text=f"{w.name}",
                callback_data=f"admin_wine_{action}:{w.id}",
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_tasting_selection_for_wine_keyboard(tastings: list[Tasting]) -> InlineKeyboardMarkup:
    buttons = []
    for t in tastings:
        buttons.append([
            InlineKeyboardButton(
                text=f"{t.title} ({t.date})",
                callback_data=f"admin_wine_select_tasting:{t.id}",
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_tasting_selection_for_gallery_keyboard(tastings: list[Tasting]) -> InlineKeyboardMarkup:
    buttons = []
    buttons.append([InlineKeyboardButton(text="Без привязки", callback_data="admin_gallery_tasting:0")])
    for t in tastings:
        buttons.append([
            InlineKeyboardButton(
                text=f"{t.title} ({t.date})",
                callback_data=f"admin_gallery_tasting:{t.id}",
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_delete_keyboard(entity: str, entity_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm_delete:{entity}:{entity_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back"),
        ]
    ])


def get_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")],
    ])


def get_admin_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="admin_cancel")],
    ])
