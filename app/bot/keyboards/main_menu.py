from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app.core.constants import MAIN_MENU_BUTTONS


def get_main_menu() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text=MAIN_MENU_BUTTONS["tastings"])],
        [KeyboardButton(text=MAIN_MENU_BUTTONS["register"]),
         KeyboardButton(text=MAIN_MENU_BUTTONS["wines"])],
        [KeyboardButton(text=MAIN_MENU_BUTTONS["gallery"]),
         KeyboardButton(text=MAIN_MENU_BUTTONS["reviews"])],
        [KeyboardButton(text=MAIN_MENU_BUTTONS["contacts"])],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
