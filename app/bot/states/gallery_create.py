from aiogram.fsm.state import State, StatesGroup


class GalleryCreateStates(StatesGroup):
    select_tasting = State()
    input_photo = State()
    input_description = State()
    confirm = State()
